"""Gate T1 — Cloudflare Radar connector tests against controlled fixtures."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from src.ingestion.base import (
    RawDocument,
    SourceAuthError,
    SourceRateLimitError,
    SourceSchemaError,
)
from src.ingestion.cloudflare_radar import CloudflareRadarConnector

FIX = Path(__file__).parent.parent / "fixtures" / "cloudflare_radar"


def _doc(payload: dict, status: int = 200) -> RawDocument:
    return RawDocument(
        source_id="CLOUDFLARE_RADAR",
        fetched_at=datetime.now(UTC),
        request_url="https://api.cloudflare.com/client/v4/radar/annotations/outages",
        http_status=status,
        payload=payload,
    )


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


# ---- fetch --------------------------------------------------------------


def test_fetch_sends_bearer_token():
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        seen["url"] = str(request.url)
        return httpx.Response(200, json={"success": True, "errors": [], "result": {"annotations": []}})

    c = CloudflareRadarConnector(token="tok", client=_client(handler), retry_backoff=0.0)
    c.fetch(
        datetime(2026, 9, 1, tzinfo=UTC),
        datetime(2026, 9, 8, tzinfo=UTC),
    )

    assert seen["auth"] == "Bearer tok"
    assert "/radar/annotations/outages" in seen["url"]
    assert "dateStart" in seen["url"]
    assert "2026-09-01" in seen["url"]


def test_fetch_401_raises_auth_error():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json=json.loads((FIX / "http_401.json").read_text()))

    c = CloudflareRadarConnector(token="tok", client=_client(handler), retry_backoff=0.0)
    with pytest.raises(SourceAuthError):
        c.fetch(datetime.now(UTC), datetime.now(UTC))


def test_fetch_429_retries_then_raises():
    calls = {"n": 0}

    def handler(_: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(429, json=json.loads((FIX / "http_429.json").read_text()))

    c = CloudflareRadarConnector(token="tok", client=_client(handler), max_retries=3, retry_backoff=0.0)
    with pytest.raises(SourceRateLimitError):
        c.fetch(datetime.now(UTC), datetime.now(UTC))
    assert calls["n"] == 3


def test_fetch_malformed_json_raises_schema_error():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=(FIX / "malformed.txt").read_text())

    c = CloudflareRadarConnector(token="tok", client=_client(handler), retry_backoff=0.0)
    with pytest.raises(SourceSchemaError):
        c.fetch(datetime.now(UTC), datetime.now(UTC))


def test_missing_token_raises_auth_error(monkeypatch):
    monkeypatch.delenv("CLOUDFLARE_RADAR_API_TOKEN", raising=False)
    with pytest.raises(SourceAuthError):
        CloudflareRadarConnector()


# ---- validate / transform -----------------------------------------------


def test_valid_response_yields_one_baltic_event():
    payload = json.loads((FIX / "valid_response.json").read_text())
    c = CloudflareRadarConnector(token="tok", retry_backoff=0.0)
    events = list(c.transform(_doc(payload)))

    assert len(events) == 1
    ev = events[0]
    assert ev.country_code == "EE"
    assert ev.geographic_precision == "country"
    assert ev.event_type == "Internet outage"
    assert ev.event_category == "DIGITAL_INFRASTRUCTURE"
    assert ev.reported_cause == "POWER_OUTAGE"
    assert ev.event_status == "ended"


def test_country_filter_drops_non_baltic():
    payload = json.loads((FIX / "valid_response.json").read_text())
    c = CloudflareRadarConnector(token="tok", retry_backoff=0.0)
    assert {e.country_code for e in c.transform(_doc(payload))} == {"EE"}


def test_non_outage_event_is_skipped():
    payload = json.loads((FIX / "non_outage_event.json").read_text())
    c = CloudflareRadarConnector(token="tok", retry_backoff=0.0)
    assert list(c.transform(_doc(payload))) == []


def test_empty_annotations_yields_zero_events():
    payload = json.loads((FIX / "empty_annotations.json").read_text())
    c = CloudflareRadarConnector(token="tok", retry_backoff=0.0)
    assert list(c.transform(_doc(payload))) == []


def test_ongoing_outage_has_null_end():
    payload = json.loads((FIX / "ongoing_outage.json").read_text())
    c = CloudflareRadarConnector(token="tok", retry_backoff=0.0)
    (ev,) = list(c.transform(_doc(payload)))
    assert ev.event_status == "ongoing"
    assert ev.published_at is None


def test_schema_drift_raises():
    payload = json.loads((FIX / "schema_drift.json").read_text())
    c = CloudflareRadarConnector(token="tok", retry_backoff=0.0)
    with pytest.raises(SourceSchemaError, match="schema drift"):
        list(c.transform(_doc(payload)))


def test_not_success_raises():
    payload = json.loads((FIX / "not_success.json").read_text())
    c = CloudflareRadarConnector(token="tok", retry_backoff=0.0)
    with pytest.raises(SourceSchemaError, match="success"):
        list(c.transform(_doc(payload)))


# ---- idempotency primitive ----------------------------------------------


def test_payload_hash_is_stable_and_key_order_independent():
    a = _doc({"success": True, "errors": [], "result": {"annotations": []}})
    b = _doc({"result": {"annotations": []}, "errors": [], "success": True})
    assert a.payload_sha256 == b.payload_sha256


def test_payload_hash_differs_on_content_change():
    a = _doc({"success": True, "errors": [], "result": {"annotations": []}})
    b = _doc({"success": True, "errors": [], "result": {"annotations": [{"id": "1"}]}})
    assert a.payload_sha256 != b.payload_sha256
