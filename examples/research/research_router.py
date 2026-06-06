#!/usr/bin/env python3
"""
Простой роутер: свежие факты → Perplexity, выдержки для RAG → Parallel Search.
Результат в output/research-bundle-*.md
"""
import json
import sys
from datetime import datetime, timezone

from _env import OUTPUT_DIR
from ask_perplexity import ask
from parallel_search import search


def bundle(question: str) -> str:
    pplx = ask(question)
    pplx_text = pplx["choices"][0]["message"]["content"]
    pplx_cites = pplx.get("citations") or []

    par = search(question, [question, question.replace("?", "")])
    excerpts = []
    for r in par.get("results", [])[:5]:
        text = (r.get("excerpts") or [""])[0][:800]
        excerpts.append(f"### {r.get('title')}\n{r.get('url')}\n\n{text}\n")

    md = f"""# Research bundle

**Вопрос:** {question}

## Perplexity (синтез + citations)

{pplx_text}

**Источники:**
{chr(10).join(f'- {u}' for u in pplx_cites)}

## Parallel Search (сырые выдержки для RAG)

{''.join(excerpts)}

---
*Сгенерировано research_router.py*
"""
    return md


def main():
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "Как настроить pgvector в Supabase для RAG?"
    )
    md = bundle(question)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = OUTPUT_DIR / f"research-bundle-{stamp}.md"
    out.write_text(md)
    print(md[:2000])
    if len(md) > 2000:
        print(f"\n… (ещё {len(md) - 2000} символов)")
    print(f"\nСохранено: {out}")


if __name__ == "__main__":
    main()
