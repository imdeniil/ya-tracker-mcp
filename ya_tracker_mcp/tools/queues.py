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

    @mcp.tool()
    async def create_queue(
        ctx: Context,
        key: str,
        name: str,
        lead: str,
        default_type: str,
        default_priority: str,
        issue_types_config: list[dict],
        description: str | None = None,
    ) -> str:
        """Create a new queue.

        Args:
            key: Queue key (e.g. "DEV")
            name: Queue name
            lead: Lead user login
            default_type: Default issue type key
            default_priority: Default priority key
            issue_types_config: Issue types config (list of dicts with issueType and workflow keys)
            description: Queue description
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if description is not None:
            kwargs["description"] = description

        queue = await tracker.queues.create(
            key, name, lead, default_type, default_priority, issue_types_config, **kwargs
        )
        return _format_queue(queue)

    @mcp.tool()
    async def delete_queue(
        ctx: Context,
        queue_key: str,
    ) -> str:
        """Delete a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.queues.delete(queue_key)
        return f"Queue {queue_key} deleted."

    @mcp.tool()
    async def restore_queue(
        ctx: Context,
        queue_key: str,
    ) -> str:
        """Restore a previously deleted queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.queues.restore(queue_key)
        return f"Queue {queue_key} restored."

    @mcp.tool()
    async def list_queue_versions(
        ctx: Context,
        queue_key: str,
    ) -> str:
        """List versions of a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
        """
        tracker = ctx.lifespan_context["tracker"]
        versions = await tracker.queues.versions.list(queue_key)

        if not versions:
            return f"No versions in queue {queue_key}."

        lines = [f"Versions in {queue_key}:\n"]
        for v in versions:
            vid = v.get("id", "?")
            name = v.get("name", "")
            start = v.get("startDate", "")
            due = v.get("dueDate", "")
            released = v.get("released", False)
            status = "released" if released else "active"
            lines.append(f"- [{vid}] {name} ({start} — {due}) [{status}]")
        return "\n".join(lines)

    @mcp.tool()
    async def create_queue_version(
        ctx: Context,
        queue_key: str,
        name: str,
        description: str | None = None,
        start_date: str | None = None,
        due_date: str | None = None,
    ) -> str:
        """Create a version in a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
            name: Version name
            description: Version description
            start_date: Start date (YYYY-MM-DD)
            due_date: Due date (YYYY-MM-DD)
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if description is not None:
            kwargs["description"] = description
        if start_date is not None:
            kwargs["start_date"] = start_date
        if due_date is not None:
            kwargs["due_date"] = due_date

        version = await tracker.queues.versions.create(queue_key, name, **kwargs)
        vid = version.get("id", "?")
        return f"Version created: [{vid}] {name} in queue {queue_key}"

    @mcp.tool()
    async def delete_queue_tag(
        ctx: Context,
        queue_key: str,
        tag: str,
    ) -> str:
        """Delete a tag from a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
            tag: Tag name to delete
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.queues.tags.delete(queue_key, tag)
        return f"Tag '{tag}' deleted from queue {queue_key}."

    @mcp.tool()
    async def get_queue_user_permissions(
        ctx: Context,
        queue_key: str,
        user_id: str,
    ) -> str:
        """Get user permissions for a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
            user_id: User login or UID
        """
        tracker = ctx.lifespan_context["tracker"]
        perms = await tracker.queues.permissions.get_user(queue_key, user_id)
        return f"Permissions for {user_id} in {queue_key}:\n{perms}"

    @mcp.tool()
    async def update_queue_permissions(
        ctx: Context,
        queue_key: str,
        create: dict | None = None,
        write: dict | None = None,
        read: dict | None = None,
        grant: dict | None = None,
    ) -> str:
        """Update queue access permissions.

        Args:
            queue_key: Queue key (e.g. "DEV")
            create: Create permission (e.g. {"users": {"add": ["uid1"]}})
            write: Write permission
            read: Read permission
            grant: Grant permission
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if create is not None:
            kwargs["create"] = create
        if write is not None:
            kwargs["write"] = write
        if read is not None:
            kwargs["read"] = read
        if grant is not None:
            kwargs["grant"] = grant

        if not kwargs:
            return "No permissions to update."

        result = await tracker.queues.permissions.update(queue_key, **kwargs)
        return f"Permissions updated for queue {queue_key}."


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
