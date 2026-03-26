from fastmcp import FastMCP, Context
from ..utils.directory_manager import manager


def register_queue_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_queues(
        ctx: Context,
        per_page: int | None = None,
        use_cache: bool = True,
    ) -> str:
        """List all available queues.

        Args:
            per_page: Results per page (if not using cache)
            use_cache: Whether to use local cache (default: True). Note: per_page is ignored if using cache.
        """
        tracker = ctx.lifespan_context["tracker"]

        # Cache only the full list (without per_page filter)
        if per_page is None:
            queues = await manager.get("queues", tracker.queues.list, force=not use_cache)
        else:
            queues = await tracker.queues.list(per_page=per_page)

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
        
        # Invalidate queues cache
        await manager.get("queues", tracker.queues.list, force=True)
        
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
        
        # Invalidate queues cache
        await manager.get("queues", tracker.queues.list, force=True)
        
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
        
        # Invalidate queues cache
        await manager.get("queues", tracker.queues.list, force=True)
        
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
        
        # Using DirectoryManager for versions might be tricky since they are per-queue
        # but our manager supports scope. However, versions are not in DEFAULT_TTLS.
        # Let's use a generic 'queue_versions' dir type if needed, or just keep it simple.
        # Actually, let's just use the API for now or add it to manager.
        
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
        """Create a new version for a queue.

        Args:
            queue_key: Queue key
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
            queue_key: Queue key
            tag: Tag name
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.queues.tags.delete(queue_key, tag)
        
        # Invalidate queue tags cache
        await manager.get(
            "queue_tags", 
            lambda: tracker.queues.tags.list(queue_key),
            scope=queue_key,
            force=True
        )
        
        return f"Tag '{tag}' deleted from queue {queue_key}."

    @mcp.tool()
    async def get_queue_user_permissions(
        ctx: Context,
        queue_key: str,
        user_id: str,
    ) -> str:
        """Get user permissions for a queue.

        Args:
            queue_key: Queue key
            user_id: User ID or login
        """
        tracker = ctx.lifespan_context["tracker"]
        perms = await tracker.queues.permissions.get_user(queue_key, user_id)
        
        lines = [f"Permissions for user {user_id} in {queue_key}:\n"]
        for p in perms:
            lines.append(f"- {p}")
        return "\n".join(lines)

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
            queue_key: Queue key
            create: Permission payload for 'create' action (e.g. {"users": {"add": ["user1"]}})
            write: Permission payload for 'write' action
            read: Permission payload for 'read' action
            grant: Permission payload for 'grant' action
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if create: kwargs["create"] = create
        if write: kwargs["write"] = write
        if read: kwargs["read"] = read
        if grant: kwargs["grant"] = grant

        await tracker.queues.permissions.update(queue_key, **kwargs)
        return f"Permissions for queue {queue_key} updated."


def _format_queue(q: dict) -> str:
    key = q.get("key", "?")
    name = q.get("name", "")
    lead = q.get("lead", {})
    if isinstance(lead, dict):
        lead = lead.get("display", lead.get("id", "?"))
    
    lines = [
        f"**{key}**: {name}",
        f"Lead: {lead}",
    ]
    
    desc = q.get("description")
    if desc:
        lines.append(f"\nDescription:\n{desc}")
        
    lines.append(f"\nhttps://tracker.yandex.ru/manager/queues/{key}")
    return "\n".join(lines)
