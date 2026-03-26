import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastmcp import FastMCP, Context
from YaTrackerApi import YandexTrackerClient

from ya_tracker_mcp.tools.issues import register_issue_tools
from ya_tracker_mcp.tools.comments import register_comment_tools
from ya_tracker_mcp.tools.links import register_link_tools
from ya_tracker_mcp.tools.transitions import register_transition_tools
from ya_tracker_mcp.tools.queues import register_queue_tools
from ya_tracker_mcp.tools.users import register_user_tools
from ya_tracker_mcp.tools.overviews import register_overview_tools
from ya_tracker_mcp.tools.entities import register_entity_tools
from ya_tracker_mcp.tools.boards import register_board_tools
from ya_tracker_mcp.tools.worklog import register_worklog_tools
from ya_tracker_mcp.tools.checklists import register_checklist_tools
from ya_tracker_mcp.tools.attachments import register_attachment_tools
from ya_tracker_mcp.tools.presets import register_preset_tools
from ya_tracker_mcp.tools.team import register_team_tools
from ya_tracker_mcp.tools.directories import register_directory_tools
from ya_tracker_mcp.tools.automations import register_automation_tools
from ya_tracker_mcp.tools.bulk import register_bulk_tools
from ya_tracker_mcp.tools.imports import register_import_tools
from ya_tracker_mcp.tools.filters import register_filter_tools
from ya_tracker_mcp.tools.dashboards import register_dashboard_tools
from ya_tracker_mcp.tools.external_links import register_external_link_tools
from ya_tracker_mcp.resources.static import register_resources
from ya_tracker_mcp.prompts.prompts import register_prompts


@asynccontextmanager
async def lifespan(mcp: FastMCP) -> AsyncIterator[dict]:
    from ya_tracker_mcp import __version__
    print(f"Starting ya-tracker-mcp v{__version__}")
    
    token = os.environ.get("YA_TRACKER_TOKEN") or os.environ["TRACKER_API_KEY"]
    org_id = os.environ.get("YA_TRACKER_ORG_ID") or os.environ["TRACKER_ORG_ID"]
    async with YandexTrackerClient(oauth_token=token, org_id=org_id) as client:
        yield {"tracker": client}


mcp = FastMCP(
    "Yandex Tracker",
    instructions="MCP server for Yandex Tracker API",
    lifespan=lifespan,
)

register_issue_tools(mcp)
register_comment_tools(mcp)
register_link_tools(mcp)
register_transition_tools(mcp)
register_queue_tools(mcp)
register_user_tools(mcp)
register_overview_tools(mcp)
register_entity_tools(mcp)
register_board_tools(mcp)
register_worklog_tools(mcp)
register_checklist_tools(mcp)
register_attachment_tools(mcp)
register_preset_tools(mcp)
register_team_tools(mcp)
register_directory_tools(mcp)
register_automation_tools(mcp)
register_bulk_tools(mcp)
register_import_tools(mcp)
register_filter_tools(mcp)
register_dashboard_tools(mcp)
register_external_link_tools(mcp)
register_resources(mcp)
register_prompts(mcp)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
