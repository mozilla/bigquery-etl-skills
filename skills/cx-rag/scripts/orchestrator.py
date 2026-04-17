#!/usr/bin/env python3
"""
Retrieval backend for the cx-rag Claude skill.

Queries three Mozilla CX data sources via VECTOR_SEARCH (semantic similarity):
  - kitsune_retrieval_index
  - zendesk_retrieval_index
  - knowledge_base_retrieval_index

Uses only Python stdlib + gcloud CLI — no pip installs needed.

Prerequisites:
    Google Cloud SDK (gcloud CLI)
    gcloud config set project <your-project-id>
    gcloud auth application-default login

Usage:
    python scripts/orchestrator.py --question "What are users saying about Firefox sync?"
    python scripts/orchestrator.py --question "..." --date-from 2026-03-01 --date-to 2026-03-31
    python scripts/orchestrator.py --question "..." --product "Firefox for Android" --locale en-US
    python scripts/orchestrator.py --inspect
"""

import json
import re
import sys
import argparse
import subprocess
import urllib.request
import urllib.error
import concurrent.futures

PROJECT  = None
LOCATION = "us-central1"
DATASET  = "customer_experience_derived"
EMBEDDING_MODEL = "gemini-embedding-001"
TOP_K = 5

KITSUNE_TABLE = ""
ZENDESK_TABLE = ""
KB_TABLE      = ""

KITSUNE_COLS = ["title", "content", "answer_content", "summary_generated",
                "category_generated", "sentiment_score", "recency_score", "product", "topic"]
ZENDESK_COLS = ["title", "content", "summary_generated", "category_generated",
                "sentiment_score", "product", "star_rating", "recency_score"]
KB_COLS      = ["title", "summary_generated", "category_generated", "slug", "product"]


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_auth() -> tuple[str, str]:
    """Returns (access_token, project_id) from application-default credentials."""
    try:
        token_result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, check=True,
        )
        token = token_result.stdout.strip()
    except subprocess.CalledProcessError:
        print(
            "GCP authentication required.\n"
            "Follow the authentication instructions provided by DE, then try again.\n"
            "  gcloud auth application-default login",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        project_result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True, text=True, check=True,
        )
        project = project_result.stdout.strip()
        if not project or project == "(unset)":
            print(
                "No GCP project configured.\n"
                "Follow the instructions provided by DE to set the project name, then try again.\n"
                "  gcloud config set project <project-name-from-DE>",
                file=sys.stderr,
            )
            sys.exit(1)
    except subprocess.CalledProcessError:
        print(
            "Could not read GCP project.\n"
            "Follow the instructions provided by DE to set the project name, then try again.\n"
            "  gcloud config set project <project-name-from-DE>",
            file=sys.stderr,
        )
        sys.exit(1)

    return token, project


# ── HTTP / BigQuery helpers ───────────────────────────────────────────────────

def _request(url: str, token: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(
                "Authentication rejected (401).\n"
                "Follow the authentication instructions provided by DE and re-run:\n"
                "  gcloud auth application-default login",
                file=sys.stderr,
            )
            sys.exit(1)
        try:
            msg = json.loads(e.read().decode()).get("error", {}).get("message", f"HTTP {e.code}")
        except Exception:
            msg = f"HTTP {e.code}"
        print(f"API error: {msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def _bq_query(sql: str, token: str) -> list[dict]:
    url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT}/queries"
    resp = _request(url, token, {"query": sql, "useLegacySql": False, "timeoutMs": 30000})
    while not resp.get("jobComplete"):
        job_id = resp["jobReference"]["jobId"]
        resp = _request(
            f"https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT}"
            f"/queries/{job_id}?timeoutMs=30000",
            token,
        )
    fields = resp.get("schema", {}).get("fields", [])
    rows   = resp.get("rows", [])
    col_names = [f["name"] for f in fields]
    return [dict(zip(col_names, (cell.get("v") for cell in row["f"]))) for row in rows]


# ── Embedding ─────────────────────────────────────────────────────────────────

def embed_text(text: str, token: str) -> list[float]:
    url = (
        f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}"
        f"/locations/{LOCATION}/publishers/google/models/{EMBEDDING_MODEL}:predict"
    )
    try:
        resp = _request(url, token, {
            "instances": [{"content": text, "task_type": "RETRIEVAL_QUERY"}]
        })
        return resp["predictions"][0]["embeddings"]["values"]
    except (KeyError, IndexError):
        print("Unexpected response from Vertex AI embedding API.", file=sys.stderr)
        sys.exit(1)


