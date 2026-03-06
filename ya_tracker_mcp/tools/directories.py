from fastmcp import FastMCP, Context


def register_directory_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_issue_types(ctx: Context) -> str:
        """List all issue types in the organization."""
        tracker = ctx.lifespan_context["tracker"]
        types = await tracker.issues.types.list()

        if not types:
            return "No issue types found."

        lines = ["Issue types:\n"]
        for t in types:
            key = t.get("key", "?")
            name = t.get("name", "")
            if isinstance(name, dict):
                name = name.get("ru", name.get("en", str(name)))
            lines.append(f"- **{key}** — {name}")
        return "\n".join(lines)

    @mcp.tool()
    async def list_statuses(ctx: Context) -> str:
        """List all issue statuses in the organization."""
        tracker = ctx.lifespan_context["tracker"]
        statuses = await tracker.issues.statuses.list()

        if not statuses:
            return "No statuses found."

        lines = ["Statuses:\n"]
        for s in statuses:
            key = s.get("key", "?")
            name = s.get("name", "")
            if isinstance(name, dict):
                name = name.get("ru", name.get("en", str(name)))
            stype = s.get("type", "")
            lines.append(f"- **{key}** — {name} (type: {stype})")
        return "\n".join(lines)

    @mcp.tool()
    async def list_priorities(ctx: Context) -> str:
        """List all issue priorities in the organization."""
        tracker = ctx.lifespan_context["tracker"]
        priorities = await tracker.issues.priorities.list()

        if not priorities:
            return "No priorities found."

        lines = ["Priorities:\n"]
        for p in priorities:
            key = p.get("key", "?")
            name = p.get("name", "")
            if isinstance(name, dict):
                name = name.get("ru", name.get("en", str(name)))
            lines.append(f"- **{key}** — {name}")
        return "\n".join(lines)

    @mcp.tool()
    async def list_resolutions(ctx: Context) -> str:
        """List all issue resolutions in the organization."""
        tracker = ctx.lifespan_context["tracker"]
        resolutions = await tracker.issues.resolutions.list()

        if not resolutions:
            return "No resolutions found."

        lines = ["Resolutions:\n"]
        for r in resolutions:
            key = r.get("key", "?")
            name = r.get("name", "")
            if isinstance(name, dict):
                name = name.get("ru", name.get("en", str(name)))
            lines.append(f"- **{key}** — {name}")
        return "\n".join(lines)

    @mcp.tool()
    async def list_queue_fields(
        ctx: Context,
        queue_key: str,
    ) -> str:
        """List fields (including local fields) of a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
        """
        tracker = ctx.lifespan_context["tracker"]
        fields = await tracker.queues.fields.list(queue_key)

        if not fields:
            return f"No fields for queue {queue_key}."

        lines = [f"Fields for queue {queue_key} ({len(fields)}):\n"]
        for f in fields:
            fid = f.get("id", "?")
            name = f.get("name", "")
            if isinstance(name, dict):
                name = name.get("ru", name.get("en", str(name)))
            ftype = f.get("type", "")
            lines.append(f"- **{fid}** — {name} ({ftype})")
        return "\n".join(lines)

    @mcp.tool()
    async def list_queue_tags(
        ctx: Context,
        queue_key: str,
    ) -> str:
        """List tags used in a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
        """
        tracker = ctx.lifespan_context["tracker"]
        tags = await tracker.queues.tags.list(queue_key)

        if not tags:
            return f"No tags in queue {queue_key}."

        return f"Tags in {queue_key}: {', '.join(tags)}"

    @mcp.tool()
    async def list_components(ctx: Context) -> str:
        """List all components in the organization."""
        tracker = ctx.lifespan_context["tracker"]
        components = await tracker.components.list()

        if not components:
            return "No components found."

        lines = ["Components:\n"]
        for c in components:
            cid = c.get("id", "?")
            name = c.get("name", "")
            queue = c.get("queue", {})
            if isinstance(queue, dict):
                queue = queue.get("key", queue.get("display", "?"))
            lead = c.get("lead", {})
            if isinstance(lead, dict):
                lead = lead.get("display", "?")
            lines.append(f"- [{cid}] **{name}** (queue: {queue}, lead: {lead})")
        return "\n".join(lines)

    @mcp.tool()
    async def list_global_fields(ctx: Context) -> str:
        """List all global issue fields."""
        tracker = ctx.lifespan_context["tracker"]
        fields = await tracker.issues.fields.list()

        if not fields:
            return "No global fields found."

        lines = [f"Global fields ({len(fields)}):\n"]
        for f in fields:
            fid = f.get("id", "?")
            name = f.get("name", "")
            if isinstance(name, dict):
                name = name.get("ru", name.get("en", str(name)))
            ftype = f.get("type", "")
            lines.append(f"- **{fid}** — {name} ({ftype})")
        return "\n".join(lines)
