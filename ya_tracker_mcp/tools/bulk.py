import json

from fastmcp import FastMCP, Context


def register_bulk_tools(mcp: FastMCP):

    @mcp.tool()
    async def bulk_update(
        ctx: Context,
        issues: list[str],
        values: dict,
        notify: bool | None = None,
    ) -> str:
        """Bulk update multiple issues at once.

        Args:
            issues: List of issue keys (e.g. ["DEV-1", "DEV-2"])
            values: Dict of fields to update (e.g. {"priority": "critical", "tags": {"add": ["urgent"]}})
            notify: Send notifications
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if notify is not None:
            kwargs["notify"] = notify

        result = await tracker.issues.bulk.update(issues, values, **kwargs)
        bulk_id = result.get("id", "?") if isinstance(result, dict) else "?"
        return f"Bulk update started. ID: {bulk_id}. Use get_bulk_status to check progress."

    @mcp.tool()
    async def bulk_move(
        ctx: Context,
        queue: str,
        issues: list[str],
        move_all_fields: bool | None = None,
        notify: bool | None = None,
    ) -> str:
        """Bulk move issues to another queue.

        Args:
            queue: Target queue key (e.g. "SUPPORT")
            issues: List of issue keys to move
            move_all_fields: Keep all fields when moving
            notify: Send notifications
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if move_all_fields is not None:
            kwargs["move_all_fields"] = move_all_fields
        if notify is not None:
            kwargs["notify"] = notify

        result = await tracker.issues.bulk.move(queue, issues, **kwargs)
        bulk_id = result.get("id", "?") if isinstance(result, dict) else "?"
        return f"Bulk move started. ID: {bulk_id}. Use get_bulk_status to check progress."

    @mcp.tool()
    async def bulk_transition(
        ctx: Context,
        transition: str,
        issues: list[str],
        values: dict | None = None,
        notify: bool | None = None,
    ) -> str:
        """Bulk transition issues to a new status.

        Args:
            transition: Transition ID to execute
            issues: List of issue keys
            values: Optional field updates during transition
            notify: Send notifications
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if values is not None:
            kwargs["values"] = values
        if notify is not None:
            kwargs["notify"] = notify

        result = await tracker.issues.bulk.transition(transition, issues, **kwargs)
        bulk_id = result.get("id", "?") if isinstance(result, dict) else "?"
        return f"Bulk transition started. ID: {bulk_id}. Use get_bulk_status to check progress."

    @mcp.tool()
    async def get_bulk_status(
        ctx: Context,
        bulk_change_id: str,
        output_format: str = "text",
    ) -> str:
        """Check the status of a bulk operation.

        Args:
            bulk_change_id: Bulk operation ID (from bulk_update/bulk_move/bulk_transition)
            output_format: Response format: "text" (default, markdown) or "json"
        """
        tracker = ctx.lifespan_context["tracker"]
        result = await tracker.issues.bulk.get_status(bulk_change_id)

        if output_format == "json":
            return json.dumps(result, ensure_ascii=False, default=str)

        status = result.get("status", "?") if isinstance(result, dict) else str(result)
        total = result.get("totalCount", "?") if isinstance(result, dict) else "?"
        done = result.get("doneCount", "?") if isinstance(result, dict) else "?"
        failed = result.get("failedCount", 0) if isinstance(result, dict) else 0

        line = f"Bulk operation {bulk_change_id}: {status} ({done}/{total})"
        if failed:
            line += f", {failed} failed"
        return line

    @mcp.tool()
    async def get_bulk_failed_issues(
        ctx: Context,
        bulk_change_id: str,
        output_format: str = "text",
    ) -> str:
        """Get list of issues that failed in a bulk operation.

        Args:
            bulk_change_id: Bulk operation ID
            output_format: Response format: "text" (default, markdown) or "json"
        """
        tracker = ctx.lifespan_context["tracker"]
        result = await tracker.issues.bulk.get_failed_issues(bulk_change_id)

        if not result:
            if output_format == "json":
                return "[]"
            return f"No failed issues in bulk operation {bulk_change_id}."

        if output_format == "json":
            return json.dumps(result, ensure_ascii=False, default=str)

        lines = [f"Failed issues in bulk {bulk_change_id}:\n"]
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    key = item.get("key", item.get("id", "?"))
                    errors = item.get("errors", [])
                    lines.append(f"- {key}: {errors}")
                else:
                    lines.append(f"- {item}")
        else:
            lines.append(str(result))
        return "\n".join(lines)
