from fastmcp import FastMCP, Context


def register_worklog_tools(mcp: FastMCP):

    @mcp.tool()
    async def add_worklog(
        ctx: Context,
        issue_key: str,
        start: str,
        duration: str,
        comment: str | None = None,
    ) -> str:
        """Add a worklog entry to an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            start: Start time (YYYY-MM-DDThh:mm:ss.sss+hhmm)
            duration: Duration in ISO 8601 (e.g. "PT2H30M", "P1D", "PT45M")
            comment: Optional comment
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if comment is not None:
            kwargs["comment"] = comment

        entry = await tracker.worklog.create(issue_key, start, duration, **kwargs)
        return _format_worklog(entry, issue_key)

    @mcp.tool()
    async def list_worklog(
        ctx: Context,
        issue_key: str,
    ) -> str:
        """List worklog entries for an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
        """
        tracker = ctx.lifespan_context["tracker"]
        entries = await tracker.worklog.list(issue_key)

        if not entries:
            return f"No worklog entries for {issue_key}."

        lines = [f"Worklog for {issue_key} ({len(entries)}):\n"]
        for e in entries:
            lines.append(_format_worklog(e, issue_key))
        return "\n".join(lines)

    @mcp.tool()
    async def update_worklog(
        ctx: Context,
        issue_key: str,
        worklog_id: str,
        duration: str,
        comment: str | None = None,
    ) -> str:
        """Update a worklog entry.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            worklog_id: Worklog entry ID
            duration: New duration in ISO 8601 (e.g. "PT3H")
            comment: New comment
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if comment is not None:
            kwargs["comment"] = comment

        entry = await tracker.worklog.update(issue_key, worklog_id, duration, **kwargs)
        return _format_worklog(entry, issue_key)

    @mcp.tool()
    async def delete_worklog(
        ctx: Context,
        issue_key: str,
        worklog_id: str,
    ) -> str:
        """Delete a worklog entry.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            worklog_id: Worklog entry ID
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.worklog.delete(issue_key, worklog_id)
        return f"Worklog {worklog_id} deleted from {issue_key}."

    @mcp.tool()
    async def search_worklog(
        ctx: Context,
        created_by: str | None = None,
        created_at_from: str | None = None,
        created_at_to: str | None = None,
    ) -> str:
        """Search worklog entries across all issues.

        Args:
            created_by: Filter by author login
            created_at_from: Start date (YYYY-MM-DD or ISO 8601)
            created_at_to: End date (YYYY-MM-DD or ISO 8601)
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if created_by is not None:
            kwargs["created_by"] = created_by
        if created_at_from is not None:
            kwargs["created_at_from"] = created_at_from
        if created_at_to is not None:
            kwargs["created_at_to"] = created_at_to

        entries = await tracker.worklog.search(**kwargs)

        if not entries:
            return "No worklog entries found."

        lines = [f"Worklog entries ({len(entries)}):\n"]
        for entry in entries:
            wid = entry.get("id", "?")
            issue = entry.get("issue", {})
            issue_key = issue.get("key", "?") if isinstance(issue, dict) else str(issue)
            duration = entry.get("duration", "?")
            start = entry.get("start", "")
            comment = entry.get("comment", "")
            author = entry.get("createdBy", {})
            if isinstance(author, dict):
                author = author.get("display", "?")
            line = f"- [{wid}] {issue_key}: {duration} by {author} at {start}"
            if comment:
                line += f" — {comment[:100]}"
            lines.append(line)
        return "\n".join(lines)


def _format_worklog(entry: dict, issue_key: str) -> str:
    wid = entry.get("id", "?")
    duration = entry.get("duration", "?")
    start = entry.get("start", "")
    comment = entry.get("comment", "")
    author = entry.get("createdBy", {})
    if isinstance(author, dict):
        author = author.get("display", author.get("id", "?"))

    line = f"- [{wid}] {duration} by {author} at {start}"
    if comment:
        line += f" — {comment[:100]}"
    return line
