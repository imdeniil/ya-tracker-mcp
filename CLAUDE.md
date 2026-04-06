# Ya-Tracker-MCP

MCP-сервер для Yandex Tracker API на базе FastMCP. Версия в pyproject.toml.

## Общие правила

- Думай и действуй на английском, отвечай в чате на русском
- Используй uv

## Документация

- `docs/mcp.txt` — справочник FastMCP. Не читай полностью, ищи нужную информацию по ключевым словам
- `docs/YaTrackerApi.md` — подробная документация по API Яндекс Трекера
- `docs/ya-tracker-mcp-reference.md` — справочник по самому проекту

## Архитектура

```
ya_tracker_mcp/
├── server.py              — точка входа, lifespan (инициализация клиента), регистрация всех модулей
├── tools/                 — 22 модуля MCP-инструментов (~4200 строк)
│   ├── issues.py          — CRUD задач, поиск, changelog, перемещение
│   ├── entities.py        — проекты/портфолио/цели (CRUD, комментарии, связи, чеклисты, метрики)
│   ├── directories.py     — справочники (типы, статусы, приоритеты, поля) с кешированием
│   ├── automations.py     — автоэкшены, макросы, триггеры
│   ├── queues.py          — очереди и версии
│   ├── boards.py          — доски и колонки
│   ├── overviews.py       — сводки по задаче/очереди
│   ├── presets.py         — пресеты создания задач из YAML-конфига
│   └── ...                — comments, links, transitions, users, worklog, checklists,
│                            attachments, team, bulk, imports, filters, dashboards, external_links
├── utils/
│   ├── directory_manager.py — DirectoryManager: кеш справочников в YAML с TTL
│   └── formatters.py       — format_mcp_item/format_mcp_list для MCP-ответов
├── resources/static.py    — 6 статических ресурсов (query language, YFM, типы связей и др.)
├── prompts/prompts.py     — 4 промпта (мои задачи, визард, декомпозиция, отчёт просрочки)
└── ~/.cache/ya-tracker-mcp/ — YAML-конфиги (presets.yaml, team.yaml, directories.yaml)
```

## Ключевые паттерны

### Register-pattern
Каждый модуль в `tools/` экспортирует `register_*_tools(mcp: FastMCP)`. Внутри — `@mcp.tool()` декораторы. Доступ к API через `ctx.lifespan_context["tracker"]`.

### Добавление нового инструмента
1. Создать/открыть модуль в `tools/`
2. Добавить функцию с `@mcp.tool()` внутри `register_*_tools`
3. Если новый модуль — импортировать и вызвать `register_*_tools(mcp)` в `server.py`

### Кеширование справочников
`DirectoryManager` (`utils/directory_manager.py`) хранит данные в `~/.cache/ya-tracker-mcp/directories.yaml` с настраиваемыми TTL. Инструменты справочников принимают `use_cache: bool = True`.

### Форматирование ответов
`utils/formatters.py` — `format_mcp_item` и `format_mcp_list` с шаблонами и поддержкой `extra_fields`.

## Зависимости

- `fastmcp >= 2.0.0` — MCP-фреймворк
- `YaTrackerApi >= 2.3.0` — async-клиент Yandex Tracker
- `pyyaml >= 6.0` — конфигурация и кеш

## Env-переменные

- `YA_TRACKER_TOKEN` или `TRACKER_API_KEY` — OAuth-токен
- `YA_TRACKER_ORG_ID` или `TRACKER_ORG_ID` — ID организации

## Запуск

```bash
uv run ya-tracker-mcp
```