# ya-tracker-mcp

MCP server for [Yandex Tracker](https://tracker.yandex.ru/) API. Provides 68 tools for managing issues, projects, boards, sprints, worklog and more through the [Model Context Protocol](https://modelcontextprotocol.io/).

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

## Tools (68)

### Issues
| Tool | Description |
|------|-------------|
| `create_issue` | Create issue (queue, summary, type, priority, assignee...) |
| `get_issue` | Get issue details with optional expand (transitions, attachments) |
| `update_issue` | Update issue fields |
| `search_issues` | Search with query language or filters |
| `count_issues` | Count matching issues |
| `move_issue` | Move to another queue |

### Comments
| Tool | Description |
|------|-------------|
| `add_comment` | Add comment with optional summonees |
| `list_comments` | List issue comments |
| `update_comment` | Update comment text |
| `delete_comment` | Delete comment |

### Status Transitions
| Tool | Description |
|------|-------------|
| `list_transitions` | List available transitions |
| `transition_issue` | Execute status transition |

### Links
| Tool | Description |
|------|-------------|
| `link_issues` | Create link (relates, depends on, subtask, epic...) |
| `list_links` | List issue links |
| `delete_link` | Delete link |

### Entities (Projects / Portfolios / Goals)
| Tool | Description |
|------|-------------|
| `create_entity` | Create project, portfolio, or goal |
| `get_entity` | Get entity with fields |
| `update_entity` | Update entity |
| `delete_entity` | Delete entity |
| `search_entities` | Search entities |

### Boards & Sprints
| Tool | Description |
|------|-------------|
| `list_boards` | List all boards |
| `get_board` | Board details |
| `list_board_columns` | Board columns with statuses |
| `list_sprints` | Board sprints |
| `create_sprint` | Create sprint |

### Worklog
| Tool | Description |
|------|-------------|
| `add_worklog` | Log time (ISO 8601 duration) |
| `list_worklog` | List worklog entries |
| `update_worklog` | Update entry |
| `delete_worklog` | Delete entry |

### Checklists
| Tool | Description |
|------|-------------|
| `list_checklist` | List checklist items |
| `add_checklist_item` | Add item |
| `update_checklist_item` | Update item (text, checked, assignee) |
| `delete_checklist_item` | Delete item |

### Attachments
| Tool | Description |
|------|-------------|
| `list_attachments` | List attachments |
| `delete_attachment` | Delete attachment |

### Queues
| Tool | Description |
|------|-------------|
| `list_queues` | List all queues |
| `get_queue` | Queue details (expand: components, versions) |

### Users
| Tool | Description |
|------|-------------|
| `get_myself` | Current user info |
| `list_users` | Organization users |

### Directories (Reference Data)
| Tool | Description |
|------|-------------|
| `list_issue_types` | All issue types |
| `list_statuses` | All statuses |
| `list_priorities` | All priorities |
| `list_resolutions` | All resolutions |
| `list_global_fields` | Global fields |
| `list_queue_fields` | Queue fields (including local) |
| `list_queue_tags` | Queue tags |
| `list_components` | All components |

### Automations
| Tool | Description |
|------|-------------|
| `list_macros` / `get_macro` | Queue macros |
| `list_triggers` / `get_trigger` | Queue triggers |
| `list_autoactions` / `get_autoaction` | Queue autoactions |

### Bulk Operations
| Tool | Description |
|------|-------------|
| `bulk_update` | Update multiple issues |
| `bulk_move` | Move issues to queue |
| `bulk_transition` | Transition multiple issues |
| `get_bulk_status` | Check operation status |

### Import
| Tool | Description |
|------|-------------|
| `import_issue` | Import with original dates/author |
| `import_comment` | Import comment |
| `import_link` | Import link |

### Overviews (Aggregated Reports)
| Tool | Description |
|------|-------------|
| `issue_overview` | Full issue summary (status, links, comments, checklist, worklog) |
| `queue_overview` | Queue summary (open count, top priority issues) |

### Presets
| Tool | Description |
|------|-------------|
| `list_presets` | Available task presets |
| `get_preset` | Preset details (params, template, rules) |
| `create_from_preset` | Create issue from preset |

### Team Directory
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

Edit `config/presets.yaml` to define task templates:

```yaml
presets:
  bug_report:
    name: "Bug report"
    description: "Bug with reproduction steps"
    params:
      type: "bug"
      priority: "critical"
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
