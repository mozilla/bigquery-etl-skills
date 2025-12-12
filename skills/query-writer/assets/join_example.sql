-- Standard JOIN pattern with partition and clustering fields
SELECT
  events.*,
  clients.country,
  clients.channel,
  clients.os
FROM
  `moz-fx-data-shared-prod.telemetry.events` AS events
LEFT JOIN
  `moz-fx-data-shared-prod.telemetry.clients_daily` AS clients
  ON events.client_id = clients.client_id
  AND events.submission_date = clients.submission_date
WHERE
  events.submission_date = @submission_date
