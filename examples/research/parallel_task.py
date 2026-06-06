#!/usr/bin/env python3
"""Parallel Task API — структурированный ресёрч с citations."""
import json
import sys
import time
from datetime import datetime, timezone

import requests

from _env import OUTPUT_DIR, require_key

BASE = "https://api.parallel.ai/v1/tasks/runs"


def create_task(subject: str, processor: str = "lite") -> str:
    api_key = require_key("PARALLEL_API_KEY")
    payload = {
        "input": subject,
        "processor": processor,
        "task_spec": {
            "output_schema": {
                "type": "json",
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "key_facts": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["summary", "key_facts"],
                },
            }
        },
    }
    resp = requests.post(
        BASE,
        headers={"Content-Type": "application/json", "x-api-key": api_key},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["run_id"]


def poll_result(run_id: str, timeout_sec: int = 300) -> dict:
    api_key = require_key("PARALLEL_API_KEY")
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        resp = requests.get(
            f"{BASE}/{run_id}/result",
            headers={"x-api-key": api_key},
            timeout=60,
        )
        if resp.status_code == 404:
            time.sleep(3)
            continue
        resp.raise_for_status()
        data = resp.json()
        status = data.get("run", {}).get("status")
        if status == "completed":
            return data
        if status == "failed":
            raise RuntimeError(data)
        print(f"status: {status}…")
        time.sleep(5)
    raise TimeoutError(f"Task {run_id} не завершился за {timeout_sec}s")


def main():
    subject = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Claude Code"
    run_id = create_task(subject)
    print(f"run_id: {run_id}")
    data = poll_result(run_id)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = OUTPUT_DIR / f"parallel-task-{stamp}.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    output = data.get("output", {})
    print(json.dumps(output.get("content"), indent=2, ensure_ascii=False))
    basis = output.get("basis") or []
    if basis:
        print(f"\nconfidence: {basis[0].get('confidence')}")
        for c in (basis[0].get("citations") or [])[:3]:
            print(f"- {c.get('title')}: {c.get('url')}")
    print(f"\nСохранено: {out}")


if __name__ == "__main__":
    main()
