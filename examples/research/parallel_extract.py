#!/usr/bin/env python3
"""Parallel Extract API — чистый текст со страницы по URL."""
import json
import sys
from datetime import datetime, timezone

import requests

from _env import OUTPUT_DIR, require_key


def extract(url: str, objective: str | None = None) -> dict:
    api_key = require_key("PARALLEL_API_KEY")
    payload = {"urls": [url]}
    if objective:
        payload["objective"] = objective
    resp = requests.post(
        "https://api.parallel.ai/v1beta/extract",
        headers={"Content-Type": "application/json", "x-api-key": api_key},
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else (
        "https://docs.parallel.ai/getting-started/overview"
    )
    objective = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    data = extract(url, objective)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = OUTPUT_DIR / f"parallel-extract-{stamp}.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    print(f"extract_id: {data.get('extract_id')}")
    for r in data.get("results", []):
        excerpt = (r.get("excerpts") or [""])[0][:500]
        print(f"\n{r.get('title')}\n{r.get('url')}\n{excerpt}…")
    print(f"\nСохранено: {out}")


if __name__ == "__main__":
    main()
