from fastmcp import FastMCP, Context


def register_board_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_boards(ctx: Context) -> str:
        """List all boards."""
        tracker = ctx.lifespan_context["tracker"]
        boards = await tracker.boards.list()

        if not boards:
            return "No boards found."

        lines = [f"Boards ({len(boards)}):\n"]
        for b in boards:
            bid = b.get("id", "?")
            name = b.get("name", "")
            lines.append(f"- [{bid}] {name}")
        return "\n".join(lines)

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
    ) -> str:
        """List sprints of a board.

        Args:
            board_id: Board ID
        """
        tracker = ctx.lifespan_context["tracker"]
        sprints = await tracker.boards.sprints.list(board_id)

        if not sprints:
            return f"No sprints for board {board_id}."

        lines = [f"Sprints for board {board_id} ({len(sprints)}):\n"]
        for s in sprints:
            sid = s.get("id", "?")
            name = s.get("name", "")
            start = s.get("startDate", "")
            end = s.get("endDate", "")
            status = s.get("status", "")
            lines.append(f"- [{sid}] {name} ({start} — {end}) [{status}]")
        return "\n".join(lines)

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
                if isinstance(s, dict):
                    status_names.append(s.get("display", s.get("key", "?")))
                else:
                    status_names.append(str(s))
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
        if columns is not None:
            kwargs["columns"] = columns
        if sprints_available is not None:
            kwargs["sprints_available"] = sprints_available
        if backlog_available is not None:
            kwargs["backlog_available"] = backlog_available
        if board_permissions_template is not None:
            kwargs["board_permissions_template"] = board_permissions_template

        board = await tracker.boards.create(name, **kwargs)
        return _format_board(board)

    @mcp.tool()
    async def update_board(
        ctx: Context,
        board_id: int,
        name: str | None = None,
        columns: list[dict] | None = None,
        sprints_available: bool | None = None,
        backlog_available: bool | None = None,
    ) -> str:
        """Update board settings.

        Args:
            board_id: Board ID
            name: New board name
            columns: New columns config
            sprints_available: Enable/disable sprints
            backlog_available: Enable/disable backlog
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if columns is not None:
            kwargs["columns"] = columns
        if sprints_available is not None:
            kwargs["sprints_available"] = sprints_available
        if backlog_available is not None:
            kwargs["backlog_available"] = backlog_available

        if not kwargs:
            return "No fields to update."

        board = await tracker.boards.update(board_id, **kwargs)
        return _format_board(board)

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
        return f"Board {board_id} deleted."

    @mcp.tool()
    async def get_sprint(
        ctx: Context,
        sprint_id: int,
    ) -> str:
        """Get sprint details.

        Args:
            sprint_id: Sprint ID
        """
        tracker = ctx.lifespan_context["tracker"]
        sprint = await tracker.boards.sprints.get(sprint_id)
        sid = sprint.get("id", "?")
        name = sprint.get("name", "")
        status = sprint.get("status", "")
        start = sprint.get("startDate", "")
        end = sprint.get("endDate", "")
        board = sprint.get("board", {})
        board_id = board.get("id", "?") if isinstance(board, dict) else board
        return f"**Sprint [{sid}]**: {name}\nStatus: {status}\nPeriod: {start} — {end}\nBoard: {board_id}"

    @mcp.tool()
    async def create_board_column(
        ctx: Context,
        board_id: int,
        name: str,
        statuses: list[str],
    ) -> str:
        """Create a column on a board.

        Args:
            board_id: Board ID
            name: Column name
            statuses: List of status keys for this column
        """
        tracker = ctx.lifespan_context["tracker"]
        column = await tracker.boards.columns.create(board_id, name, statuses)
        cid = column.get("id", "?")
        return f"Column created: [{cid}] {name} on board {board_id}"

    @mcp.tool()
    async def update_board_column(
        ctx: Context,
        board_id: int,
        column_id: int,
        name: str | None = None,
        statuses: list[str] | None = None,
    ) -> str:
        """Update a board column.

        Args:
            board_id: Board ID
            column_id: Column ID
            name: New column name
            statuses: New list of status keys
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if statuses is not None:
            kwargs["statuses"] = statuses

        if not kwargs:
            return "No fields to update."

        column = await tracker.boards.columns.update(board_id, column_id, **kwargs)
        return f"Column [{column_id}] updated on board {board_id}."

    @mcp.tool()
    async def delete_board_column(
        ctx: Context,
        board_id: int,
        column_id: int,
    ) -> str:
        """Delete a column from a board.

        Args:
            board_id: Board ID
            column_id: Column ID
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.boards.columns.delete(board_id, column_id)
        return f"Column [{column_id}] deleted from board {board_id}."


def _format_board(board: dict) -> str:
    bid = board.get("id", "?")
    name = board.get("name", "")
    owner = board.get("owner", {})
    if isinstance(owner, dict):
        owner = owner.get("display", owner.get("id", "?"))

    lines = [
        f"**Board [{bid}]**: {name}",
        f"Owner: {owner}",
    ]

    if board.get("sprintsAvailable"):
        lines.append("Sprints: enabled")
    if board.get("backlogAvailable"):
        lines.append("Backlog: enabled")

    columns = board.get("columns", [])
    if columns:
        col_names = [c.get("name", "?") if isinstance(c, dict) else str(c) for c in columns]
        lines.append(f"Columns: {' -> '.join(col_names)}")

    return "\n".join(lines)
