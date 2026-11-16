from datetime import UTC, datetime
from pathlib import Path

import pytest
from src.ingestion.cert_eu import CertEuConnector

from src.ingestion.base import RawDocument, SourceSchemaError

FIX = Path(__file__).parent.parent / "fixtures" / "cert_eu"


def _doc(payload: dict) -> RawDocument:
    return RawDocument(
        source_id="CERT_EU",
        fetched_at=datetime.now(UTC),
        request_url="https://cert.europa.eu/publications/security-advisories-rss",
        http_status=200,
        payload=payload,
    )


def test_valid_rss_yields_events():
    xml_text = (FIX / "valid_feed.xml").read_text()
    c = CertEuConnector()
    events = list(c.transform(_doc({"raw_xml": xml_text})))

    assert len(events) == 1
    ev = events[0]
    assert ev.country_code == "EE"
    assert ev.event_category == "CYBER"
    assert ev.verification_status == "verified"
    assert ev.external_event_id == "advisory-123"
    assert ev.event_type == "Critical vulnerability in widely used router"

    # Check RFC822 date parsing
    assert ev.occurred_at.year == 2026
    assert ev.occurred_at.month == 11
    assert ev.occurred_at.day == 6


def test_invalid_xml_raises_schema_error():
    c = CertEuConnector()
    with pytest.raises(SourceSchemaError, match="Invalid XML"):
        list(c.transform(_doc({"raw_xml": "<rss><channel>"})))
