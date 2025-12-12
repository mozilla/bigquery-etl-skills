-- UNNEST pattern for repeated fields
SELECT
  submission_date,
  client_id,
  event.timestamp AS event_timestamp,
  event.category AS event_category,
  event.method AS event_method,
FROM
  `moz-fx-data-shared-prod.telemetry.event`
CROSS JOIN
  UNNEST(payload.events.parent) AS event
WHERE
  submission_date = @submission_date
