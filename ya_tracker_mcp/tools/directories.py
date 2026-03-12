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
        return f"Component updated: [{component_id}] {cname}"

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

    # --- Issue types CRUD ---

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
        result = await tracker.issues.types.create(key, name)
        return f"Issue type created: {key}"

    @mcp.tool()
    async def update_issue_type(
        ctx: Context,
        id_or_key: str,
        name: dict | None = None,
        version: str | None = None,
    ) -> str:
        """Update an issue type.

        Args:
            id_or_key: Type ID or key
            name: New localized name
            version: Version for optimistic locking
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if version is not None:
            kwargs["version"] = version
        result = await tracker.issues.types.update(id_or_key, **kwargs)
        return f"Issue type updated: {id_or_key}"

    # --- Statuses CRUD ---

    @mcp.tool()
    async def create_status(
        ctx: Context,
        key: str,
        name: dict,
        status_type: str,
    ) -> str:
        """Create an issue status.

        Args:
            key: Status key
            name: Localized name (e.g. {"ru": "В работе", "en": "In Progress"})
            status_type: Status type: "new", "inProgress", "paused", "done", "cancelled"
        """
        tracker = ctx.lifespan_context["tracker"]
        result = await tracker.issues.statuses.create(key, name, status_type)
        return f"Status created: {key}"

    @mcp.tool()
    async def update_status(
        ctx: Context,
        id_or_key: str,
        name: dict | None = None,
        version: str | None = None,
    ) -> str:
        """Update an issue status.

        Args:
            id_or_key: Status ID or key
            name: New localized name
            version: Version for optimistic locking
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if version is not None:
            kwargs["version"] = version
        result = await tracker.issues.statuses.update(id_or_key, **kwargs)
        return f"Status updated: {id_or_key}"

    # --- Priorities CRUD ---

    @mcp.tool()
    async def create_priority(
        ctx: Context,
        key: str,
        name: dict,
        order: int,
        description: str | None = None,
    ) -> str:
        """Create an issue priority.

        Args:
            key: Priority key
            name: Localized name
            order: Sort order
            description: Description
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if description is not None:
            kwargs["description"] = description
        result = await tracker.issues.priorities.create(key, name, order, **kwargs)
        return f"Priority created: {key}"

    @mcp.tool()
    async def update_priority(
        ctx: Context,
        id_or_key: str,
        name: dict | None = None,
        description: str | None = None,
        version: str | None = None,
    ) -> str:
        """Update an issue priority.

        Args:
            id_or_key: Priority ID or key
            name: New localized name
            description: New description
            version: Version for optimistic locking
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if description is not None:
            kwargs["description"] = description
        if version is not None:
            kwargs["version"] = version
        result = await tracker.issues.priorities.update(id_or_key, **kwargs)
        return f"Priority updated: {id_or_key}"

    # --- Resolutions CRUD ---

    @mcp.tool()
    async def create_resolution(
        ctx: Context,
        key: str,
        name: dict,
    ) -> str:
        """Create an issue resolution.

        Args:
            key: Resolution key
            name: Localized name
        """
        tracker = ctx.lifespan_context["tracker"]
        result = await tracker.issues.resolutions.create(key, name)
        return f"Resolution created: {key}"

    @mcp.tool()
    async def update_resolution(
        ctx: Context,
        id_or_key: str,
        name: dict | None = None,
        version: str | None = None,
    ) -> str:
        """Update an issue resolution.

        Args:
            id_or_key: Resolution ID or key
            name: New localized name
            version: Version for optimistic locking
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if version is not None:
            kwargs["version"] = version
        result = await tracker.issues.resolutions.update(id_or_key, **kwargs)
        return f"Resolution updated: {id_or_key}"

    # --- Global fields CRUD ---

    @mcp.tool()
    async def get_field(
        ctx: Context,
        field_id: str,
    ) -> str:
        """Get a global field by ID.

        Args:
            field_id: Field ID
        """
        tracker = ctx.lifespan_context["tracker"]
        f = await tracker.issues.fields.get(field_id)
        fid = f.get("id", "?")
        name = f.get("name", "")
        if isinstance(name, dict):
            name = name.get("ru", name.get("en", str(name)))
        ftype = f.get("type", "")
        version = f.get("version", "")
        category = f.get("category", {})
        if isinstance(category, dict):
            category = category.get("display", category.get("id", "?"))
        return f"**{fid}** — {name}\nType: {ftype}\nCategory: {category}\nVersion: {version}"

    @mcp.tool()
    async def create_field(
        ctx: Context,
        name: dict,
        field_id: str,
        category: str,
        field_type: str,
    ) -> str:
        """Create a global issue field.

        Args:
            name: Localized name (e.g. {"ru": "Поле", "en": "Field"})
            field_id: Field ID (e.g. "myCustomField")
            category: Category ID
            field_type: Field type (e.g. "string", "number", "date")
        """
        tracker = ctx.lifespan_context["tracker"]
        result = await tracker.issues.fields.create(name, field_id, category, field_type)
        return f"Field created: {field_id}"

    @mcp.tool()
    async def update_field(
        ctx: Context,
        field_id: str,
        version: str,
        name: dict | None = None,
        category: str | None = None,
        description: str | None = None,
    ) -> str:
        """Update a global issue field.

        Args:
            field_id: Field ID
            version: Version for optimistic locking (from get_field)
            name: New localized name
            category: New category ID
            description: New description
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if category is not None:
            kwargs["category"] = category
        if description is not None:
            kwargs["description"] = description
        result = await tracker.issues.fields.update(field_id, version, **kwargs)
        return f"Field updated: {field_id}"

    # --- Local fields ---

    @mcp.tool()
    async def get_local_field(
        ctx: Context,
        queue_key: str,
        field_key: str,
    ) -> str:
        """Get a local field of a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
            field_key: Local field key
        """
        tracker = ctx.lifespan_context["tracker"]
        f = await tracker.issues.fields.local.get(queue_key, field_key)
        fid = f.get("id", f.get("key", "?"))
        name = f.get("name", "")
        if isinstance(name, dict):
            name = name.get("ru", name.get("en", str(name)))
        ftype = f.get("type", "")
        return f"**{fid}** — {name} (type: {ftype})"

    @mcp.tool()
    async def create_local_field(
        ctx: Context,
        queue_key: str,
        name: dict,
        field_id: str,
        category: str,
        field_type: str,
    ) -> str:
        """Create a local field in a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
            name: Localized name
            field_id: Field ID
            category: Category ID
            field_type: Field type
        """
        tracker = ctx.lifespan_context["tracker"]
        result = await tracker.issues.fields.local.create(queue_key, name, field_id, category, field_type)
        return f"Local field created: {field_id} in queue {queue_key}"

    @mcp.tool()
    async def update_local_field(
        ctx: Context,
        queue_key: str,
        field_key: str,
        name: dict | None = None,
        category: str | None = None,
        description: str | None = None,
    ) -> str:
        """Update a local field in a queue.

        Args:
            queue_key: Queue key (e.g. "DEV")
            field_key: Local field key
            name: New localized name
            category: New category
            description: New description
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if category is not None:
            kwargs["category"] = category
        if description is not None:
            kwargs["description"] = description
        result = await tracker.issues.fields.local.update(queue_key, field_key, **kwargs)
        return f"Local field updated: {field_key} in queue {queue_key}"

    # --- Field categories ---

    @mcp.tool()
    async def list_field_categories(ctx: Context) -> str:
        """List all field categories."""
        tracker = ctx.lifespan_context["tracker"]
        cats = await tracker.issues.fields.categories.list()
        if not cats:
            return "No field categories found."
        lines = [f"Field categories ({len(cats)}):\n"]
        for c in cats:
            cid = c.get("id", "?")
            name = c.get("name", "?")
            version = c.get("version", "?")
            lines.append(f"- **{cid}** — {name} (v{version})")
        return "\n".join(lines)

    @mcp.tool()
    async def create_field_category(
        ctx: Context,
        name_en: str,
        name_ru: str,
        order: int | None = None,
    ) -> str:
        """Create a field category.

        Args:
            name_en: Category name in English
            name_ru: Category name in Russian
            order: Sort order (optional)
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if order is not None:
            kwargs["order"] = order
        result = await tracker.issues.fields.categories.create(
            name={"en": name_en, "ru": name_ru}, **kwargs
        )
        cid = result.get("id", "?")
        return f"Field category created: {cid} — {name_en} / {name_ru}"

    @mcp.tool()
    async def update_field_category(
        ctx: Context,
        category_id: str,
        version: str,
        name_en: str | None = None,
        name_ru: str | None = None,
        order: int | None = None,
    ) -> str:
        """Update a field category.

        Args:
            category_id: Category ID
            version: Current version (for optimistic locking, from list_field_categories)
            name_en: New English name
            name_ru: New Russian name
            order: New sort order
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name_en is not None or name_ru is not None:
            name = {}
            if name_en is not None:
                name["en"] = name_en
            if name_ru is not None:
                name["ru"] = name_ru
            kwargs["name"] = name
        if order is not None:
            kwargs["order"] = order
        result = await tracker.issues.fields.categories.update(
            category_id=category_id, version=version, **kwargs
        )
        return f"Field category updated: {category_id}"
