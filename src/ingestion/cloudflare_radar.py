"""Cloudflare Radar — Internet outage annotations.

Endpoint and schema verified against:
  https://developers.cloudflare.com/radar/investigate/outages/
  https://developers.cloudflare.com/api/resources/radar/subresources/annotations/subresources/outages/methods/get/

Design rules enforced here (see docs/METHODOLOGY.md):
  * eventType != "OUTAGE" is skipped — traffic anomalies are not outages.
  * outage.outageCause is preserved verbatim as reported_cause; never inferred.
  * scope is free text; events stay at geographic_precision="country".
  * One NormalizedEvent per affected Baltic country, because
    events.country_code is a single CHAR(2).
"""

from __future__ import annotations

import os
import time
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import ClassVar

import httpx

from .base import (
    NormalizedEvent,
    RawDocument,
    SourceAuthError,
    SourceConnector,
    SourceRateLimitError,
    SourceSchemaError,
)

API_URL = "https://api.cloudflare.com/client/v4/radar/annotations/outages"
BALTIC = ("EE", "LV", "LT")


class CloudflareRadarConnector(SourceConnector):
    source_id: ClassVar[str] = "CLOUDFLARE_RADAR"

    def __init__(
        self,
        token: str | None = None,
        client: httpx.Client | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
    ) -> None:
        self._token = token or os.environ.get("CLOUDFLARE_RADAR_API_TOKEN")
        if not self._token:
            raise SourceAuthError(
                "CLOUDFLARE_RADAR_API_TOKEN is not set. Create a Custom Token with Account > Radar > Read."
            )
        self._client = client or httpx.Client(timeout=timeout)
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff

    # ---- fetch -----------------------------------------------------------

    def fetch(self, start: datetime, end: datetime) -> RawDocument:
        params = {
            "dateStart": _iso_z(start),
            "dateEnd": _iso_z(end),
            "format": "json",
            "limit": 200,
        }
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }

        last_exc: Exception | None = None
        resp: httpx.Response | None = None
        for attempt in range(self._max_retries):
            resp = self._client.get(API_URL, params=params, headers=headers)
            if resp.status_code in (401, 403):
                raise SourceAuthError(f"Cloudflare Radar auth failed: HTTP {resp.status_code}")
            if resp.status_code == 429:
                last_exc = SourceRateLimitError("Cloudflare Radar rate limited (429)")
                time.sleep(self._retry_backoff * (2**attempt))
                continue
            if resp.status_code >= 500:
                last_exc = SourceSchemaError(f"Cloudflare Radar server error: HTTP {resp.status_code}")
                time.sleep(self._retry_backoff * (2**attempt))
                continue
            resp.raise_for_status()
            break
        else:
            raise last_exc or SourceSchemaError("Cloudflare Radar fetch failed after retries")

        assert resp is not None
        try:
            body = resp.json()
        except ValueError as exc:
            raise SourceSchemaError(f"Cloudflare Radar returned non-JSON: {exc}") from exc

        return RawDocument(
            source_id=self.source_id,
            fetched_at=datetime.now(UTC),
            request_url=str(resp.request.url),
            request_params=params,
            http_status=resp.status_code,
            content_type=resp.headers.get("content-type"),
            payload=body,
        )

    # ---- validate --------------------------------------------------------

    def validate(self, doc: RawDocument) -> None:
        if not isinstance(doc.payload, dict):
            raise SourceSchemaError("payload is not a JSON object")
        if doc.payload.get("success") is not True:
            raise SourceSchemaError(f"payload.success is not true: {doc.payload.get('success')!r}")
        result = doc.payload.get("result")
        if not isinstance(result, dict):
            raise SourceSchemaError("payload.result missing or not an object")
        annotations = result.get("annotations")
        if not isinstance(annotations, list):
            raise SourceSchemaError("payload.result.annotations missing or not a list")
        for i, ann in enumerate(annotations):
            if not isinstance(ann, dict):
                raise SourceSchemaError(f"annotations[{i}] is not an object")
            for key in ("eventType", "startDate", "locations"):
                if key not in ann:
                    raise SourceSchemaError(f"annotations[{i}] missing required field {key!r} — schema drift")

    # ---- transform -------------------------------------------------------

    def transform(self, doc: RawDocument) -> Iterable[NormalizedEvent]:
        self.validate(doc)
        for ann in doc.payload["result"]["annotations"]:
            if ann.get("eventType") != "OUTAGE":
                continue  # TRAFFIC_ANOMALY, GENERAL, EVENT, ... are not outages
            if not ann.get("locations"):
                continue

            outage = ann.get("outage") or {}
            cause = outage.get("outageCause")
            occurred_at = _parse_dt(ann["startDate"])
            external_id = str(ann.get("id") or doc.payload_sha256[:16])
            status = "ongoing" if ann.get("endDate") is None else "ended"

            for country in ann["locations"]:
                if country not in BALTIC:
                    continue
                yield NormalizedEvent(
                    external_event_id=f"{external_id}:{country}",
                    event_type="Internet outage",
                    event_category="DIGITAL_INFRASTRUCTURE",
                    affected_sector="digital_infrastructure",
                    country_code=country,
                    geographic_precision="country",
                    occurred_at=occurred_at,
                    published_at=None,  # Radar exposes no distinct publication time
                    event_status=status,
                    reported_cause=cause,
                    verification_status="reported",
                    source_reference=str(ann.get("linkedUrl") or doc.request_url),
                )


def _iso_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_dt(s: str) -> datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)
