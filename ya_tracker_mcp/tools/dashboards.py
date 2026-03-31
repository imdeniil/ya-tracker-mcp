import json

from fastmcp import FastMCP, Context


def register_dashboard_tools(mcp: FastMCP):

    @mcp.tool()
    async def create_dashboard(
        ctx: Context,
        name: str,
        layout: str | None = None,
        owner: str | None = None,
        output_format: str = "text",
    ) -> str:
        """Create a dashboard.

        Args:
            name: Dashboard name
            layout: Layout type
            owner: Owner login
            output_format: Response format: "text" (default, markdown) or "json"
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if layout is not None:
            kwargs["layout"] = layout
        if owner is not None:
            kwargs["owner"] = owner

        result = await tracker.dashboards.create(name, **kwargs)
        if output_format == "json":
            return json.dumps(result, ensure_ascii=False, default=str)
        did = result.get("id", "?")
        return f"Dashboard created: [{did}] {name}"

    @mcp.tool()
    async def create_cycle_time_widget(
        ctx: Context,
        dashboard_id: str,
        description: str,
        query: str | None = None,
        filter_id: str | None = None,
        output_format: str = "text",
    ) -> str:
        """Create a cycle time widget on a dashboard.

        Args:
            dashboard_id: Dashboard ID
            description: Widget description
            query: Query string for filtering issues
            filter_id: Filter ID for filtering issues
            output_format: Response format: "text" (default, markdown) or "json"
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if query is not None:
            kwargs["query"] = query
        if filter_id is not None:
            kwargs["filter_id"] = filter_id

        result = await tracker.dashboards.create_cycle_time_widget(
            dashboard_id, description, **kwargs
        )
        if output_format == "json":
            return json.dumps(result, ensure_ascii=False, default=str)
        wid = result.get("id", "?")
        return f"Cycle time widget created: [{wid}] on dashboard {dashboard_id}"
