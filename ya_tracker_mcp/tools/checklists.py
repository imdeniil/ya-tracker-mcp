import json

from fastmcp import FastMCP, Context


def register_checklist_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_checklist(
        ctx: Context,
        issue_key: str,
        output_format: str = "text",
    ) -> str:
        """List checklist items of an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            output_format: Response format: "text" (default, markdown) or "json"
        """
        tracker = ctx.lifespan_context["tracker"]
        items = await tracker.issues.checklists.list(issue_key)

        if not items:
            if output_format == "json":
                return "[]"
            return f"No checklist items on {issue_key}."

        if output_format == "json":
            return json.dumps(items, ensure_ascii=False, default=str)

        done = sum(1 for i in items if i.get("checked"))
        lines = [f"Checklist for {issue_key} ({done}/{len(items)}):\n"]
        for item in items:
            iid = item.get("id", "?")
            mark = "x" if item.get("checked") else " "
            text = item.get("text", "?")
            assignee = item.get("assignee")
            if isinstance(assignee, dict):
                assignee = assignee.get("display", "")
            extra = f" @{assignee}" if assignee else ""
            lines.append(f"- [{mark}] [{iid}] {text}{extra}")
        return "\n".join(lines)

    @mcp.tool()
    async def add_checklist_item(
        ctx: Context,
        issue_key: str,
        text: str,
        checked: bool | None = None,
        assignee: str | None = None,
        deadline: str | None = None,
    ) -> str:
        """Add a checklist item to an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            text: Item text
            checked: Whether item is checked
            assignee: Assignee login
            deadline: Deadline date (YYYY-MM-DD)
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if checked is not None:
            kwargs["checked"] = checked
        if assignee is not None:
            kwargs["assignee"] = assignee
        if deadline is not None:
            kwargs["deadline"] = {"date": deadline, "deadlineType": "date"}

        result = await tracker.issues.checklists.create(issue_key, text, **kwargs)

        if isinstance(result, list):
            return f"Checklist item added to {issue_key}. Total items: {len(result)}."
        return f"Checklist item added to {issue_key}."

    @mcp.tool()
    async def update_checklist_item(
        ctx: Context,
        issue_key: str,
        item_id: str,
        text: str | None = None,
        checked: bool | None = None,
        assignee: str | None = None,
        deadline: str | None = None,
    ) -> str:
        """Update a checklist item.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            item_id: Checklist item ID (from list_checklist)
            text: New text
            checked: Mark as checked/unchecked
            assignee: New assignee login
            deadline: New deadline (YYYY-MM-DD)
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if text is not None:
            kwargs["text"] = text
        if checked is not None:
            kwargs["checked"] = checked
        if assignee is not None:
            kwargs["assignee"] = assignee
        if deadline is not None:
            kwargs["deadline"] = {"date": deadline, "deadlineType": "date"}

        await tracker.issues.checklists.item.update(issue_key, item_id, **kwargs)
        return f"Checklist item {item_id} updated on {issue_key}."

    @mcp.tool()
    async def delete_checklist_item(
        ctx: Context,
        issue_key: str,
        item_id: str,
    ) -> str:
        """Delete a single checklist item.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            item_id: Checklist item ID (from list_checklist)
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.issues.checklists.item.delete(issue_key, item_id)
        return f"Checklist item {item_id} deleted from {issue_key}."

    @mcp.tool()
    async def delete_checklist(
        ctx: Context,
        issue_key: str,
    ) -> str:
        """Delete the entire checklist from an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.issues.checklists.delete(issue_key)
        return f"Checklist deleted from {issue_key}."
