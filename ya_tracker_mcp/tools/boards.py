from fastmcp import FastMCP, Context
from ..utils.directory_manager import manager
from ..utils.formatters import format_mcp_list


def register_board_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_boards(
        ctx: Context,
        fields: list[str] | None = None,
        use_cache: bool = True,
    ) -> str:
        """List all boards.

        Args:
            fields: Optional list of additional fields (e.g. ["owner", "sprintsAvailable"])
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        boards = await manager.get("boards", tracker.boards.list, force=not use_cache)

        return format_mcp_list(
            boards, "Boards",
            basic_fields=[],
            extra_fields=fields
        )

    @mcp.tool()
    async def get_board(
        ctx: Context,
        board_id: int,
    ) -> str:
        """Get board details.

        Args:
            board_id: Board ID
        """
        tracker = ctx.lifespan_context["tracker"]
        board = await tracker.boards.get(board_id)
        return _format_board(board)

    @mcp.tool()
    async def list_sprints(
        ctx: Context,
        board_id: int,
        fields: list[str] | None = None,
        use_cache: bool = True,
    ) -> str:
        """List sprints of a board.

        Args:
            board_id: Board ID
            fields: Optional list of additional fields
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        
        sprints = await manager.get(
            "sprints",
            lambda: tracker.boards.sprints.list(board_id),
            scope=str(board_id),
            force=not use_cache
        )

        return format_mcp_list(
            sprints, f"Sprints for board {board_id}",
            basic_fields=["startDate", "endDate", "status"],
            extra_fields=fields,
            template="- [{key}] **{name}** ({basics})"
        )

    @mcp.tool()
    async def create_sprint(
        ctx: Context,
        name: str,
        board_id: int,
        start_date: str,
        end_date: str,
    ) -> str:
        """Create a new sprint.

        Args:
            name: Sprint name
            board_id: Board ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        tracker = ctx.lifespan_context["tracker"]
        sprint = await tracker.boards.sprints.create(
            name, board_id, start_date, end_date
        )

        sid = sprint.get("id", "?")
        
        # Invalidate sprints cache for this board
        await manager.get(
            "sprints",
            lambda: tracker.boards.sprints.list(board_id),
            scope=str(board_id),
            force=True
        )
        
        return f"Sprint [{sid}] '{name}' created ({start_date} — {end_date})."

    @mcp.tool()
    async def list_board_columns(
        ctx: Context,
        board_id: int,
    ) -> str:
        """List columns of a board.

        Args:
            board_id: Board ID
        """
        tracker = ctx.lifespan_context["tracker"]
        columns = await tracker.boards.columns.list(board_id)

        if not columns:
            return f"No columns for board {board_id}."

        lines = [f"Columns for board {board_id} ({len(columns)}):\n"]
        for c in columns:
            cid = c.get("id", "?")
            name = c.get("name", "")
            statuses = c.get("statuses", [])
            status_names = []
            for s in statuses:
                from ..utils.formatters import _extract_display
                status_names.append(_extract_display(s))
            lines.append(f"- [{cid}] {name}: {', '.join(status_names) if status_names else '-'}")
        return "\n".join(lines)

    @mcp.tool()
    async def create_board(
        ctx: Context,
        name: str,
        columns: list[dict] | None = None,
        sprints_available: bool | None = None,
        backlog_available: bool | None = None,
        board_permissions_template: str | None = None,
    ) -> str:
        """Create a new board.

        Args:
            name: Board name
            columns: Columns config (list of dicts with name and statuses)
            sprints_available: Enable sprints (Scrum)
            backlog_available: Enable backlog
            board_permissions_template: Permission template ("private", etc.)
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if columns: kwargs["columns"] = columns
        if sprints_available is not None: kwargs["sprints_available"] = sprints_available
        if backlog_available is not None: kwargs["backlog_available"] = backlog_available
        if board_permissions_template: kwargs["board_permissions_template"] = board_permissions_template

        board = await tracker.boards.create(name=name, **kwargs)
        
        # Invalidate boards cache
        await manager.get("boards", tracker.boards.list, force=True)
        
        return _format_board(board)

    @mcp.tool()
    async def update_board(
        ctx: Context,
        board_id: int,
        name: str | None = None,
        sprints_available: bool | None = None,
        backlog_available: bool | None = None,
    ) -> str:
        """Update an existing board.

        Args:
            board_id: Board ID
            name: New board name
            sprints_available: Enable sprints
            backlog_available: Enable backlog
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name: kwargs["name"] = name
        if sprints_available is not None: kwargs["sprints_available"] = sprints_available
        if backlog_available is not None: kwargs["backlog_available"] = backlog_available

        if not kwargs:
            return "No fields to update."

        board = await tracker.boards.update(board_id, **kwargs)
        
        # Invalidate boards cache
        await manager.get("boards", tracker.boards.list, force=True)
        
        return f"Board [{board_id}] updated."

    @mcp.tool()
    async def delete_board(
        ctx: Context,
        board_id: int,
    ) -> str:
        """Delete a board.

        Args:
            board_id: Board ID
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.boards.delete(board_id)
        
        # Invalidate boards cache
        await manager.get("boards", tracker.boards.list, force=True)
        
        return f"Board [{board_id}] deleted."


def _format_board(b: dict) -> str:
    bid = b.get("id", "?")
    name = b.get("name", "")
    lines = [f"**Board [{bid}]**: {name}"]
    
    # Optional fields
    if "sprintsAvailable" in b:
        lines.append(f"Sprints enabled: {b['sprintsAvailable']}")
    if "backlogAvailable" in b:
        lines.append(f"Backlog enabled: {b['backlogAvailable']}")
        
    lines.append(f"\nhttps://tracker.yandex.ru/manager/boards/{bid}")
    return "\n".join(lines)
