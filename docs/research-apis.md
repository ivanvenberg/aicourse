# Глава: Perplexity + Parallel — полная теория поиска для AI-native

*Дополнение к урокам 4–5. Без продакт-менеджмента — только инженерия: как доставать факты из сети, не галлюцинировать, встраивать в агентов и RAG.*

Живые скрипты: [`examples/research/`](../examples/research/). Ключи: `docs/env.example` → `.env` (не в git).

---

## Проверь себя

| Вопрос | ✅ / ❌ |
|--------|--------|
| Почему «спроси ChatGPT» плохо для фактов 2026 года | |
| Чем Search отличается от Task у Parallel | |
| Что такое `citations` / `basis` | |
| Когда Perplexity, когда Parallel Search, когда Task | |
| Как связать поиск с RAG | |
| Где хранить ключи и что делать если засветил | |

---

## 1. Проблема: модель не интернет

```
Пользователь: «Какой лимит у sonar-pro в Perplexity?»

Без поиска:
  модель → уверенный ответ → возможно выдуманный URL

С поисковым API:
  модель → API ходит в сеть → ответ + URL → ты проверяешь
```

**Три симптома «без поиска»:**
1. **Устаревание** — обучение модели отстаёт от релизов.
2. **Галлюцинации ссылок** — красивый markdown, мёртвый домен.
3. **Нет трассировки** — непонятно, откуда факт.

**AI-native правило:** любой факт «из мира» → **источник в файле** (`research.md`, `citations[]`, `basis[]`).

---

## 2. Карта инструментов Parallel

Parallel — не один endpoint, а **семейство** API для разных глубин ресёрча.

| API | Форма | Латентность | Когда |
|-----|-------|-------------|-------|
| **Search** | objective + keyword queries → `results[].excerpts` | секунды | Быстрые факты, материал для RAG |
| **Extract** | URL → чистые выдержки/markdown | секунды | Уже знаешь страницу, нужен текст |
| **Task** | вопрос/JSON + schema → структура + `basis` | секунды–часы | Глубокий ресёрч, обогащение таблиц |
| **Entity Search** | люди/компании → ranked matches | секунды | Поиск сущностей |
| **FindAll** | критерии → список сущностей | минуты | Лид-листы, конкурентная карта |
| **Monitor** | расписание + webhook | фон | «Скажи, если изменилось» |

