INSERT INTO source_registry (
    source_id, name, url, source_type, license, access_method,
    update_frequency, geographic_precision, limitations
) VALUES (
    'CLOUDFLARE_RADAR',
    'Cloudflare Radar — Internet outages and anomalies',
    'https://developers.cloudflare.com/radar/investigate/outages/',
    'api',
    'Cloudflare Radar API terms — verify before redistributing derived data',
    'REST GET, Authorization: Bearer <token>',
    'continuous — poll every 30-60 min',
    'country',
    'An Internet outage is not by itself a cyberattack. Preserve the reported cause; never infer one. scope is free text and is never mapped to NUTS.'
)
ON CONFLICT (source_id) DO NOTHING;

INSERT INTO source_registry (
    source_id, name, url, source_type, license, access_method,
    update_frequency, geographic_precision, limitations
) VALUES (
    'CERT_EE',
    'CERT-EU / RIA Cyber Advisories',
    'https://cert.europa.eu/',
    'api',
    'Public domain',
    'RSS/XML',
    'daily',
    'country',
    'National and EU-level cyber advisories.'
)
ON CONFLICT (source_id) DO NOTHING;
