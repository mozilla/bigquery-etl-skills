# Privacy & Data Handling

## Key Principles from Mozilla's Data Platform

- **Geo IP lookup**: IP addresses are discarded after geo-city metadata extraction
- **User agent parsing**: Raw user agent strings are discarded after feature extraction
- **Deduplication**: Best-effort deduplication in Pub/Sub, full deduplication per UTC day in BigQuery
- **Deletion requests**: Support for user deletion requests via `deletion-request` pings
- **Sample ID**: Use `sample_id` field (0-99) for sampling, enables 1% samples when `sample_id = 0`

## Best Practices

- Don't include PII (personally identifiable information) in derived tables
- Use client-level identifiers (`client_id`) not individual-level identifiers
- Respect data retention policies (typically ~2 years for client-level data)
- Label client-level tables with `table_type: client_level` in metadata.yaml
- Redact or aggregate data that could identify individuals
- Follow structured ingestion for automatic geo/user-agent anonymization

## For Detailed Privacy Guidelines

- See: https://docs.telemetry.mozilla.org/tools/guiding_principles.html
- Contact: Data Platform team for privacy review questions