Документация: [docs.parallel.ai](https://docs.parallel.ai). Индекс для агентов: `https://docs.parallel.ai/llms.txt`.

### Perplexity vs Parallel — не конкуренты

| | Perplexity API | Parallel |
|--|----------------|----------|
| Сильная сторона | Готовый **синтез** ответа + citations | **Сырые выдержки** и структурированный ресёрч |
| Формат | `chat/completions` (как OpenAI) | Search / Task / Extract |
| Лучше для | «Объясни за 30 секунд» | «Дай 20 кусков текста в RAG» |
| Цена | за запрос + токены | за processor tier |

**Паттерн курса:** Perplexity = первый черновик; Parallel Search = корпус для RAG; Parallel Task = таблица/JSON с полями.

---

## 3. Perplexity API — подробно

### 3.1 Модели

| Модель | Смысл |
|--------|--------|
| `sonar` | Быстрый поиск + ответ |
| `sonar-pro` | Глубже, дороже |
| `sonar-reasoning` | С рассуждением (если нужна цепочка) |

Актуальный список — в [docs.perplexity.ai](https://docs.perplexity.ai).

### 3.2 Запрос

```bash
curl https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar",
    "messages": [
      {"role": "user", "content": "Что такое MCP? Дай 3 примера серверов."}
    ]
  }'
```

Ключ: `PERPLEXITY_API_KEY` в `.env`. Префикс `pplx-`.

### 3.3 Реальный ответ (сокращённо, проверено на API)

**Текст:**
> MCP — open-source стандарт для подключения AI к внешним системам… Примеры серверов: Google Drive, Slack, GitHub.

**Поля ответа:**
```json
{
  "choices": [{"message": {"content": "…"}}],
  "citations": [
    "https://www.anthropic.com/news/model-context-protocol",
    "https://en.wikipedia.org/wiki/Model_Context_Protocol"
  ],
  "usage": {
    "total_tokens": 117,
    "cost": {
      "request_cost": 0.005,
      "total_cost": 0.00512
    }
  }
}
```

**Важно:**
- `citations` — массив URL, не всегда 1:1 с `[1][2]` в тексте.
- `usage.cost` — считай бюджет на демо (урок 6).
- Сохраняй **и текст, и citations** в `research/`.

### 3.4 Python

См. `examples/research/ask_perplexity.py`.

### 3.5 Когда НЕ Perplexity

- Внутренние PDF/Notion → **RAG**.
- Точные цифры по `data/*.csv` → **скрипт** (урок 3).
- Нужны сырые куски 10 страниц, не эссе → **Parallel Search**.

---

## 4. Parallel Search API

### 4.1 Смысл

Один round-trip: **цель на человеческом** + 2–3 keyword-запроса → массив страниц с **уже сжатыми** `excerpts` (удобно в контекст модели).

### 4.2 Запрос

```bash
curl https://api.parallel.ai/v1/search \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "objective": "Найти туториалы по pgvector для RAG",
    "search_queries": [
      "pgvector RAG tutorial",
      "supabase pgvector embeddings"
    ]
  }'
```

### 4.3 Реальный фрагмент ответа

```json
{
  "search_id": "search_2fe33c3f6303405997afdf1f673de06d",
  "results": [
    {
      "url": "https://encore.dev/blog/you-probably-dont-need-a-vector-database",
      "title": "pgvector Guide: Vector Search and RAG in PostgreSQL",
      "publish_date": "2026-03-09",
      "excerpts": [
        "pgvector is a PostgreSQL extension that adds vector storage..."
      ]
    }
  ]
}
```

### 4.4 Как кормить агенту

```
1. parallel_search.py → output/*.json
2. Агент: «Возьми excerpts из output/… → sources.md»
3. Ответь на вопрос ТОЛЬКО по sources.md. Если нет данных — скажи честно.
```

Это **grounding**: модель не придумывает, а пересказывает выдержки.

### 4.5 Search → RAG pipeline

```
excerpts[] → чанки (500–800 токенов) → embeddings → pgvector
```

На уроке 5: тот же текст можно положить в `knowledge/` без векторизации — для прототипа хватит grep + один файл `sources.md`.

---

## 5. Parallel Extract API

Когда URL **уже известен** (нашёл через Search или дал пользователь).

```bash
curl https://api.parallel.ai/v1beta/extract \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "urls": ["https://docs.parallel.ai/getting-started/overview"],
    "objective": "Какие API предлагает Parallel?"
  }'
```

**Ответ:** `extract_id`, `results[]` с `excerpts` — по сути «прочитай эту страницу за меня», в т.ч. JS-сайты и PDF.

Скрипт: `examples/research/parallel_extract.py`.

---

## 6. Parallel Task API

### 6.1 Смысл

**Multi-hop ресёрч:** агент Parallel сам ходит по сети, синтезирует, отдаёт **структуру** + **basis** (поле → citations → reasoning → confidence).

Жизненный цикл: `POST /v1/tasks/runs` → `status: queued` → poll `GET …/result` или webhook/SSE для `pro`/`ultra`.

### 6.2 Processors (tiers)

| Processor | Ожидание | Для чего |
|-----------|----------|----------|
| `lite` | ~30–60 с | Факты, 1–2 поля |
| `base` | ~1–3 мин | Стандартный ресёрч |
| `core` | несколько мин | Сложнее, больше источников |
| `pro` / `ultra` | 10 мин – 2 ч | Отчёты; на `ultra` — webhook |

### 6.3 Создание run (текст)

```bash
curl -X POST https://api.parallel.ai/v1/tasks/runs \
  -H "Content-Type: application/json" \
  -H "x-api-key: $PARALLEL_API_KEY" \
  -d '{
    "input": "OpenRouter",
    "processor": "lite",
    "task_spec": {
      "output_schema": "Год основания и одно предложение что это за сервис"
    }
  }'
```

**Ответ создания:**
```json
{
  "run_id": "trun_4c2e0ec6d7bd4ef68eeec23338bf2819",
  "status": "queued",
  "processor": "lite"
}
```

### 6.4 Результат (реальный пример)

```json
{
  "run": { "status": "completed", "processor": "lite" },
  "output": {
    "type": "text",
    "content": "2023; OpenRouter is a unified API gateway...",
    "basis": [{
      "field": "output",
      "confidence": "high",
      "reasoning": "Multiple reliable sources...",
      "citations": [
        {
          "title": "OpenRouter — StartupHub.ai",
          "url": "https://www.startuphub.ai/startups/openrouter",
          "excerpts": ["OpenRouter was founded in 2023."]
        }
      ]
    }]
  }
}
```

### 6.5 JSON schema на выходе

```bash
# task_spec.output_schema.type = "json" + json_schema
# Пример: Claude Code → what_is + key_features[]
```

Реальный `content` (тип `json`):
```json
{
  "what_is": "Claude Code is Anthropic's terminal-based agentic coding tool...",
  "key_features": [
    "Agentic Loop: plans, reads files, executes commands...",
    "CLAUDE.md — Project Memory."
  ]
}
```

Каждое поле в `basis[]` — свои `citations` и `confidence: high|medium|low`.

Скрипт с polling: `examples/research/parallel_task.py`.

### 6.6 Batch / обогащение CSV

```
companies.csv (50 строк)
  → for row: Task(input=row.name, schema={website, niche})
  → merged.csv
```

Для сотен строк — **Task Groups** (параллельные runs + агрегация). См. docs: Task Groups.

### 6.7 Лимиты и ошибки

- **429** — >2000 req/min на ключ; backoff + retry.
- **failed** — смотри `errors` в run; упрости schema или смени processor.
- Долгие задачи — не блокируй UI; webhook → продолжить в фоне.

---

## 7. Entity Search, FindAll, Monitor (кратко)

### Entity Search
Быстрый поиск **людей/компаний** с ранжированием. Когда Task — overkill, а Search — слишком общий.

### FindAll
«Найди все студии motion design в Берлине с сайтом» → датасет с верификацией. Для креативных профессий: конкуренты, референсы, подрядчики — **не** для PM-воронок.

### Monitor
NL-запрос по расписанию + webhook при изменениях. Пример: «Новости про лицензии Midjourney» → Telegram-бот (урок 5).

---

## 8. Схемы интеграции

### 8.1 Агент в Cursor / Claude Code

```
Ты → «Исследуй тему X»
  → skill / скрипт parallel_search.py
  → sources.md
  → агент пишет черновик строго по sources.md
```

**Parallel MCP** (`parallel-web`) — агент вызывает Search без твоего скрипта:
```bash
/plugin marketplace add parallel-web/parallel-agent-skills
/parallel:setup
```

### 8.2 Perplexity + RAG (урок 5)

```
Вопрос
  ├─ свежие факты?     → Perplexity (citations)
  ├─ наши доки?        → RAG / knowledge/
  └─ сырые страницы?   → Parallel Search → chunks → pgvector
        ↓
  Собрать context с метками [WEB] [INTERNAL]
        ↓
  OpenRouter / Claude → ответ
```

**Не смешивай** регламент компании и новости из сети без пометок — модель склеит как одну правду.

### 8.3 research_router

`examples/research/research_router.py` — один вопрос → markdown с двумя секциями. Шаблон для домашки.

### 8.4 Tool use в своём боте

Опиши tools для модели:

```json
{
  "name": "web_search",
  "description": "Искать выдержки в интернете через Parallel",
  "parameters": {
    "type": "object",
    "properties": {
      "objective": {"type": "string"},
      "search_queries": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```

В `execute` — HTTP к Parallel, верни JSON агенту.

---

## 9. Безопасность и гигиена

| Правило | Почему |
|---------|--------|
| Ключи только в `.env` | git публичный |
| Не вставлять ключ в чат Cursor | логи, история |
| Засветил ключ → **rotate** в кабинете | billing чужих |
| Не отдавать агенту prod-ключи без лимитов | «протестирую на 10k запросов» |
| Логировать `search_id` / `run_id` | дебаг и support |

---

## 10. Стоимость и выбор (практика)

| Сценарий | Инструмент | Порядок цены |
|----------|------------|--------------|
| FAQ бота «что нового в MCP» | Perplexity sonar | ~$0.005/запрос |
| Подложить 5 статей в RAG | Parallel Search | зависит от тарифа |
| 100 компаний → колонка «сайт» | Parallel Task lite × 100 | считай заранее |
| Еженедельный дайджест | Monitor + Extract | фон |

**Для курса:** начни с `lite` / `sonar`, смотри `usage` / dashboard провайдера.

---

## 11. Типичные ошибки

| Ошибка | Симптом | Фикс |
|--------|---------|------|
| Один промпт «сделай ресёрч» без API | Выдуманные URL | Search/Task |
| Игнор citations | Нельзя проверить | Сохранять в md |
| Task без polling | Пустой ответ | Ждать `completed` |
| Search без `search_queries` | Слабее recall | 2–3 keyword |
| Perplexity для 50 PDF | Дорого и мимо | RAG |
| Ключ в репозитории | 403/чужие траты | .env + rotate |

---

## 12. Чеклист «готово к уроку 5»

- [ ] `.env` с `PERPLEXITY_API_KEY` и `PARALLEL_API_KEY`
- [ ] `python examples/research/parallel_search.py` — есть `search_id`
- [ ] `python examples/research/ask_perplexity.py` — есть `citations`
- [ ] `python examples/research/parallel_task.py` — `status: completed`
- [ ] Понимаешь: Search vs Task vs Perplexity
- [ ] В проекте есть `research/` или `output/` с сохранёнными источниками

---

## 13. Ссылки

- [Perplexity API](https://docs.perplexity.ai)
- [Parallel docs](https://docs.parallel.ai)
- [Parallel Search quickstart](https://docs.parallel.ai/search-api/search-quickstart)
- [Parallel Task quickstart](https://docs.parallel.ai/task-api/task-quickstart)
- [Task lifecycle](https://docs.parallel.ai/task-api/guides/execute-task-run)
- [Python SDK](https://github.com/parallel-web/parallel-sdk-python)

**Следующий шаг в курсе:** `lesson-5/theory.md` — RAG, pgvector, боты, OWASP.
