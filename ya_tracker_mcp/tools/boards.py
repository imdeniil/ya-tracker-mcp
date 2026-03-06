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
