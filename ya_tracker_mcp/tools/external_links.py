from fastmcp import FastMCP, Context


def register_external_link_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_external_applications(ctx: Context) -> str:
        """List external applications registered for issue linking."""
        tracker = ctx.lifespan_context["tracker"]
        apps = await tracker.external.links.get_applications()

        if not apps:
            return "No external applications found."

        lines = ["External applications:\n"]
        for app in apps:
            aid = app.get("id", "?")
            name = app.get("name", "")
            lines.append(f"- [{aid}] {name}")
        return "\n".join(lines)

    @mcp.tool()
    async def list_external_links(
        ctx: Context,
        issue_key: str,
    ) -> str:
        """List external links of an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
        """
        tracker = ctx.lifespan_context["tracker"]
        links = await tracker.external.links.list(issue_key)

        if not links:
            return f"No external links for {issue_key}."

        lines = [f"External links for {issue_key}:\n"]
        for link in links:
            lid = link.get("id", "?")
            rel = link.get("relationship", "?")
            key = link.get("key", "")
            url = link.get("object", {}).get("url", "") if isinstance(link.get("object"), dict) else ""
            lines.append(f"- [{lid}] {rel}: {key} {url}")
        return "\n".join(lines)

    @mcp.tool()
    async def create_external_link(
        ctx: Context,
        issue_key: str,
        relationship: str,
        key: str,
        origin: str,
        backlink: str | None = None,
    ) -> str:
        """Create an external link on an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            relationship: Relationship type
            key: External object key
            origin: External application ID
            backlink: URL for backlink
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if backlink is not None:
            kwargs["backlink"] = backlink

        result = await tracker.external.links.create(
            issue_key, relationship, key, origin, **kwargs
        )
        lid = result.get("id", "?")
        return f"External link created: [{lid}] on {issue_key}"

    @mcp.tool()
    async def delete_external_link(
        ctx: Context,
        issue_key: str,
        link_id: str,
    ) -> str:
        """Delete an external link from an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            link_id: External link ID
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.external.links.delete(issue_key, link_id)
        return f"External link {link_id} deleted from {issue_key}."