# ── Filter helpers ────────────────────────────────────────────────────────────

def _sanitize(value: str) -> str:
    """Strip characters that could break SQL string literals."""
    return re.sub(r"['\";\\]", "", value)


def _kitsune_conditions(date_from: str | None, date_to: str | None,
                         product: str | None, locale: str | None) -> list[str]:
    conds = []
    if date_from:
        conds.append(f"base.creation_date >= '{date_from}'")
    if date_to:
        conds.append(f"base.creation_date <= '{date_to}'")
    if product:
        conds.append(f"LOWER(base.product) LIKE LOWER('%{_sanitize(product)}%')")
    if locale:
        conds.append(f"LOWER(base.locale) LIKE LOWER('%{_sanitize(locale)}%')")
    return conds


def _zendesk_conditions(date_from: str | None, date_to: str | None,
                         product: str | None, locale: str | None) -> list[str]:
    conds = []
    if date_from:
        conds.append(f"DATE(base.creation_date) >= '{date_from}'")
    if date_to:
        conds.append(f"DATE(base.creation_date) <= '{date_to}'")
    if product:
        conds.append(f"LOWER(base.product) LIKE LOWER('%{_sanitize(product)}%')")
    if locale:
        conds.append(f"LOWER(base.locale) LIKE LOWER('%{_sanitize(locale)}%')")
    return conds


def _kb_conditions(product: str | None, locale: str | None) -> list[str]:
    conds = []
    if product:
        conds.append(f"LOWER(base.product) LIKE LOWER('%{_sanitize(product)}%')")
    if locale:
        conds.append(f"LOWER(base.locale) LIKE LOWER('%{_sanitize(locale)}%')")
    return conds


# ── Search functions ──────────────────────────────────────────────────────────

def search_kitsune(embedding: list[float], token: str, top_k: int,
                   date_from: str | None = None, date_to: str | None = None,
                   product: str | None = None, locale: str | None = None) -> list[dict]:
    literal = "[" + ",".join(str(v) for v in embedding) + "]"
    cols = ", ".join(f"base.{c}" for c in KITSUNE_COLS)
    conds = _kitsune_conditions(date_from, date_to, product, locale)
    where_clause = f"WHERE {' AND '.join(conds)}" if conds else ""
    sql = f"""
    SELECT {cols}, distance, 'kitsune' AS _source
    FROM VECTOR_SEARCH(
        TABLE `{KITSUNE_TABLE}`, 'embedding',
        (SELECT {literal} AS embedding),
        top_k => {top_k}, distance_type => 'COSINE'
    )
    {where_clause}
    ORDER BY distance ASC
    """
    return _bq_query(sql, token)


def search_zendesk(embedding: list[float], token: str, top_k: int,
                   date_from: str | None = None, date_to: str | None = None,
                   product: str | None = None, locale: str | None = None) -> list[dict]:
    literal = "[" + ",".join(str(v) for v in embedding) + "]"
    cols = ", ".join(f"base.{c}" for c in ZENDESK_COLS)
    conds = _zendesk_conditions(date_from, date_to, product, locale)
    where_clause = f"WHERE {' AND '.join(conds)}" if conds else ""
    sql = f"""
    SELECT {cols}, distance, 'zendesk' AS _source
    FROM VECTOR_SEARCH(
        TABLE `{ZENDESK_TABLE}`, 'embedding',
        (SELECT {literal} AS embedding),
        top_k => {top_k}, distance_type => 'COSINE'
    )
    {where_clause}
    ORDER BY distance ASC
    """
    return _bq_query(sql, token)


def search_kb(embedding: list[float], token: str, top_k: int,
              product: str | None = None, locale: str | None = None) -> list[dict]:
    literal = "[" + ",".join(str(v) for v in embedding) + "]"
    cols = ", ".join(f"base.{c}" for c in KB_COLS)
    conds = _kb_conditions(product, locale)
    where_clause = f"WHERE {' AND '.join(conds)}" if conds else ""
    sql = f"""
    SELECT {cols}, distance, 'knowledge_base' AS _source
    FROM VECTOR_SEARCH(
        TABLE `{KB_TABLE}`, 'embedding',
        (SELECT {literal} AS embedding),
        top_k => {top_k}, distance_type => 'COSINE'
    )
    {where_clause}
    ORDER BY distance ASC
    """
    return _bq_query(sql, token)


# ── Output ────────────────────────────────────────────────────────────────────

