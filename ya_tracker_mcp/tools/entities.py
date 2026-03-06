from fastmcp import FastMCP, Context


def register_entity_tools(mcp: FastMCP):

    @mcp.tool()
    async def create_entity(
        ctx: Context,
        entity_type: str,
        summary: str,
        lead: str | None = None,
        description: str | None = None,
        team_access: bool | None = None,
        team_users: list[str] | None = None,
        followers: list[str] | None = None,
        start: str | None = None,
        end: str | None = None,
        tags: list[str] | None = None,
        parent_entity: str | None = None,
        entity_status: str | None = None,
    ) -> str:
        """Create a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            summary: Entity name
            lead: Lead user login
            description: Description (YFM markdown)
            team_access: Restrict access to team members only
            team_users: List of team member logins
            followers: List of follower logins
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            tags: List of tags
            parent_entity: Parent entity ID (as string)
            entity_status: Status (e.g. "in_progress", "draft", "at_risk")
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if lead is not None:
            kwargs["lead"] = lead
        if description is not None:
            kwargs["description"] = description
        if team_access is not None:
            kwargs["team_access"] = team_access
        if team_users is not None:
            kwargs["team_users"] = team_users
        if followers is not None:
            kwargs["followers"] = followers
        if start is not None:
            kwargs["start"] = start
        if end is not None:
            kwargs["end"] = end
        if tags is not None:
            kwargs["tags"] = tags
        if parent_entity is not None:
            kwargs["parent_entity"] = {"primary": parent_entity}
        if entity_status is not None:
            kwargs["entity_status"] = entity_status

        entity = await tracker.entities.create(entity_type, summary, **kwargs)
        return _format_entity(entity, entity_type)

    @mcp.tool()
    async def get_entity(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        fields: str | None = None,
    ) -> str:
        """Get a project, portfolio, or goal by ID.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            fields: Comma-separated fields to return (e.g. "summary,description,lead,teamAccess,entityStatus,checklistItems")
        """
        tracker = ctx.lifespan_context["tracker"]
        entity = await tracker.entities.get(entity_type, entity_id, fields=fields)
        return _format_entity(entity, entity_type)

    @mcp.tool()
    async def update_entity(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        summary: str | None = None,
        description: str | None = None,
        lead: str | None = None,
        team_access: bool | None = None,
        team_users: list[str] | None = None,
        followers: list[str] | None = None,
        start: str | None = None,
        end: str | None = None,
        tags: list[str] | None = None,
        entity_status: str | None = None,
        comment: str | None = None,
    ) -> str:
        """Update a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            summary: New name
            description: New description
            lead: New lead login
            team_access: Restrict access to team
            team_users: Team member logins
            followers: Follower logins
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            tags: Tags
            entity_status: New status
            comment: Comment about the change
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if summary is not None:
            kwargs["summary"] = summary
        if description is not None:
            kwargs["description"] = description
        if lead is not None:
            kwargs["lead"] = lead
        if team_access is not None:
            kwargs["team_access"] = team_access
        if team_users is not None:
            kwargs["team_users"] = team_users
        if followers is not None:
            kwargs["followers"] = followers
        if start is not None:
            kwargs["start"] = start
        if end is not None:
            kwargs["end"] = end
        if tags is not None:
            kwargs["tags"] = tags
        if entity_status is not None:
            kwargs["entity_status"] = entity_status
        if comment is not None:
            kwargs["comment"] = comment

        entity = await tracker.entities.update(entity_type, entity_id, **kwargs)
        return _format_entity(entity, entity_type)

    @mcp.tool()
    async def delete_entity(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        with_board: bool = False,
    ) -> str:
        """Delete a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            with_board: Also delete associated board
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.entities.delete(entity_type, entity_id, with_board=with_board)
        return f"{entity_type.capitalize()} {entity_id} deleted."

    @mcp.tool()
    async def search_entities(
        ctx: Context,
        entity_type: str,
        input: str | None = None,
        fields: str | None = None,
        per_page: int | None = None,
        page: int | None = None,
        root_only: bool | None = None,
    ) -> str:
        """Search projects, portfolios, or goals.

        Args:
            entity_type: "project", "portfolio", or "goal"
            input: Text search query
            fields: Fields to return (e.g. "summary,lead,entityStatus")
            per_page: Results per page
            page: Page number
            root_only: Only return top-level entities
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if input is not None:
            kwargs["input"] = input
        if fields is not None:
            kwargs["fields"] = fields
        if per_page is not None:
            kwargs["per_page"] = per_page
        if page is not None:
            kwargs["page"] = page
        if root_only is not None:
            kwargs["root_only"] = root_only

        result = await tracker.entities.search(entity_type, **kwargs)

        values = result.get("values", []) if isinstance(result, dict) else result
        hits = result.get("hits", "?") if isinstance(result, dict) else len(values)

        if not values:
            return f"No {entity_type}s found."

        lines = [f"Found {hits} {entity_type}(s):\n"]
        for e in values:
            lines.append(_format_entity_short(e, entity_type))
        return "\n".join(lines)


def _format_entity(entity: dict, entity_type: str) -> str:
    eid = entity.get("shortId", entity.get("id", "?"))
    fields = entity.get("fields", {})

    summary = fields.get("summary", entity.get("summary", ""))
    description = fields.get("description", entity.get("description", ""))
    lead = fields.get("lead", entity.get("lead"))
    status = fields.get("entityStatus", entity.get("entityStatus"))
    start = fields.get("start", entity.get("start", ""))
    end = fields.get("end", entity.get("end", ""))

    if isinstance(lead, dict):
        lead = lead.get("display", lead.get("id", "?"))
    if isinstance(status, dict):
        status = status.get("display", status.get("key", "?"))

    lines = [f"**{entity_type.capitalize()} #{eid}**: {summary}"]
    if status:
        lines.append(f"Status: {status}")
    if lead:
        lines.append(f"Lead: {lead}")
    if start or end:
        lines.append(f"Period: {start or '?'} — {end or '?'}")
    if description:
        desc = description[:500]
        if len(description) > 500:
            desc += "..."
        lines.append(f"\n{desc}")

    # Checklist items
    checklist = fields.get("checklistItems", [])
    if checklist:
        done = sum(1 for i in checklist if i.get("checked"))
        lines.append(f"\nChecklist ({done}/{len(checklist)}):")
        for item in checklist:
            mark = "x" if item.get("checked") else " "
            lines.append(f"  [{mark}] {item.get('text', '?')}")

    return "\n".join(lines)


def _format_entity_short(entity: dict, entity_type: str) -> str:
    eid = entity.get("shortId", entity.get("id", "?"))
    fields = entity.get("fields", {})
    summary = fields.get("summary", entity.get("summary", ""))
    status = fields.get("entityStatus", entity.get("entityStatus"))
    if isinstance(status, dict):
        status = status.get("display", status.get("key", "?"))

    line = f"- **{entity_type.capitalize()} #{eid}** {summary}"
    if status:
        line += f" [{status}]"
    return line
