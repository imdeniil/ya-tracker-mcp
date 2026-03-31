import json
from fastmcp import FastMCP, Context
from ..utils.formatters import format_mcp_item, format_mcp_list


def register_worklog_tools(mcp: FastMCP):

    @mcp.tool()
    async def add_worklog(
        ctx: Context,
        issue_key: str,
        start: str,
        duration: str,
        comment: str | None = None,
        fields: list[str] | None = None,
        output_format: str = "text",
        full_description: bool = False,
    ) -> str:
        """Add a worklog entry to an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            start: Start time (YYYY-MM-DDThh:mm:ss.sss+hhmm)
            duration: Duration in ISO 8601 (e.g. "PT2H30M", "P1D", "PT45M")
            comment: Optional comment
            fields: Optional list of fields to show in response.
            output_format: Response format: "text" (default, markdown) or "json"
            full_description: If true, do not truncate description (default false)
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if comment is not None:
            kwargs["comment"] = comment

        entry = await tracker.worklog.create(issue_key, start, duration, **kwargs)
        return _format_worklog_full(entry, fields, output_format=output_format, full_description=full_description)

    @mcp.tool()
    async def list_worklog(
        ctx: Context,
        issue_key: str,
        fields: list[str] | None = None,
        output_format: str = "text",
    ) -> str:
        """List worklog entries for an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            fields: Optional list of fields to show.
            output_format: Response format: "text" (default, markdown) or "json"
        """
        tracker = ctx.lifespan_context["tracker"]
        entries = await tracker.worklog.list(issue_key)

        return format_mcp_list(
            entries, f"Worklog for {issue_key}",
            basic_fields=["duration", "createdBy", "start"],
            extra_fields=fields,
            name_field="comment",
            template="- [{key}] {basics}: {name}",
            output_format=output_format,
        )

    @mcp.tool()
    async def update_worklog(
        ctx: Context,
        issue_key: str,
        worklog_id: str,
        duration: str,
        comment: str | None = None,
        fields: list[str] | None = None,
        output_format: str = "text",
        full_description: bool = False,
    ) -> str:
        """Update a worklog entry.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            worklog_id: Worklog entry ID
            duration: New duration in ISO 8601 (e.g. "PT3H")
            comment: New comment
            fields: Optional list of fields to show in response.
            output_format: Response format: "text" (default, markdown) or "json"
            full_description: If true, do not truncate description (default false)
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if comment is not None:
            kwargs["comment"] = comment

        entry = await tracker.worklog.update(issue_key, worklog_id, duration, **kwargs)
        return _format_worklog_full(entry, fields, output_format=output_format, full_description=full_description)

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
        fields: list[str] | None = None,
        output_format: str = "text",
    ) -> str:
        """Search worklog entries across all issues.

        Args:
            created_by: Filter by author login
            created_at_from: Start date (YYYY-MM-DD or ISO 8601)
            created_at_to: End date (YYYY-MM-DD or ISO 8601)
            fields: Optional list of additional fields to show.
            output_format: Response format: "text" (default, markdown) or "json"
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

        return format_mcp_list(
            entries, "Worklog entries",
            basic_fields=["issue", "duration", "createdBy", "start"],
            extra_fields=fields,
            name_field="comment",
            template="- [{key}] {basics}: {name}",
            output_format=output_format,
        )


def _format_worklog_full(
    entry: dict,
    extra_fields: list[str] | None = None,
    output_format: str = "text",
    full_description: bool = False,
) -> str:
    return format_mcp_item(
        entry, "Worklog",
        basic_fields=["duration", "createdBy", "start"],
        extra_fields=extra_fields,
        name_field="comment",
        template="[{key}] {basics}: {name}",
        description_field=None,
        output_format=output_format,
        full_description=full_description,
    )
