# Примеры: Perplexity + Parallel

Скрипты для уроков 4–5. Ключи — только в `.env` в корне **твоего** проекта (см. `docs/env.example`).

## Быстрый старт

```bash
cd examples/research
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Скопируй docs/env.example → .env в корне aicourse (или в examples/research)
export $(grep -v '^#' ../../.env | xargs) 2>/dev/null || true

python parallel_search.py "pgvector RAG tutorial"
python ask_perplexity.py "Что такое MCP в двух предложениях?"
python parallel_task.py "OpenRouter"
python parallel_extract.py "https://docs.parallel.ai/getting-started/overview"
python research_router.py "Как настроить pgvector в Supabase?"
```

Результаты по умолчанию пишутся в `output/` (в `.gitignore`).

Полная теория: [`docs/research-apis.md`](../../docs/research-apis.md).
