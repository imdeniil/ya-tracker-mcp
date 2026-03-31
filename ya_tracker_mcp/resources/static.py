from fastmcp import FastMCP


QUERY_LANGUAGE = """# Yandex Tracker Query Language

## Format
"<Parameter>": "<value>"

## Operators
| Operator | Example |
|----------|---------|
| AND (or space) | Queue: DEV AND Status: Open |
| OR | Priority: Critical OR Priority: Blocker |
| () | (Assignee: me() OR Author: me()) AND Status: Open |
| !"value" | Priority: !"Minor" |
| > < >= <= | Created: >2017-01-01 |
| .. | Created: 2017-01-01..2017-01-30 |
| , | Status: "Open", "In Progress" |

## Functions
| Function | Result |
|----------|--------|
| empty() | Empty value |
| notEmpty() | Any non-empty |
| me() | Current user |
| now() | Current time |
| today() | Today's date |
| week() / month() / quarter() / year() | Current period |
| unresolved() | No resolution |

Arithmetic: today() + 3d, now() - "1w 1d"

## Search by changes
Status: changed(to: "In Progress" by: "user" date: >today()-1w)

## Sort
"Sort By": Created ASC, Updated DESC

## Common queries
- My open tasks: Assignee: me() Resolution: empty()
- Overdue: Deadline: <today() Resolution: empty()
- Critical without assignee: Priority: Critical, Blocker AND Assignee: empty()
"""

YFM_SYNTAX = """# YFM - Yandex Flavored Markdown

## Text formatting
| Markup | Result |
|--------|--------|
| **text** | Bold |
| _text_ | Italic |
| ++text++ | Underline |
| ~~text~~ | Strikethrough |
| ##text## | Monospace |
| ==text== | Highlight |
| {color}(text) | Colored (gray/yellow/orange/red/green/blue/violet) |
| `code` | Inline code |
| @login | Mention user |
| TEST-123 | Auto-link to issue |

## Notes
{% note info "Title" %}
Content
{% endnote %}
Types: info (blue), warning (orange), alert (red), tip (green)

## Collapsible sections
{% cut "Click to expand" %}
Hidden content
{% endcut %}

## Tables (wiki-style)
#|
|| **Header 1** | **Header 2** ||
|| cell 1 | cell 2 ||
|#
"""

LINK_TYPES = """# Issue Link Types

| Type | relationship value |
|------|-------------------|
| Related | relates |
| Depends on | depends on |
| Blocks | is dependent by |
| Subtask | is subtask for |
| Parent | is parent task for |
| Duplicate of | duplicates |
| Is duplicated by | is duplicated by |
| Epic of | is epic of |
| Has epic | has epic |
| Clone | clone |
| Original | original |
"""

ENTITY_STATUSES = """# Entity Statuses

## Projects / Portfolios
draft, draft2, in_progress, according_to_plan, postponed, at_risk, blocked, launched, cancelled

## Goals
draft, according_to_plan, at_risk, blocked, achieved, partially_achieved, not_achieved, exceeded, cancelled
"""

FIELD_TYPES = """# Issue Field Types

| Type | Java path |
|------|-----------|
| String | ru.yandex.startrek.core.fields.StringFieldType |
| Text | ru.yandex.startrek.core.fields.TextFieldType |
| Integer | ru.yandex.startrek.core.fields.IntegerFieldType |
| Float | ru.yandex.startrek.core.fields.FloatFieldType |
| Date | ru.yandex.startrek.core.fields.DateFieldType |
| DateTime | ru.yandex.startrek.core.fields.DateTimeFieldType |
| User | ru.yandex.startrek.core.fields.UserFieldType |
| Uri | ru.yandex.startrek.core.fields.UriFieldType |

name: {"en": "English", "ru": "Russian"}
container=True for multi-value (String, User with optionsProvider)
optionsProvider: {"type": "FixedListOptionsProvider", "values": ["A", "B"]}
"""

