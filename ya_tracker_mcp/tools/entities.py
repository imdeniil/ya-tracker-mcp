from fastmcp import FastMCP, Context
from ..utils.formatters import format_mcp_item, format_mcp_list


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
        fields: list[str] | None = None,
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
            fields: Optional list of fields to show in response.
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
        return _format_entity_full(entity, entity_type, fields)

    @mcp.tool()
    async def get_entity(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        fields: list[str] | None = None,
    ) -> str:
        """Get a project, portfolio, or goal by ID.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            fields: Optional list of fields to return. Use ["all"] for all fields.
        """
        tracker = ctx.lifespan_context["tracker"]
        
        api_fields = None
        if fields and "all" not in fields:
            # Note: entities API expects comma-separated string
            api_fields = ",".join(fields)

        entity = await tracker.entities.get(entity_type, entity_id, fields=api_fields)
        return _format_entity_full(entity, entity_type, fields)

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
        fields: list[str] | None = None,
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
            fields: Optional list of fields to show in response.
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
        return _format_entity_full(entity, entity_type, fields)

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
        fields: list[str] | None = None,
        per_page: int | None = None,
        page: int | None = None,
        root_only: bool | None = None,
    ) -> str:
        """Search projects, portfolios, or goals.

        Args:
            entity_type: "project", "portfolio", or "goal"
            input: Text search query
            fields: Optional list of fields to return. Use ["all"] for all fields.
            per_page: Results per page
            page: Page number
            root_only: Only return top-level entities
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if input is not None:
            kwargs["input"] = input
        if fields is not None:
            # API expects comma-separated string for fields
            if "all" not in fields:
                kwargs["fields"] = ",".join(fields)
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

        return format_mcp_list(
            values, f"{entity_type.capitalize()}s",
            basic_fields=["entityStatus", "lead"],
            extra_fields=fields,
            key_field="shortId",
            name_field="summary",
            template="- **#{key}** {name} ({basics})"
        )

    @mcp.tool()
    async def entity_changelog(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        per_page: int | None = None,
    ) -> str:
        """Get changelog of a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            per_page: Results per page
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if per_page is not None:
            kwargs["per_page"] = per_page

        changes = await tracker.entities.changelog(entity_type, entity_id, **kwargs)

        if not changes:
            return f"No changelog for {entity_type} {entity_id}."

        lines = [f"Changelog for {entity_type} {entity_id} ({len(changes)} entries):\n"]
        for entry in changes:
            updated = entry.get("updatedAt", "")
            updater = entry.get("updatedBy", {})
            if isinstance(updater, dict):
                updater = updater.get("display", "?")
            fields = entry.get("fields", [])
            field_changes = []
            for f in fields:
                fname = f.get("field", {})
                if isinstance(fname, dict):
                    fname = fname.get("display", fname.get("id", "?"))
                frm = f.get("from", "")
                if isinstance(frm, dict):
                    frm = frm.get("display", str(frm))
                to = f.get("to", "")
                if isinstance(to, dict):
                    to = to.get("display", str(to))
                field_changes.append(f"{fname}: {frm} → {to}")
            changes_str = "; ".join(field_changes) if field_changes else "no details"
            lines.append(f"- [{updated}] {updater}: {changes_str}")
        return "\n".join(lines)

    @mcp.tool()
    async def update_key_results(
        ctx: Context,
        entity_id: str,
        key_result_items: list[dict],
        comment: str | None = None,
    ) -> str:
        """Update key results of a goal.

        Args:
            entity_id: Goal entity ID
            key_result_items: List of key result items (dicts with fields like target, current, etc.)
            comment: Optional comment
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if comment is not None:
            kwargs["comment"] = comment

        result = await tracker.entities.update_key_results(entity_id, key_result_items, **kwargs)
        return f"Key results updated for goal {entity_id}."

    @mcp.tool()
    async def update_entity_metrics(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        metric_items: list[dict],
        comment: str | None = None,
    ) -> str:
        """Update metrics of a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            metric_items: List of metric items
            comment: Optional comment
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if comment is not None:
            kwargs["comment"] = comment

        result = await tracker.entities.update_metrics(entity_type, entity_id, metric_items, **kwargs)
        return f"Metrics updated for {entity_type} {entity_id}."

    # --- Entity comments ---

    @mcp.tool()
    async def list_entity_comments(
        ctx: Context,
        entity_type: str,
        entity_id: str,
    ) -> str:
        """List comments on a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
        """
        tracker = ctx.lifespan_context["tracker"]
        comments = await tracker.entities.comments.list(entity_type, entity_id)

        if not comments:
            return f"No comments on {entity_type} {entity_id}."

        lines = [f"Comments on {entity_type} {entity_id} ({len(comments)}):\n"]
        for c in comments:
            cid = c.get("id", "?")
            text = c.get("text", "")[:200]
            author = c.get("createdBy", {})
            if isinstance(author, dict):
                author = author.get("display", "?")
            created = c.get("createdAt", "")
            lines.append(f"- [{cid}] {author} ({created}): {text}")
        return "\n".join(lines)

    @mcp.tool()
    async def add_entity_comment(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        text: str,
        summonees: list[str] | None = None,
    ) -> str:
        """Add a comment to a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            text: Comment text
            summonees: List of user logins to mention
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if summonees is not None:
            kwargs["summonees"] = summonees

        comment = await tracker.entities.comments.create(entity_type, entity_id, text, **kwargs)
        cid = comment.get("id", "?")
        return f"Comment [{cid}] added to {entity_type} {entity_id}."

    @mcp.tool()
    async def update_entity_comment(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        comment_id: str,
        text: str,
    ) -> str:
        """Update a comment on a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            comment_id: Comment ID
            text: New comment text
        """
        tracker = ctx.lifespan_context["tracker"]
        comment = await tracker.entities.comments.update(entity_type, entity_id, comment_id, text=text)
        return f"Comment [{comment_id}] updated on {entity_type} {entity_id}."

    @mcp.tool()
    async def delete_entity_comment(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        comment_id: str,
    ) -> str:
        """Delete a comment from a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            comment_id: Comment ID
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.entities.comments.delete(entity_type, entity_id, comment_id)
        return f"Comment [{comment_id}] deleted from {entity_type} {entity_id}."

    # --- Entity links ---

    @mcp.tool()
    async def list_entity_links(
        ctx: Context,
        entity_type: str,
        entity_id: str,
    ) -> str:
        """List links of a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
        """
        tracker = ctx.lifespan_context["tracker"]
        links = await tracker.entities.links.get(entity_type, entity_id)

        if not links:
            return f"No links for {entity_type} {entity_id}."

        lines = [f"Links for {entity_type} {entity_id}:\n"]
        if isinstance(links, list):
            for link in links:
                rel = link.get("relationship", "?")
                target = link.get("entity", {})
                if isinstance(target, dict):
                    target = target.get("display", target.get("id", "?"))
                lines.append(f"- {rel}: {target}")
        else:
            lines.append(str(links))
        return "\n".join(lines)

    @mcp.tool()
    async def create_entity_link(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        relationship: str,
        entity: str,
    ) -> str:
        """Create a link between entities.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Source entity ID
            relationship: Relationship type
            entity: Target entity ID
        """
        tracker = ctx.lifespan_context["tracker"]
        result = await tracker.entities.links.create(entity_type, entity_id, relationship, entity)
        return f"Link created: {entity_type} {entity_id} —[{relationship}]→ {entity}"

    @mcp.tool()
    async def delete_entity_link(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        right: str,
    ) -> str:
        """Delete a link from an entity.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            right: Target entity ID to unlink
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.entities.links.delete(entity_type, entity_id, right)
        return f"Link deleted from {entity_type} {entity_id} to {right}."

    # --- Entity attachments ---

    @mcp.tool()
    async def list_entity_attachments(
        ctx: Context,
        entity_type: str,
        entity_id: str,
    ) -> str:
        """List attachments of a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
        """
        tracker = ctx.lifespan_context["tracker"]
        attachments = await tracker.entities.attachments.list(entity_type, entity_id)

        if not attachments:
            return f"No attachments for {entity_type} {entity_id}."

        lines = [f"Attachments for {entity_type} {entity_id}:\n"]
        for a in attachments:
            aid = a.get("id", "?")
            name = a.get("name", "")
            size = a.get("size", "?")
            lines.append(f"- [{aid}] {name} ({size} bytes)")
        return "\n".join(lines)

    @mcp.tool()
    async def delete_entity_attachment(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        file_id: str,
    ) -> str:
        """Delete an attachment from a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            file_id: Attachment file ID
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.entities.attachments.delete(entity_type, entity_id, file_id)
        return f"Attachment [{file_id}] deleted from {entity_type} {entity_id}."

    # --- Entity checklists ---

    @mcp.tool()
    async def add_entity_checklist_item(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        text: str,
        checked: bool | None = None,
        assignee: str | None = None,
        deadline: str | None = None,
    ) -> str:
        """Add a checklist item to a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            text: Checklist item text
            checked: Whether the item is checked
            assignee: Assignee login
            deadline: Deadline (YYYY-MM-DD)
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if checked is not None:
            kwargs["checked"] = checked
        if assignee is not None:
            kwargs["assignee"] = assignee
        if deadline is not None:
            kwargs["deadline"] = deadline

        result = await tracker.entities.checklists.create(entity_type, entity_id, text, **kwargs)
        return f"Checklist item added to {entity_type} {entity_id}."

    @mcp.tool()
    async def update_entity_checklist_item(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        item_id: str,
        text: str | None = None,
        checked: bool | None = None,
        assignee: str | None = None,
        deadline: str | None = None,
    ) -> str:
        """Update a checklist item on a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            item_id: Checklist item ID
            text: New text
            checked: New checked status
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
            kwargs["deadline"] = deadline

        result = await tracker.entities.checklists.item.update(
            entity_type, entity_id, item_id, **kwargs
        )
        return f"Checklist item [{item_id}] updated on {entity_type} {entity_id}."

    @mcp.tool()
    async def delete_entity_checklist_item(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        item_id: str,
    ) -> str:
        """Delete a checklist item from a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            item_id: Checklist item ID
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.entities.checklists.item.delete(entity_type, entity_id, item_id)
        return f"Checklist item [{item_id}] deleted from {entity_type} {entity_id}."

    # --- Entity bulk ---

    @mcp.tool()
    async def bulk_update_entities(
        ctx: Context,
        entity_type: str,
        entity_ids: list[str],
        comment: str | None = None,
    ) -> str:
        """Bulk update multiple entities.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_ids: List of entity IDs
            comment: Optional comment
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if comment is not None:
            kwargs["comment"] = comment

        result = await tracker.entities.bulk.update(entity_type, entity_ids, **kwargs)
        return f"Bulk update started for {len(entity_ids)} {entity_type}(s)."

    # --- Entity settings ---

    @mcp.tool()
    async def get_entity_settings(
        ctx: Context,
        entity_type: str,
        entity_id: str,
    ) -> str:
        """Get access settings of a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
        """
        tracker = ctx.lifespan_context["tracker"]
        settings = await tracker.entities.settings.get(entity_type, entity_id)
        return f"Settings for {entity_type} {entity_id}:\n{settings}"

    @mcp.tool()
    async def update_entity_settings(
        ctx: Context,
        entity_type: str,
        entity_id: str,
        permission_sources: list[str] | None = None,
        acl: list[dict] | None = None,
    ) -> str:
        """Update access settings of a project, portfolio, or goal.

        Args:
            entity_type: "project", "portfolio", or "goal"
            entity_id: Entity ID
            permission_sources: Permission sources list
            acl: Access control list
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if permission_sources is not None:
            kwargs["permission_sources"] = permission_sources
        if acl is not None:
            kwargs["acl"] = acl

        result = await tracker.entities.settings.update(entity_type, entity_id, **kwargs)
        return f"Settings updated for {entity_type} {entity_id}."


def _format_entity_full(entity: dict, entity_type: str, extra_fields: list[str] | None = None) -> str:
    # Use format_mcp_item for standard formatting
    res = format_mcp_item(
        entity, entity_type.capitalize(),
        basic_fields=["entityStatus", "lead", "start", "end", "tags"],
        extra_fields=extra_fields,
        key_field="shortId",
        name_field="summary",
        template="**{key}**: {name}\n{basics}"
    )

    # Checklist items (specific logic for entities)
    fields = entity.get("fields", {})
    checklist = fields.get("checklistItems", [])
    if checklist:
        done = sum(1 for i in checklist if i.get("checked"))
        res += f"\n\nChecklist ({done}/{len(checklist)}):"
        for item in checklist:
            mark = "x" if item.get("checked") else " "
            res += f"\n  [{mark}] {item.get('text', '?')}"

    return res
