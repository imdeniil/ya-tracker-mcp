# ya-tracker-mcp

MCP server for [Yandex Tracker](https://tracker.yandex.ru/) API. Provides 145 tools for managing issues, projects, boards, sprints, worklog and more through the [Model Context Protocol](https://modelcontextprotocol.io/).

Built with [FastMCP](https://gofastmcp.com) and [YaTrackerApi](https://pypi.org/project/YaTrackerApi/).

## Quick Start

### Claude Code

```bash
claude mcp add ya-tracker \
  -e YA_TRACKER_TOKEN=your-oauth-token \
  -e YA_TRACKER_ORG_ID=your-org-id \
  -- uvx ya-tracker-mcp
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ya-tracker": {
      "command": "uvx",
      "args": ["ya-tracker-mcp"],
      "env": {
        "YA_TRACKER_TOKEN": "your-oauth-token",
        "YA_TRACKER_ORG_ID": "your-org-id"
      }
    }
  }
}
```

### Cursor / Windsurf

Add to MCP settings:

```json
{
  "ya-tracker": {
    "command": "uvx",
    "args": ["ya-tracker-mcp"],
    "env": {
      "YA_TRACKER_TOKEN": "your-oauth-token",
      "YA_TRACKER_ORG_ID": "your-org-id"
    }
  }
}
```

## Authentication

You need an OAuth token and organization ID:

1. **OAuth token** - get at [oauth.yandex.ru](https://oauth.yandex.ru/) with Tracker access
2. **Organization ID** - find in Tracker admin settings or via API `GET /v3/myself`

## Tools (145)

### Issues (7)
| Tool | Description |
|------|-------------|
| `create_issue` | Create issue (queue, summary, type, priority, assignee, extra_fields for custom/local fields) |
| `get_issue` | Get issue details with optional expand (transitions, attachments) |
| `update_issue` | Update issue fields (supports extra_fields for custom/local fields) |
| `search_issues` | Search with query language or filters |
| `count_issues` | Count matching issues |
| `move_issue` | Move to another queue |
| `issue_changelog` | Get issue change history (filter by field) |

### Comments (4)
| Tool | Description |
|------|-------------|
| `add_comment` | Add comment with optional summonees |
| `list_comments` | List issue comments |
| `update_comment` | Update comment text |
| `delete_comment` | Delete comment |

### Status Transitions (2)
| Tool | Description |
|------|-------------|
| `list_transitions` | List available transitions |
| `transition_issue` | Execute status transition |

### Links (3)
| Tool | Description |
|------|-------------|
| `link_issues` | Create link (relates, depends on, subtask, epic...) |
| `list_links` | List issue links |
| `delete_link` | Delete link |

### Entities — Projects / Portfolios / Goals (23)
| Tool | Description |
|------|-------------|
| `create_entity` | Create project, portfolio, or goal |
| `get_entity` | Get entity with fields |
| `update_entity` | Update entity |
| `delete_entity` | Delete entity |
| `search_entities` | Search entities |
| `entity_changelog` | Get entity change history |
| `update_key_results` | Update goal key results |
| `update_entity_metrics` | Update entity metrics |
| `list_entity_comments` | List entity comments |
| `add_entity_comment` | Add comment to entity |
| `update_entity_comment` | Update entity comment |
| `delete_entity_comment` | Delete entity comment |
| `list_entity_links` | List entity links |
| `create_entity_link` | Create link between entities |
| `delete_entity_link` | Delete entity link |
| `list_entity_attachments` | List entity attachments |
| `delete_entity_attachment` | Delete entity attachment |
| `add_entity_checklist_item` | Add checklist item to entity |
| `update_entity_checklist_item` | Update entity checklist item |
| `delete_entity_checklist_item` | Delete entity checklist item |
| `bulk_update_entities` | Bulk update entities |
| `get_entity_settings` | Get entity access settings |
| `update_entity_settings` | Update entity access settings |

### Boards & Sprints (12)
| Tool | Description |
|------|-------------|
| `list_boards` | List all boards (cached) |
| `get_board` | Board details |
| `create_board` | Create board (invalidates cache) |
| `update_board` | Update board settings (invalidates cache) |
| `delete_board` | Delete board (invalidates cache) |
| `list_board_columns` | Board columns with statuses |
| `create_board_column` | Create column |
| `update_board_column` | Update column |
| `delete_board_column` | Delete column |
| `list_sprints` | Board sprints (cached) |
| `get_sprint` | Sprint details |
| `create_sprint` | Create sprint (invalidates cache) |

### Worklog (5)
| Tool | Description |
|------|-------------|
| `add_worklog` | Log time (ISO 8601 duration) |
| `list_worklog` | List worklog entries |
| `update_worklog` | Update entry |
| `delete_worklog` | Delete entry |
| `search_worklog` | Search worklog across all issues |

### Checklists (5)
| Tool | Description |
|------|-------------|
| `list_checklist` | List checklist items |
| `add_checklist_item` | Add item |
| `update_checklist_item` | Update item (text, checked, assignee) |
| `delete_checklist_item` | Delete item |
| `delete_checklist` | Delete entire checklist |

### Attachments (2)
| Tool | Description |
|------|-------------|
| `list_attachments` | List attachments |
| `delete_attachment` | Delete attachment |

### Queues (10)
| Tool | Description |
|------|-------------|
| `list_queues` | List all queues (cached) |
| `get_queue` | Queue details (expand: components, versions) |
| `create_queue` | Create queue (invalidates cache) |
| `delete_queue` | Delete queue (invalidates cache) |
| `restore_queue` | Restore deleted queue (invalidates cache) |
| `list_queue_versions` | List queue versions |
| `create_queue_version` | Create version |
| `delete_queue_tag` | Delete queue tag (invalidates cache) |
| `get_queue_user_permissions` | Get user permissions for queue |
| `update_queue_permissions` | Update queue access permissions |

### Users (3)
| Tool | Description |
|------|-------------|
| `get_myself` | Current user info |
| `get_user` | Get specific user info |
| `list_users` | Organization users (cached) |

### Cache Management (4)
| Tool | Description |
|------|-------------|
| `get_cache_status` | Show status of directories cache (TTL, last updated, record count) |
| `sync_directory` | Manually sync a specific directory from API (supports scope) |
| `sync_all_directories` | Force sync all basic directories from API |
| `configure_cache` | Configure TTL for a specific directory cache |

> **Tip:** Most `list_*` tools now support a `use_cache: bool` parameter (default: `True`). Set it to `False` to force a fresh fetch from the API.

### Directories — Reference Data (27)
| Tool | Description |
|------|-------------|
| `list_issue_types` | All issue types (cached) |
| `create_issue_type` | Create issue type (invalidates cache) |
| `update_issue_type` | Update issue type |
| `list_statuses` | All statuses (cached) |
| `create_status` | Create status (invalidates cache) |
| `update_status` | Update status |
| `list_priorities` | All priorities (cached) |
| `create_priority` | Create priority (invalidates cache) |
| `update_priority` | Update priority |
| `list_resolutions` | All resolutions (cached) |
| `create_resolution` | Create resolution (invalidates cache) |
| `update_resolution` | Update resolution |
| `list_global_fields` | Global fields (cached) |
| `get_field` | Get field details |
| `create_field` | Create global field |
| `update_field` | Update global field |
| `list_queue_fields` | Queue fields (cached) |
| `get_local_field` | Get local field |
| `create_local_field` | Create local field |
| `update_local_field` | Update local field |
| `list_queue_tags` | Queue tags (cached) |
| `list_components` | All components (cached, supports `fields` param) |
| `get_component` | Get component details by ID |
| `create_component` | Create component (invalidates cache) |
| `update_component` | Update component (invalidates cache) |
| `list_field_categories` | List field categories (cached) |
| `create_field_category` | Create field category (bilingual name) |
| `update_field_category` | Update field category |

### Automations (15)
| Tool | Description |
|------|-------------|
| `list_macros` | List queue macros |
| `get_macro` | Get macro details |
| `create_macro` | Create macro |
| `update_macro` | Update macro |
| `delete_macro` | Delete macro |
| `list_triggers` | List queue triggers |
| `get_trigger` | Get trigger details |
| `create_trigger` | Create trigger |
| `update_trigger` | Update trigger |
| `get_trigger_logs` | Get trigger execution logs |
| `list_autoactions` | List queue autoactions |
| `get_autoaction` | Get autoaction details |
| `create_autoaction` | Create autoaction |
| `get_autoaction_logs` | Get autoaction execution logs |

### Bulk Operations (5)
| Tool | Description |
|------|-------------|
| `bulk_update` | Update multiple issues |
| `bulk_move` | Move issues to queue |
| `bulk_transition` | Transition multiple issues |
| `get_bulk_status` | Check operation status |
| `get_bulk_failed_issues` | Get failed issues from bulk operation |

### Import (4)
| Tool | Description |
|------|-------------|
| `import_issue` | Import with original dates/author |
| `import_comment` | Import comment |
| `import_link` | Import link |
| `import_file` | Import file attachment |

### Filters (3)
| Tool | Description |
|------|-------------|
| `create_filter` | Create saved filter |
| `get_filter` | Get filter details |
| `update_filter` | Update filter |

### Dashboards (2)
| Tool | Description |
|------|-------------|
| `create_dashboard` | Create dashboard |
| `create_cycle_time_widget` | Create cycle time widget |

### External Links (4)
| Tool | Description |
|------|-------------|
| `list_external_applications` | List registered external apps |
| `list_external_links` | List external links on issue |
| `create_external_link` | Create external link |
| `delete_external_link` | Delete external link |

### Overviews (2)
| Tool | Description |
|------|-------------|
| `issue_overview` | Full issue summary (status, links, comments, checklist, worklog) |
| `queue_overview` | Queue summary (open count, top priority issues) |

### Presets (5)
| Tool | Description |
|------|-------------|
| `list_presets` | Available task presets |
| `get_preset` | Preset details (params, template, rules) |
| `create_from_preset` | Create issue from preset (supports overrides and extra_fields) |
| `add_preset` | Add or update a preset at runtime (params supports all create_issue fields) |
| `remove_preset` | Remove a preset |

### Team Directory (3)
| Tool | Description |
|------|-------------|
| `list_team` | Team members |
| `get_team_member` | Member details (areas, queues) |
| `find_assignee` | Find assignee by area/queue |

## Resources (6)

| Resource | Description |
|----------|-------------|
| `tracker://query-language` | Query language syntax |
| `tracker://yfm-syntax` | YFM markdown reference |
| `tracker://link-types` | Issue link types |
| `tracker://entity-statuses` | Entity status values |
| `tracker://field-types` | Field types with Java paths |
| `tracker://api-errors` | API error codes |

## Prompts (4)

| Prompt | Description |
|--------|-------------|
| `my_tasks` | Show active tasks with priorities |
| `create_task_wizard` | Step-by-step task creation |
| `issue_decomposition` | Decompose issue into subtasks |
| `overdue_report` | Overdue tasks report |

## Configuration

### Task Presets

Define presets in `config/presets.yaml` or manage at runtime with `add_preset` / `remove_preset`. `params` section supports all fields from `create_issue` (type, priority, assignee, tags, components, sprint, parent, project, followers, deadline, story_points, original_estimation, extra_fields):

```yaml
presets:
  bug_report:
    name: "Bug report"
    description: "Bug with reproduction steps"
    params:
      type: "bug"
      priority: "critical"
      tags: ["bug", "regression"]
      components: ["API"]
    description_template: |
      ## Steps to reproduce
      {input.steps}
      ## Expected
      {input.expected}
      ## Actual
      {input.actual}
    rules:
      - "Always include reproduction steps"
```

### Team Directory

Edit `config/team.yaml` to enable smart assignee suggestions:

```yaml
team:
  - login: "user3370"
    name: "Ivan Ivanov"
    role: "Backend developer"
    areas: ["API", "auth", "databases"]
    queues: ["DEV"]
    notes: "Tech lead"
```

## Query Language Examples

```
# My open tasks
Assignee: me() Resolution: empty()

# Critical bugs
Type: bug Priority: Critical, Blocker Resolution: empty()

# Overdue tasks
Deadline: <today() Resolution: empty()

# Updated this week
Updated: >today()-1w Queue: DEV

# Tasks in sprint
Sprint: "Sprint 24" Resolution: empty()
```

## Development

```bash
git clone https://github.com/keemor/ya-tracker-mcp.git
cd ya-tracker-mcp
uv sync

# Run locally
YA_TRACKER_TOKEN=... YA_TRACKER_ORG_ID=... uv run ya-tracker-mcp
```

## License

MIT
