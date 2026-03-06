from fastmcp import FastMCP, Context


def register_link_tools(mcp: FastMCP):

    @mcp.tool()
    async def link_issues(
        ctx: Context,
        issue_key: str,
        relationship: str,
        target: str,
    ) -> str:
        """Create a link between two issues.

        Args:
            issue_key: Source issue key (e.g. "DEV-123")
            relationship: Link type - one of: "relates", "depends on", "is dependent by",
                "is subtask for", "is parent task for", "duplicates", "is duplicated by",
                "is epic of", "has epic"
            target: Target issue key (e.g. "DEV-456")
        """
        tracker = ctx.lifespan_context["tracker"]
        link = await tracker.issues.links.create(
            issue_key, relationship, target
        )
        return _format_link(link)

    @mcp.tool()
    async def list_links(
        ctx: Context,
        issue_key: str,
    ) -> str:
        """List all links of an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
        """
        tracker = ctx.lifespan_context["tracker"]
        links = await tracker.issues.links.list(issue_key)

        if not links:
            return f"No links on {issue_key}."

        lines = [f"Links on {issue_key} ({len(links)}):\n"]
        for link in links:
            lines.append(_format_link(link))
        return "\n".join(lines)

    @mcp.tool()
    async def delete_link(
        ctx: Context,
        issue_key: str,
        link_id: str,
    ) -> str:
        """Delete a link from an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            link_id: Link ID
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.issues.links.delete(issue_key, link_id)
        return f"Link {link_id} deleted from {issue_key}."


def _format_link(link: dict) -> str:
    link_id = link.get("id", "?")
    rel_type = link.get("type", {})
    if isinstance(rel_type, dict):
        rel_name = rel_type.get("id", "?")
    else:
        rel_name = str(rel_type)

    direction = link.get("direction", "")

    target = link.get("object", {})
    if isinstance(target, dict):
        target_key = target.get("key", "?")
        target_summary = target.get("display", target.get("summary", ""))
    else:
        target_key = str(target)
        target_summary = ""

    status = ""
    if isinstance(target, dict) and "status" in target:
        s = target["status"]
        status = f" [{s.get('display', s.get('key', ''))}]" if isinstance(s, dict) else f" [{s}]"

    return f"- [{link_id}] {rel_name} {direction} {target_key}{status} {target_summary}"
