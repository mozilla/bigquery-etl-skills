"""
Module docstring explaining what this script does.

Example Python query template following Mozilla conventions.
"""

from argparse import ArgumentParser
from google.cloud import bigquery

parser = ArgumentParser(description=__doc__)
parser.add_argument("--project", default="moz-fx-data-shared-prod")
parser.add_argument("--destination_dataset", default="dataset_name")
parser.add_argument("--destination_table", default="table_name_v1")

def main():
    """Main function that performs the ETL operation."""
    args = parser.parse_args()

    client = bigquery.Client(args.project)

    # Your ETL logic here
    destination_table = f"{args.project}.{args.destination_dataset}.{args.destination_table}"

    job_config = bigquery.QueryJobConfig(
        destination=destination_table,
        write_disposition="WRITE_TRUNCATE"  # or WRITE_APPEND
    )

    query = """
    SELECT
      *
    FROM
      `moz-fx-data-shared-prod.telemetry.main`
    WHERE
      DATE(submission_timestamp) = @submission_date
    """

    client.query(query, job_config=job_config).result()

if __name__ == "__main__":
    main()
