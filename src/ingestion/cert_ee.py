import xml.etree.ElementTree as ET
from collections.abc import Iterable
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import ClassVar

import httpx

from .base import (
    NormalizedEvent,
    RawDocument,
    SourceConnector,
    SourceSchemaError,
)

# Example public RSS feed for national cyber alerts (Estonia)
RSS_URL = "https://www.ria.ee/en/rss.xml"


class CertEeConnector(SourceConnector):
    source_id: ClassVar[str] = "CERT_EE"

    def __init__(self, client: httpx.Client | None = None, timeout: float = 30.0) -> None:
        self._client = client or httpx.Client(timeout=timeout)

    def fetch(self, start: datetime, end: datetime) -> RawDocument:
        headers = {"User-Agent": "EuropeanResilienceIntelligence/0.1"}
        resp = self._client.get(RSS_URL, headers=headers)
        resp.raise_for_status()

        # Store the raw XML text in the payload dict
        return RawDocument(
            source_id=self.source_id,
            fetched_at=datetime.now(UTC),
            request_url=str(resp.request.url),
            http_status=resp.status_code,
            content_type=resp.headers.get("content-type"),
            payload={"raw_xml": resp.text},
        )

    def validate(self, doc: RawDocument) -> None:
        xml_str = doc.payload.get("raw_xml", "")
        if not xml_str:
            raise SourceSchemaError("payload missing raw_xml")
        try:
            ET.fromstring(xml_str)
        except ET.ParseError as exc:
            raise SourceSchemaError(f"Invalid XML: {exc}") from exc

    def transform(self, doc: RawDocument) -> Iterable[NormalizedEvent]:
        self.validate(doc)
        xml_str = doc.payload["raw_xml"]
        root = ET.fromstring(xml_str)

        # Standard RSS structure: <rss><channel><item>...
        for item in root.findall(".//item"):
            title = item.findtext("title", default="Unknown advisory")
            link = item.findtext("link", default=RSS_URL)
            pub_date_str = item.findtext("pubDate")
            guid = item.findtext("guid", default=link)

            # Parse RFC 822 date string from RSS (e.g., "Wed, 02 Oct 2002 13:00:00 GMT")
            occurred_at = datetime.now(UTC)
            if pub_date_str:
                try:
                    occurred_at = parsedate_to_datetime(pub_date_str)
                except ValueError:
                    pass

            yield NormalizedEvent(
                external_event_id=guid,
                event_type=title[:100],  # Truncate to fit DB constraint
                event_category="CYBER",
                affected_sector="cyber",
                country_code="EE",
                geographic_precision="country",
                occurred_at=occurred_at,
                published_at=occurred_at,
                event_status="reported",
                reported_cause="CERT-EE Advisory",
                verification_status="verified",  # Government source
                source_reference=link,
            )
