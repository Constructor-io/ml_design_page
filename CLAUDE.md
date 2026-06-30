# ML Design Documents

## Что это

Набор технических design-документов для ML-системы e-commerce search/recommendations (Constructor.io). Описывают целевую архитектуру — к которой стремимся, не текущее состояние.

## Файлы

- `principles.md` — инженерные принципы ML платформы
- `attribution.md` — attribution pipeline (как связываем действия юзеров с запросами для training data)
- `retrieval.md` — L0: multi-stream retrieval (candidate generation, 800-1200 items)
- `personalization.md` — personalization: scoring model + embedding model
- `reranker.md` — L1: two-stage reranker (Stage A pointwise GBDT + Stage B listwise neural)
- `reranker_current_state.md` — reference: текущая система (как есть сейчас)

## Контекст

SaaS product search. 200+ клиентов (e-commerce stores). Multi-tenant: shared infra, per-customer models/configs.

Кодовые базы для reference:
- `../lingoml` — ML библиотека (reranker models, preprocessing, backends)
- `../data-pipeline` — training pipelines (Luigi/Spark, feature store, customer configs)
- `../autocomplete` — serving (reranker service, feature store client, SABR)

## Как писать

- Суровая техническая дока. Без воды, без продуктовых/мотивационных предложений. Все всё понимают.
- Описываем целевое состояние системы, не переход из текущего. Не нужен roadmap.
- Учитываем реальные ограничения (inverted index никуда не денется, reranker service существует), но не отталкиваемся от текущих ограничений при проектировании.
- Русский язык, технические термины на английском.
- Стиль: как retrieval.md и personalization.md — structured, concise, с примерами и диаграммами где нужно.
