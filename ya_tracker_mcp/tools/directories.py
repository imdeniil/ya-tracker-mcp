from fastmcp import FastMCP, Context
from ..utils.directory_manager import manager


def register_directory_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_issue_types(
        ctx: Context,
        use_cache: bool = True,
    ) -> str:
        """List all issue types in the organization.

        Args:
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        
        types = await manager.get("issue_types", tracker.issues.types.list, force=not use_cache)

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
    async def list_statuses(
        ctx: Context,
        use_cache: bool = True,
    ) -> str:
        """List all issue statuses in the organization.

        Args:
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        
        statuses = await manager.get("statuses", tracker.issues.statuses.list, force=not use_cache)

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
    async def list_priorities(
        ctx: Context,
        use_cache: bool = True,
    ) -> str:
        """List all issue priorities in the organization.

        Args:
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        
        priorities = await manager.get("priorities", tracker.issues.priorities.list, force=not use_cache)

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
    async def list_resolutions(
        ctx: Context,
        use_cache: bool = True,
    ) -> str:
        """List all issue resolutions in the organization.

        Args:
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        
        resolutions = await manager.get("resolutions", tracker.issues.resolutions.list, force=not use_cache)

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
        use_cache: bool = True,
    ) -> str:
        """List fields (including local fields) of a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        
        fields = await manager.get(
            "queue_fields", 
            lambda: tracker.queues.fields.list(queue_key),
            scope=queue_key,
            force=not use_cache
        )

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
        use_cache: bool = True,
    ) -> str:
        """List tags used in a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        
        tags = await manager.get(
            "queue_tags",
            lambda: tracker.queues.tags.list(queue_key),
            scope=queue_key,
            force=not use_cache
        )

        if not tags:
            return f"No tags in queue {queue_key}."

        return f"Tags in {queue_key}: {', '.join(tags)}"

    @mcp.tool()
    async def list_components(
        ctx: Context,
        fields: list[str] | None = None,
        use_cache: bool = True,
    ) -> str:
        """List all components in the organization.

        Args:
            fields: Optional list of additional fields to show (e.g. ["description", "assignAuto"])
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        
        components = await manager.get("components", tracker.components.list, force=not use_cache)

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
            
            info = f"- [{cid}] **{name}** (queue: {queue}, lead: {lead})"
            
            if fields:
                extra = []
                for f in fields:
                    if f in c and f not in ["id", "name", "queue", "lead"]:
                        val = c[f]
                        if isinstance(val, dict):
                            val = val.get("display", val.get("name", str(val)))
                        extra.append(f"{f}: {val}")
                if extra:
                    info += f" | {', '.join(extra)}"
            
            lines.append(info)
        return "\n".join(lines)

    @mcp.tool()
    async def get_component(
        ctx: Context,
        component_id: int,
        use_cache: bool = True,
    ) -> str:
        """Get detailed information about a specific component by ID.

        Args:
            component_id: Numerical ID of the component
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        components = await manager.get("components", tracker.components.list, force=not use_cache)
        
        # Search in cache
        component = next((c for c in components if str(c.get("id")) == str(component_id)), None)
        
        if not component and use_cache:
            # If not found in cache and we were using cache, try to force refresh once
            components = await manager.get("components", tracker.components.list, force=True)
            component = next((c for c in components if str(c.get("id")) == str(component_id)), None)
            
        if not component:
            return f"Component with ID {component_id} not found."

        name = component.get("name", "?")
        lines = [f"### Component: {name} [{component_id}]"]
        
        # Format all available fields
        for k, v in component.items():
            if k == "name" or k == "id":
                continue
            
            display_val = v
            if isinstance(v, dict):
                display_val = v.get("display", v.get("name", v.get("key", str(v))))
            
            lines.append(f"**{k}**: {display_val}")
            
        return "\n".join(lines)

    @mcp.tool()
    async def create_component(
        ctx: Context,
        name: str,
        queue: str,
        description: str | None = None,
        lead: str | None = None,
        assign_auto: bool | None = None,
    ) -> str:
        """Create a new component.

        Args:
            name: Component name
            queue: Queue key (e.g. "DEV")
            description: Component description
            lead: Component lead login
            assign_auto: Auto-assign issues to lead
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if description is not None:
            kwargs["description"] = description
        if lead is not None:
            kwargs["lead"] = lead
        if assign_auto is not None:
            kwargs["assign_auto"] = assign_auto

        component = await tracker.components.create(name=name, queue=queue, **kwargs)
        cid = component.get("id", "?")
        cname = component.get("name", name)
        
        # Invalidate components cache
        await manager.get("components", tracker.components.list, force=True)
        
        return f"Component created: [{cid}] {cname} in queue {queue}"

    @mcp.tool()
    async def update_component(
        ctx: Context,
        component_id: int,
        name: str | None = None,
        description: str | None = None,
        lead: str | None = None,
        assign_auto: bool | None = None,
    ) -> str:
        """Update an existing component.

        Args:
            component_id: Component ID
            name: New component name
            description: New description
            lead: New lead login
            assign_auto: Auto-assign issues to lead
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if description is not None:
            kwargs["description"] = description
        if lead is not None:
            kwargs["lead"] = lead
        if assign_auto is not None:
            kwargs["assign_auto"] = assign_auto

        if not kwargs:
            return "No fields to update."

        component = await tracker.components.update(component_id, **kwargs)
        cname = component.get("name", "?")
        
        # Invalidate components cache
        await manager.get("components", tracker.components.list, force=True)
        
        return f"Component updated: [{component_id}] {cname}"

    @mcp.tool()
    async def list_global_fields(
        ctx: Context,
        use_cache: bool = True,
    ) -> str:
        """List all global issue fields.

        Args:
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        
        fields = await manager.get("global_fields", tracker.issues.fields.list, force=not use_cache)

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

    @mcp.tool()
    async def list_field_categories(
        ctx: Context,
        use_cache: bool = True,
    ) -> str:
        """List all field categories.

        Args:
            use_cache: Whether to use local cache (default: True)
        """
        tracker = ctx.lifespan_context["tracker"]
        
        categories = await manager.get("field_categories", tracker.issues.fields.categories.list, force=not use_cache)

        if not categories:
            return "No field categories found."

        lines = [f"Field categories ({len(categories)}):\n"]
        for c in categories:
            cid = c.get("id", "?")
            name = c.get("name", "")
            if isinstance(name, dict):
                name = name.get("ru", name.get("en", str(name)))
            lines.append(f"- [{cid}] **{name}**")
        return "\n".join(lines)

    # --- Cache Management Tools ---

    @mcp.tool()
    async def get_cache_status(ctx: Context) -> str:
        """Show status of directories cache (TTL, last updated, record count)."""
        status = manager.get_status()
        if not status:
            return "Cache is empty."

        lines = ["### Directory Cache Status\n"]
        lines.append("| Entity | Records | Last Updated | TTL (s) | Expires In |")
        lines.append("| :--- | :---: | :--- | :---: | :---: |")
        
        for s in status:
            exp = f"{s['expires_in_sec']}s" if not s['is_expired'] else "EXPIRED"
            lines.append(f"| {s['key']} | {s['count']} | {s['updated_at']} | {s['ttl']} | {exp} |")
        
        return "\n".join(lines)

    @mcp.tool()
    async def sync_directory(
        ctx: Context,
        directory: str,
        scope: str | None = None,
    ) -> str:
        """Manually sync a specific directory from API.

        Args:
            directory: Directory name (e.g. "statuses", "users", "queues", "queue_fields")
            scope: Optional scope (e.g. queue key for queue_fields)
        """
        tracker = ctx.lifespan_context["tracker"]
        
        # Map directory names to fetch functions
        registry = {
            "issue_types": tracker.issues.types.list,
            "statuses": tracker.issues.statuses.list,
            "priorities": tracker.issues.priorities.list,
            "resolutions": tracker.issues.resolutions.list,
            "global_fields": tracker.issues.fields.list,
            "field_categories": tracker.issues.fields.categories.list,
            "components": tracker.components.list,
            "queues": tracker.queues.list,
            "users": tracker.users.list,
            "boards": tracker.boards.list,
        }
        
        # Scoped registry
        scoped_registry = {
            "queue_fields": lambda: tracker.queues.fields.list(scope),
            "queue_tags": lambda: tracker.queues.tags.list(scope),
            "sprints": lambda: tracker.boards.sprints.list(scope), # scope is board_id here
        }

        if directory in registry:
            await manager.get(directory, registry[directory], force=True)
            return f"Successfully synced '{directory}'."
        
        if directory in scoped_registry:
            if not scope:
                return f"Error: '{directory}' requires a scope (e.g. queue key or board ID)."
            await manager.get(directory, scoped_registry[directory], scope=scope, force=True)
            return f"Successfully synced '{directory}' for scope '{scope}'."
            
        return f"Error: Unknown directory '{directory}'. Available: {', '.join(list(registry.keys()) + list(scoped_registry.keys()))}"

    @mcp.tool()
    async def sync_all_directories(ctx: Context) -> str:
        """Force sync all basic directories from API."""
        tracker = ctx.lifespan_context["tracker"]
        
        registry = {
            "issue_types": tracker.issues.types.list,
            "statuses": tracker.issues.statuses.list,
            "priorities": tracker.issues.priorities.list,
            "resolutions": tracker.issues.resolutions.list,
            "global_fields": tracker.issues.fields.list,
            "field_categories": tracker.issues.fields.categories.list,
            "components": tracker.components.list,
            "queues": tracker.queues.list,
            "users": tracker.users.list,
            "boards": tracker.boards.list,
        }
        
        results = await manager.sync_all(registry)
        return "Sync results:\n" + "\n".join(results)

    @mcp.tool()
    async def configure_cache(
        ctx: Context,
        directory: str,
        ttl: int,
    ) -> str:
        """Configure TTL (Time To Live) for a specific directory cache.

        Args:
            directory: Directory name (e.g. "statuses", "users", "queue_tags")
            ttl: TTL in seconds (0 to disable caching)
        """
        manager.set_ttl(directory, ttl)
        return f"TTL for '{directory}' set to {ttl} seconds."

    # --- CRUD tools for other entities (unchanged logic but can use cache invalidation) ---

    @mcp.tool()
    async def create_issue_type(
        ctx: Context,
        key: str,
        name: dict,
    ) -> str:
        """Create an issue type.

        Args:
            key: Type key (e.g. "task")
            name: Localized name (e.g. {"ru": "Задача", "en": "Task"})
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.issues.types.create(key=key, name=name)
        await manager.get("issue_types", tracker.issues.types.list, force=True)
        return f"Issue type '{key}' created."

    @mcp.tool()
    async def create_status(
        ctx: Context,
        key: str,
        name: dict,
        stype: str,
    ) -> str:
        """Create a new status.

        Args:
            key: Status key
            name: Localized name
            stype: Status type: "new", "inProgress", "paused", "done", "cancelled"
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.issues.statuses.create(key=key, name=name, type=stype)
        await manager.get("statuses", tracker.issues.statuses.list, force=True)
        return f"Status '{key}' created."

    @mcp.tool()
    async def create_priority(
        ctx: Context,
        key: str,
        name: dict,
        order: int,
    ) -> str:
        """Create a priority.

        Args:
            key: Priority key
            name: Localized name
            order: Priority order (number)
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.issues.priorities.create(key=key, name=name, order=order)
        await manager.get("priorities", tracker.issues.priorities.list, force=True)
        return f"Priority '{key}' created."

    @mcp.tool()
    async def create_resolution(
        ctx: Context,
        key: str,
        name: dict,
    ) -> str:
        """Create a resolution.

        Args:
            key: Resolution key
            name: Localized name
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.issues.resolutions.create(key=key, name=name)
        await manager.get("resolutions", tracker.issues.resolutions.list, force=True)
        return f"Resolution '{key}' created."

    # Note: update_* tools also need invalidation if implemented
