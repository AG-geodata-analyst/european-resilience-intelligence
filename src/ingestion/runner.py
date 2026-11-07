"""Persistence layer: RawDocument -> raw_documents, NormalizedEvent -> events.

Idempotency:
  * raw_documents  UNIQUE (source_id, payload_sha256)
  * event_sources  UNIQUE (source_id, external_event_id) WHERE NOT NULL

Re-running the same fetch is a no-op: the raw document is deduplicated on its
payload hash, and each event is deduplicated on the (source_id, external_id)
pair. This makes the runner safe for the Airflow retry/backfill model in the
roadmap (see section 6.2).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.engine import Engine

from .base import NormalizedEvent, RawDocument, SourceConnector


@dataclass
class RunReport:
    source_id: str
    raw_document_id: str
    raw_was_new: bool
    events_seen: int
    events_inserted: int


class IngestionRunner:
    def __init__(self, engine: Engine, connector: SourceConnector) -> None:
        self._engine = engine
        self._connector = connector

    def run(self, start: datetime, end: datetime) -> RunReport:
        doc = self._connector.fetch(start, end)
        events = list(self._connector.transform(doc))

        with self._engine.begin() as conn:
            raw_id, raw_new = self._persist_raw(conn, doc)
            inserted = 0
            for ev in events:
                if self._persist_event(conn, ev, raw_id):
                    inserted += 1

        return RunReport(
            source_id=self._connector.source_id,
            raw_document_id=str(raw_id),
            raw_was_new=raw_new,
            events_seen=len(events),
            events_inserted=inserted,
        )

    # ---- internals -------------------------------------------------------

    def _persist_raw(self, conn, doc: RawDocument):
        row = conn.execute(
            text("""
                INSERT INTO raw_documents
                    (raw_document_id, source_id, fetched_at, request_url,
                     request_params, http_status, content_type, payload, payload_sha256)
                VALUES
                    (:id, :sid, :fetched, :url, CAST(:params AS JSONB),
                     :status, :ctype, CAST(:payload AS JSONB), :sha)
                ON CONFLICT (source_id, payload_sha256) DO NOTHING
                RETURNING raw_document_id
            """),
            {
                "id": str(doc.raw_document_id),
                "sid": doc.source_id,
                "fetched": doc.fetched_at,
                "url": doc.request_url,
                "params": None if doc.request_params is None else json.dumps(doc.request_params),
                "status": doc.http_status,
                "ctype": doc.content_type,
                "payload": json.dumps(doc.payload),
                "sha": doc.payload_sha256,
            },
        ).first()

        if row is not None:
            return row[0], True

        # Already exists: fetch the id that was written on a prior run.
        existing = conn.execute(
            text("""
                SELECT raw_document_id FROM raw_documents
                WHERE source_id = :sid AND payload_sha256 = :sha
            """),
            {"sid": doc.source_id, "sha": doc.payload_sha256},
        ).scalar_one()
        return existing, False

    def _persist_event(self, conn, ev: NormalizedEvent, raw_id) -> bool:
        # Idempotency: skip if this (source, external_id) pair is already stored.
        already = conn.execute(
            text("""
                SELECT 1 FROM event_sources
                WHERE source_id = :sid AND external_event_id = :ext
            """),
            {"sid": self._connector.source_id, "ext": ev.external_event_id},
        ).first()
        if already:
            return False

        # Derive the country's NUTS0 region (EE00 / LV00 / LT00). NULL if missing.
        region_code = conn.execute(
            text("""
                SELECT region_code FROM regions
                WHERE country_code = :cc AND nuts_level = 0
                LIMIT 1
            """),
            {"cc": ev.country_code},
        ).scalar_one_or_none()

        event_id = conn.execute(
            text("""
                INSERT INTO events (
                    event_type, event_category, affected_sector, country_code,
                    region_code, geographic_precision, occurred_at, published_at,
                    event_status, reported_cause, verification_status
                ) VALUES (
                    :etype, :ecat, :sector, :cc,
                    :region, :precision, :occurred, :published,
                    :status, :cause, :verification
                )
                RETURNING event_id
            """),
            {
                "etype": ev.event_type,
                "ecat": ev.event_category,
                "sector": ev.affected_sector,
                "cc": ev.country_code,
                "region": region_code,
                "precision": ev.geographic_precision,
                "occurred": ev.occurred_at,
                "published": ev.published_at,
                "status": ev.event_status,
                "cause": ev.reported_cause,
                "verification": ev.verification_status,
            },
        ).scalar_one()

        conn.execute(
            text("""
                INSERT INTO event_sources
                    (event_id, source_id, source_reference,
                     raw_document_id, external_event_id)
                VALUES (:eid, :sid, :ref, :raw, :ext)
            """),
            {
                "eid": event_id,
                "sid": self._connector.source_id,
                "ref": ev.source_reference,
                "raw": raw_id,
                "ext": ev.external_event_id,
            },
        )

        if region_code is not None:
            conn.execute(
                text("""
                    INSERT INTO event_regions
                        (event_id, region_code, precision_level, is_primary)
                    VALUES (:eid, :region, :precision, TRUE)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "eid": event_id,
                    "region": region_code,
                    "precision": ev.geographic_precision,
                },
            )

        return True
