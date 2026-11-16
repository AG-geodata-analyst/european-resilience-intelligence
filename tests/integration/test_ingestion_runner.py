import os
from datetime import UTC, datetime

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from src.ingestion.base import RawDocument
from src.ingestion.cert_eu import CertEuConnector
from src.ingestion.runner import IngestionRunner

load_dotenv(".env")


@pytest.mark.integration
def test_ingestion_runner_inserts_to_db():
    engine = create_engine(
        f"postgresql+psycopg://{os.getenv('POSTGRES_USER', 'bri')}:{os.getenv('POSTGRES_PASSWORD', 'change_me')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'bri')}"
    )

    with engine.begin() as conn:
        conn.execute(
            text("""
            INSERT INTO source_registry (source_id, name, url, source_type) 
            VALUES ('CERT_EU', 'CERT-EU Test', 'http://test', 'api')
            ON CONFLICT DO NOTHING;
        """)
        )

    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel><item>
    <title>Integration Test Advisory</title>
    <link>https://test.local/advisory-999</link>
    <pubDate>Mon, 06 Nov 2026 10:00:00 GMT</pubDate>
    <guid>integration-test-999</guid>
    </item></channel></rss>"""

    doc = RawDocument(
        source_id="CERT_EU",
        fetched_at=datetime.now(UTC),
        request_url="http://test",
        http_status=200,
        payload={"raw_xml": xml_text},
    )

    connector = CertEuConnector()
    runner = IngestionRunner(engine, connector)

    with engine.begin() as conn:
        raw_id, raw_new = runner._persist_raw(conn, doc)
        events = list(connector.transform(doc))
        for ev in events:
            runner._persist_event(conn, ev, raw_id)

    with engine.connect() as conn:
        count = conn.execute(text("SELECT count(*) FROM events WHERE event_type='Integration Test Advisory'")).scalar()
        assert count == 1

    with engine.begin() as conn:
        delete_regions = (
            "DELETE FROM event_regions WHERE event_id IN "
            "(SELECT event_id FROM events WHERE event_type='Integration Test Advisory')"
        )
        conn.execute(text(delete_regions))
        conn.execute(text("DELETE FROM event_sources WHERE external_event_id='integration-test-999'"))
        conn.execute(text("DELETE FROM events WHERE event_type='Integration Test Advisory'"))
        conn.execute(text("DELETE FROM raw_documents WHERE payload_sha256=:sha"), {"sha": doc.payload_sha256})
