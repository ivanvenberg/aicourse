#!/usr/bin/env python3
"""Perplexity API — ответ с citations."""
import json
import sys
from datetime import datetime, timezone

import requests

from _env import OUTPUT_DIR, require_key


def ask(question: str, model: str = "sonar") -> dict:
    api_key = require_key("PERPLEXITY_API_KEY")
    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": question}],
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "Что такое Model Context Protocol (MCP)? Дай 3 примера серверов."
    )
    data = ask(question)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = OUTPUT_DIR / f"perplexity-{stamp}.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    msg = data["choices"][0]["message"]["content"]
    citations = data.get("citations") or []
    usage = data.get("usage", {})

    print(msg)
    print("\n--- citations ---")
    for url in citations[:8]:
        print(f"- {url}")
    if usage:
        cost = usage.get("cost", {})
        print(f"\ncost: ${cost.get('total_cost', '?')} | tokens: {usage.get('total_tokens')}")
    print(f"\nСохранено: {out}")


if __name__ == "__main__":
    main()
