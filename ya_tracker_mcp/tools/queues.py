from fastmcp import FastMCP, Context


def register_queue_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_queues(
        ctx: Context,
        per_page: int | None = None,
    ) -> str:
        """List all available queues.

        Args:
            per_page: Results per page
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if per_page is not None:
            kwargs["per_page"] = per_page

        queues = await tracker.queues.list(**kwargs)

        if not queues:
            return "No queues found."

        lines = [f"Queues ({len(queues)}):\n"]
        for q in queues:
            key = q.get("key", "?")
            name = q.get("name", "")
            lead = q.get("lead", {})
            if isinstance(lead, dict):
                lead = lead.get("display", lead.get("id", "?"))
            lines.append(f"- **{key}** — {name} (lead: {lead})")
        return "\n".join(lines)

    @mcp.tool()
    async def get_queue(
        ctx: Context,
        queue_key: str,
        expand: str | None = None,
    ) -> str:
        """Get queue details.

        Args:
            queue_key: Queue key (e.g. "DEV")
            expand: Expand: "projects", "components", "versions", "all"
        """
        tracker = ctx.lifespan_context["tracker"]
        queue = await tracker.queues.get(queue_key, expand=expand)
        return _format_queue(queue)


def _format_queue(queue: dict) -> str:
    key = queue.get("key", "?")
    name = queue.get("name", "")
    lead = queue.get("lead", {})
    if isinstance(lead, dict):
        lead = lead.get("display", lead.get("id", "?"))
    description = queue.get("description", "")
    default_type = _extract_display(queue.get("defaultType"))
    default_priority = _extract_display(queue.get("defaultPriority"))

    lines = [
        f"**{key}** — {name}",
        f"Lead: {lead}",
        f"Default type: {default_type} | Default priority: {default_priority}",
    ]

    if description:
        lines.append(f"Description: {description}")

    # Components
    components = queue.get("components", [])
    if components:
        comp_names = [c.get("name", "?") if isinstance(c, dict) else str(c) for c in components]
        lines.append(f"Components: {', '.join(comp_names)}")

    # Versions
    versions = queue.get("versions", [])
    if versions:
        ver_names = [v.get("name", "?") if isinstance(v, dict) else str(v) for v in versions]
        lines.append(f"Versions: {', '.join(ver_names)}")

    return "\n".join(lines)


def _extract_display(obj) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return obj.get("display", obj.get("name", obj.get("key", str(obj))))
    return str(obj)
