#!/usr/bin/env python3
"""Parallel Search API — выдержки со страниц для RAG/агента."""
import json
import sys
from datetime import datetime, timezone

import requests

from _env import OUTPUT_DIR, require_key


def search(objective: str, queries: list[str] | None = None) -> dict:
    api_key = require_key("PARALLEL_API_KEY")
    payload = {
        "objective": objective,
        "search_queries": queries or [objective],
    }
    resp = requests.post(
        "https://api.parallel.ai/v1/search",
        headers={"Content-Type": "application/json", "x-api-key": api_key},
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    objective = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "Найти туториалы по pgvector и RAG для маленьких команд"
    )
    words = objective.split()
    queries = [objective, " ".join(words[:4])] if len(words) > 2 else [objective, f"{objective} tutorial"]
    data = search(objective, queries)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = OUTPUT_DIR / f"parallel-search-{stamp}.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    print(f"search_id: {data.get('search_id')}")
    for i, r in enumerate(data.get("results", [])[:5], 1):
        excerpt = (r.get("excerpts") or [""])[0][:200].replace("\n", " ")
        print(f"{i}. {r.get('title')}\n   {r.get('url')}\n   {excerpt}…")
    print(f"\nСохранено: {out}")


if __name__ == "__main__":
    main()