API_ERRORS = """# API Errors

| Code | Exception | Description |
|------|-----------|-------------|
| 400 | BadRequestError | Invalid parameters |
| 401 | UnauthorizedError | Invalid token |
| 403 | ForbiddenError | Insufficient permissions |
| 404 | NotFoundError | Object not found |
| 409 | ConflictError | Version conflict |
| 412 | PreconditionFailedError | Stale version (If-Match) |
| 422 | UnprocessableEntityError | Validation error |
| 423 | LockedError | Object locked |
| 428 | PreconditionRequiredError | Missing version |
| 429 | TooManyRequestsError | Rate limit |
| 5xx | ServerError | Server error |

All inherit TrackerAPIError with: status_code, url, method, error_messages
"""

TIPS = """# Yandex Tracker Tips & Caveats

## Local Fields

Local fields are queue-specific custom fields. They work like global fields but with important differences:

### Searching by local fields
Prefix the field name with the queue key and a dot:
- `DEVS.Tester: "Ivan Ivanov"`
- Multi-word field names must be quoted: `DEVS."QA Engineer": "Ivan Ivanov"`

This avoids ambiguity when different queues have local fields with the same name.

### Moving/copying issues
Local field values are **lost** when an issue is moved or copied to another queue.

### Variables in automations
In macros, triggers, and autoactions, reference local fields as:
`{{issue.local.<field_key>}}`

This applies to comment templates, formulas, and HTTP request bodies.

## Query Language Tips

### Relative dates
- `Created: >today()-1w` — created in the last week
- `Deadline: <now()+"3d"` — deadline within 3 days
- Supported units: `m` (minutes), `h` (hours), `d` (days), `w` (weeks)

### Searching by changes
`Status: changed(to: "In Progress" by: "user" date: >today()-1w)`
- Parameters `to`, `from`, `by`, `date` are all optional

### Empty vs non-empty
- `Resolution: empty()` — unresolved issues
- `Assignee: notEmpty()` — assigned issues

## Bulk Operations

### Rate limits
Bulk operations (bulk_update, bulk_move, bulk_transition) are async. Use `get_bulk_status` to poll for completion. Large batches may take minutes.

### Bulk update limitations
- Cannot set fields that require workflow transitions (e.g., status)
- Use `bulk_transition` for status changes instead

## Entities (Projects, Portfolios, Goals)

### Entity types
Always pass `entity_type` as one of: `project`, `portfolio`, `goal`.

### Goal key results
Use `update_key_results` to manage OKR-style key results on goals. Each key result needs `title` and optionally `unit`, `target`, `current`.

## Checklists

### Checklist vs subtasks
- Checklists are lightweight (no separate issue key)
- Subtasks are full issues linked via "is subtask for"
- Use checklists for simple to-do lists, subtasks for trackable work items
"""


def register_resources(mcp: FastMCP):

    @mcp.resource("tracker://query-language")
    def query_language() -> str:
        """Yandex Tracker query language syntax reference."""
        return QUERY_LANGUAGE

    @mcp.resource("tracker://yfm-syntax")
    def yfm_syntax() -> str:
        """YFM (Yandex Flavored Markdown) syntax reference."""
        return YFM_SYNTAX

    @mcp.resource("tracker://link-types")
    def link_types() -> str:
        """Issue link types reference."""
        return LINK_TYPES

    @mcp.resource("tracker://entity-statuses")
    def entity_statuses() -> str:
        """Project, portfolio, and goal status values."""
        return ENTITY_STATUSES

    @mcp.resource("tracker://field-types")
    def field_types() -> str:
        """Issue field types with Java paths."""
        return FIELD_TYPES

    @mcp.resource("tracker://api-errors")
    def api_errors() -> str:
        """API error codes and exception types."""
        return API_ERRORS

    @mcp.resource("tracker://tips")
    def tips() -> str:
        """Tips and caveats for using Yandex Tracker: local fields, query tricks, bulk ops, entities."""
        return TIPS
