"""Gate T1 — proves the SourceConnector contract works with a fake adapter.

A fake connector is tested against the same harness the real connectors use,
so the contract itself is validated before any real source is written.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
from typing import ClassVar

import pytest

from src.ingestion.base import (
    NormalizedEvent,
    RawDocument,
    SourceConnector,
    SourceSchemaError,
)


class _FakeConnector(SourceConnector):
    source_id: ClassVar[str] = "FAKE"

    def fetch(self, start, end) -> RawDocument:
        return RawDocument(
            source_id=self.source_id,
            fetched_at=datetime.now(UTC),
            request_url="fake://x",
            http_status=200,
            payload={"ok": True},
        )

    def validate(self, doc: RawDocument) -> None:
        if doc.payload.get("ok") is not True:
            raise SourceSchemaError("fake requires ok=true")

    def transform(self, doc: RawDocument) -> Iterable[NormalizedEvent]:
        self.validate(doc)
        yield NormalizedEvent(
            external_event_id="fake-1",
            event_type="Internet outage",
            event_category="DIGITAL_INFRASTRUCTURE",
            affected_sector="digital_infrastructure",
            country_code="EE",
            geographic_precision="country",
            occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
            source_reference="fake://x",
        )


def test_fake_connector_satisfies_protocol():
    c = _FakeConnector()
    doc = c.fetch(datetime.now(UTC), datetime.now(UTC))
    events = list(c.transform(doc))
    assert len(events) == 1
    assert events[0].country_code == "EE"
    assert events[0].geographic_precision == "country"


def test_invalid_precision_rejected():
    with pytest.raises(ValueError, match="geographic_precision"):
        NormalizedEvent(
            external_event_id="x",
            event_type="t",
            event_category="c",
            affected_sector="s",
            country_code="EE",
            geographic_precision="continent",
            occurred_at=datetime.now(UTC),
            source_reference="r",
        )


def test_invalid_country_rejected():
    with pytest.raises(ValueError, match="ISO 3166-1"):
        NormalizedEvent(
            external_event_id="x",
            event_type="t",
            event_category="c",
            affected_sector="s",
            country_code="EST",
            geographic_precision="country",
            occurred_at=datetime.now(UTC),
            source_reference="r",
        )