def build_context(
    kitsune_rows: list[dict],
    zendesk_rows: list[dict],
    kb_rows: list[dict],
) -> str:
    def format_section(rows: list[dict], label: str) -> str:
        if not rows:
            return f"=== {label} ===\nNo results found.\n"
        parts = [f"=== {label} ({len(rows)} results) ==="]
        for i, row in enumerate(rows, 1):
            lines = [
                f"{k}: {v}" for k, v in row.items()
                if not k.startswith("_") and v
            ]
            if lines:
                parts.append(f"[{i}]\n" + "\n".join(lines))
        return "\n".join(parts)

    return "\n\n".join([
        format_section(kitsune_rows, "SUMO / Kitsune"),
        format_section(zendesk_rows, "Zendesk"),
        format_section(kb_rows, "Knowledge Base"),
    ])


# ── Inspect ───────────────────────────────────────────────────────────────────

def inspect_all(token: str) -> None:
    tables = [
        "kitsune_retrieval_index",
        "zendesk_retrieval_index",
        "knowledge_base_retrieval_index",
    ]
    for table in tables:
        url = (f"https://bigquery.googleapis.com/bigquery/v2/projects/{PROJECT}"
               f"/datasets/{DATASET}/tables/{table}")
        resp = _request(url, token)
        fields = resp.get("schema", {}).get("fields", [])
        print(f"\nSchema for {PROJECT}.{DATASET}.{table}:\n")
        for f in fields:
            print(f"  {f['name']:<45} {f['type']:<12} {f.get('mode', 'NULLABLE')}")


# ── Entry point ───────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Retrieve CX context from Mozilla data sources.")
    parser.add_argument("--question", required=False, help="Question to search for.")
    parser.add_argument("--top-k", type=int, default=TOP_K,
                        help=f"Results per source (default {TOP_K}).")
    parser.add_argument("--inspect", action="store_true",
                        help="Print all table schemas and exit.")
    parser.add_argument("--date-from", metavar="YYYY-MM-DD",
                        help="Include only records on or after this date.")
    parser.add_argument("--date-to", metavar="YYYY-MM-DD",
                        help="Include only records on or before this date.")
    parser.add_argument("--product",
                        help="Filter by product name, partial match (e.g. 'Firefox for Android', 'Fenix').")
    parser.add_argument("--locale",
                        help="Filter by locale/language code, partial match (e.g. 'en-US', 'es', 'fr').")
    return parser.parse_args()


def main() -> None:
    global PROJECT, KITSUNE_TABLE, ZENDESK_TABLE, KB_TABLE
    args = parse_args()
    token, PROJECT = get_auth()
    KITSUNE_TABLE = f"{PROJECT}.{DATASET}.kitsune_retrieval_index"
    ZENDESK_TABLE = f"{PROJECT}.{DATASET}.zendesk_retrieval_index"
    KB_TABLE      = f"{PROJECT}.{DATASET}.knowledge_base_retrieval_index"

    if args.inspect:
        inspect_all(token)
        return

    if not args.question:
        print("Error: --question is required.", file=sys.stderr)
        sys.exit(1)

    active_filters = {k: v for k, v in [
        ("date_from", args.date_from), ("date_to", args.date_to),
        ("product", args.product), ("locale", args.locale),
    ] if v}
    if active_filters:
        print(f"  Filters active: {active_filters}", file=sys.stderr)

    print(f"Embedding question with {EMBEDDING_MODEL}...", file=sys.stderr, flush=True)
    embedding = embed_text(args.question, token)
    print(f"  {len(embedding)}-dimensional vector created.", file=sys.stderr)

    print("Searching all sources...", file=sys.stderr, flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f_kitsune = executor.submit(search_kitsune, embedding, token, args.top_k,
                                    args.date_from, args.date_to, args.product, args.locale)
        f_zendesk = executor.submit(search_zendesk, embedding, token, args.top_k,
                                    args.date_from, args.date_to, args.product, args.locale)
        f_kb      = executor.submit(search_kb, embedding, token, args.top_k, args.product, args.locale)
        kitsune_rows = f_kitsune.result()
        zendesk_rows = f_zendesk.result()
        kb_rows      = f_kb.result()

    print(
        f"  Retrieved: {len(kitsune_rows)} kitsune, "
        f"{len(zendesk_rows)} zendesk, {len(kb_rows)} knowledge base.",
        file=sys.stderr,
    )
    print(build_context(kitsune_rows, zendesk_rows, kb_rows))


if __name__ == "__main__":
    main()
