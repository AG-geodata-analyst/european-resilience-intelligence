"""Common ingestion contract (Work Package 4, gate T1).

A connector is deliberately narrow so it can be unit-tested with fixtures and
no database:

    fetch()     -> RawDocument       (HTTP only, no business logic)
    validate()  -> None | raise      (structural schema check)
    transform() -> [NormalizedEvent] (pure mapping, no I/O)

Persistence lives in runner.py so the connector stays pure.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from typing import Any, ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

GEOGRAPHIC_PRECISIONS = frozenset({"country", "nuts1", "nuts2", "nuts3", "municipality", "unknown"})


class SourceError(RuntimeError):
    """Base class for connector failures."""


class SourceAuthError(SourceError):
    """401/403 from the source — credentials missing, wrong, or revoked."""


class SourceRateLimitError(SourceError):
    """429 from the source, after retries are exhausted."""


class SourceSchemaError(SourceError):
    """Response did not match the expected schema (source drift)."""


class RawDocument(BaseModel):
    """Immutable snapshot of a source response. Written once, never updated."""

    model_config = ConfigDict(frozen=True)

    raw_document_id: UUID = Field(default_factory=uuid4)
    source_id: str
    fetched_at: datetime
    request_url: str
    request_params: dict[str, Any] | None = None
    http_status: int
    content_type: str | None = None
    payload: dict[str, Any]

    @property
    def payload_sha256(self) -> str:
        """Canonical hash for idempotent re-ingestion (UNIQUE per source)."""
        canonical = json.dumps(self.payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class NormalizedEvent(BaseModel):
    """A candidate event, ready for persistence. Not yet persisted."""

    model_config = ConfigDict(frozen=True)

    external_event_id: str
    event_type: str
    event_category: str
    affected_sector: str
    country_code: str
    geographic_precision: str
    occurred_at: datetime
    published_at: datetime | None = None
    event_status: str = "reported"
    reported_cause: str | None = None
    verification_status: str = "reported"
    source_reference: str

    @field_validator("geographic_precision")
    @classmethod
    def _precision_allowed(cls, v: str) -> str:
        if v not in GEOGRAPHIC_PRECISIONS:
            raise ValueError(f"geographic_precision must be one of {sorted(GEOGRAPHIC_PRECISIONS)}")
        return v

    @field_validator("country_code")
    @classmethod
    def _country_iso2(cls, v: str) -> str:
        if len(v) != 2 or not v.isalpha() or not v.isupper():
            raise ValueError(f"country_code must be ISO 3166-1 alpha-2, got {v!r}")
        return v


class SourceConnector(ABC):
    """Every source adapter implements this contract."""

    source_id: ClassVar[str]

    @abstractmethod
    def fetch(self, start: datetime, end: datetime) -> RawDocument:
        """Perform the HTTP request. Raise a SourceError subclass on failure."""

    @abstractmethod
    def validate(self, doc: RawDocument) -> None:
        """Raise SourceSchemaError if the payload is structurally wrong."""

    @abstractmethod
    def transform(self, doc: RawDocument) -> Iterable[NormalizedEvent]:
        """Map RawDocument to zero or more NormalizedEvent. Must not do I/O."""
