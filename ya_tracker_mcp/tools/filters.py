from fastmcp import FastMCP, Context


def register_filter_tools(mcp: FastMCP):

    @mcp.tool()
    async def create_filter(
        ctx: Context,
        name: str,
        query: str | None = None,
        filter: dict | None = None,
    ) -> str:
        """Create a saved filter.

        Args:
            name: Filter name
            query: Query string (e.g. 'Queue: DEV Resolution: empty()')
            filter: Filter as dict (e.g. {"queue": "DEV", "status": "open"})
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if query is not None:
            kwargs["query"] = query
        if filter is not None:
            kwargs["filter"] = filter

        result = await tracker.filters.create(name, **kwargs)
        fid = result.get("id", "?")
        fname = result.get("name", name)
        return f"Filter created: [{fid}] {fname}"

    @mcp.tool()
    async def get_filter(
        ctx: Context,
        filter_id: str,
    ) -> str:
        """Get a saved filter by ID.

        Args:
            filter_id: Filter ID
        """
        tracker = ctx.lifespan_context["tracker"]
        f = await tracker.filters.get(filter_id)

        fid = f.get("id", "?")
        name = f.get("name", "")
        query = f.get("query", "")
        owner = f.get("owner", {})
        if isinstance(owner, dict):
            owner = owner.get("display", "?")

        lines = [
            f"**[{fid}] {name}**",
            f"Owner: {owner}",
        ]
        if query:
            lines.append(f"Query: {query}")
        flt = f.get("filter", {})
        if flt:
            lines.append(f"Filter: {flt}")
        return "\n".join(lines)

    @mcp.tool()
    async def update_filter(
        ctx: Context,
        filter_id: str,
        name: str | None = None,
        query: str | None = None,
        filter: dict | None = None,
    ) -> str:
        """Update a saved filter.

        Args:
            filter_id: Filter ID
            name: New filter name
            query: New query string
            filter: New filter dict
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if query is not None:
            kwargs["query"] = query
        if filter is not None:
            kwargs["filter"] = filter

        if not kwargs:
            return "No fields to update."

        result = await tracker.filters.update(filter_id, **kwargs)
        fname = result.get("name", "?")
        return f"Filter updated: [{filter_id}] {fname}"
