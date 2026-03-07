from fastmcp import FastMCP, Context


def register_automation_tools(mcp: FastMCP):

    # --- Macros ---

    @mcp.tool()
    async def list_macros(
        ctx: Context,
        queue: str,
    ) -> str:
        """List macros of a queue.

        Args:
            queue: Queue key (e.g. "DEV")
        """
        tracker = ctx.lifespan_context["tracker"]
        macros = await tracker.automations.macros.list(queue)

        if not macros:
            return f"No macros in queue {queue}."

        lines = [f"Macros in {queue} ({len(macros)}):\n"]
        for m in macros:
            mid = m.get("id", "?")
            name = m.get("name", "?")
            lines.append(f"- [{mid}] {name}")
        return "\n".join(lines)

    @mcp.tool()
    async def get_macro(
        ctx: Context,
        queue: str,
        macro_id: int,
    ) -> str:
        """Get macro details.

        Args:
            queue: Queue key
            macro_id: Macro ID
        """
        tracker = ctx.lifespan_context["tracker"]
        macro = await tracker.automations.macros.get(queue, macro_id)
        return _format_macro(macro)

    # --- Triggers ---

    @mcp.tool()
    async def list_triggers(
        ctx: Context,
        queue: str,
    ) -> str:
        """List triggers of a queue.

        Args:
            queue: Queue key (e.g. "DEV")
        """
        tracker = ctx.lifespan_context["tracker"]
        result = await tracker.automations.triggers.get(queue, None)

        if isinstance(result, list):
            triggers = result
        else:
            triggers = [result] if result else []

        if not triggers:
            return f"No triggers in queue {queue}."

        lines = [f"Triggers in {queue} ({len(triggers)}):\n"]
        for t in triggers:
            tid = t.get("id", "?")
            name = t.get("name", "?")
            active = t.get("active", True)
            status = "active" if active else "inactive"
            lines.append(f"- [{tid}] {name} ({status})")
        return "\n".join(lines)

    @mcp.tool()
    async def get_trigger(
        ctx: Context,
        queue: str,
        trigger_id: int,
    ) -> str:
        """Get trigger details.

        Args:
            queue: Queue key
            trigger_id: Trigger ID
        """
        tracker = ctx.lifespan_context["tracker"]
        trigger = await tracker.automations.triggers.get(queue, trigger_id)
        return _format_trigger(trigger)

    # --- Autoactions ---

    @mcp.tool()
    async def list_autoactions(
        ctx: Context,
        queue: str,
    ) -> str:
        """List autoactions of a queue.

        Args:
            queue: Queue key (e.g. "DEV")
        """
        tracker = ctx.lifespan_context["tracker"]
        result = await tracker.automations.autoactions.get(queue, None)

        if isinstance(result, list):
            autoactions = result
        else:
            autoactions = [result] if result else []

        if not autoactions:
            return f"No autoactions in queue {queue}."

        lines = [f"Autoactions in {queue} ({len(autoactions)}):\n"]
        for a in autoactions:
            aid = a.get("id", "?")
            name = a.get("name", "?")
            active = a.get("active", True)
            status = "active" if active else "inactive"
            lines.append(f"- [{aid}] {name} ({status})")
        return "\n".join(lines)

    @mcp.tool()
    async def get_autoaction(
        ctx: Context,
        queue: str,
        autoaction_id: int,
    ) -> str:
        """Get autoaction details.

        Args:
            queue: Queue key
            autoaction_id: Autoaction ID
        """
        tracker = ctx.lifespan_context["tracker"]
        aa = await tracker.automations.autoactions.get(queue, autoaction_id)
        return _format_autoaction(aa)

    # --- Macro CRUD ---

    @mcp.tool()
    async def create_macro(
        ctx: Context,
        queue: str,
        name: str,
        body: str | None = None,
        issue_update: dict | None = None,
    ) -> str:
        """Create a macro in a queue.

        Args:
            queue: Queue key (e.g. "DEV")
            name: Macro name
            body: Macro body (comment text to add)
            issue_update: Fields to update when macro runs (dict)
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if body is not None:
            kwargs["body"] = body
        if issue_update is not None:
            kwargs["issue_update"] = issue_update

        macro = await tracker.automations.macros.create(queue, name, **kwargs)
        mid = macro.get("id", "?")
        return f"Macro created: [{mid}] {name} in queue {queue}"

    @mcp.tool()
    async def update_macro(
        ctx: Context,
        queue: str,
        macro_id: int,
        name: str,
        body: str | None = None,
        issue_update: dict | None = None,
    ) -> str:
        """Update a macro.

        Args:
            queue: Queue key
            macro_id: Macro ID
            name: Macro name
            body: Macro body
            issue_update: Fields to update
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if body is not None:
            kwargs["body"] = body
        if issue_update is not None:
            kwargs["issue_update"] = issue_update

        macro = await tracker.automations.macros.update(queue, macro_id, name, **kwargs)
        return f"Macro [{macro_id}] updated in queue {queue}."

    @mcp.tool()
    async def delete_macro(
        ctx: Context,
        queue: str,
        macro_id: int,
    ) -> str:
        """Delete a macro from a queue.

        Args:
            queue: Queue key
            macro_id: Macro ID
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.automations.macros.delete(queue, macro_id)
        return f"Macro [{macro_id}] deleted from queue {queue}."

    # --- Trigger CRUD ---

    @mcp.tool()
    async def create_trigger(
        ctx: Context,
        queue: str,
        name: str,
        actions: list[dict],
        conditions: list[dict] | None = None,
        active: bool | None = None,
    ) -> str:
        """Create a trigger in a queue.

        Args:
            queue: Queue key (e.g. "DEV")
            name: Trigger name
            actions: List of action dicts
            conditions: List of condition dicts
            active: Whether trigger is active
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if conditions is not None:
            kwargs["conditions"] = conditions
        if active is not None:
            kwargs["active"] = active

        trigger = await tracker.automations.triggers.create(queue, name, actions, **kwargs)
        tid = trigger.get("id", "?")
        return f"Trigger created: [{tid}] {name} in queue {queue}"

    @mcp.tool()
    async def update_trigger(
        ctx: Context,
        queue: str,
        trigger_id: int,
        name: str | None = None,
        actions: list[dict] | None = None,
        conditions: list[dict] | None = None,
        active: bool | None = None,
    ) -> str:
        """Update a trigger.

        Args:
            queue: Queue key
            trigger_id: Trigger ID
            name: New name
            actions: New actions
            conditions: New conditions
            active: Enable/disable
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if name is not None:
            kwargs["name"] = name
        if actions is not None:
            kwargs["actions"] = actions
        if conditions is not None:
            kwargs["conditions"] = conditions
        if active is not None:
            kwargs["active"] = active

        trigger = await tracker.automations.triggers.update(queue, trigger_id, **kwargs)
        return f"Trigger [{trigger_id}] updated in queue {queue}."

    @mcp.tool()
    async def get_trigger_logs(
        ctx: Context,
        queue: str,
        trigger_id: int,
        issue_id: str | None = None,
    ) -> str:
        """Get trigger execution logs.

        Args:
            queue: Queue key
            trigger_id: Trigger ID
            issue_id: Filter by issue key
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if issue_id is not None:
            kwargs["issue_id"] = issue_id

        logs = await tracker.automations.triggers.get_logs(queue, trigger_id, **kwargs)

        if not logs:
            return f"No logs for trigger {trigger_id}."

        lines = [f"Trigger {trigger_id} logs ({len(logs)} entries):\n"]
        for entry in logs:
            ts = entry.get("timestamp", entry.get("createdAt", ""))
            issue = entry.get("issue", {})
            issue_key = issue.get("key", "?") if isinstance(issue, dict) else str(issue)
            status = entry.get("status", "?")
            lines.append(f"- [{ts}] {issue_key}: {status}")
        return "\n".join(lines)

    # --- Autoaction CRUD ---

    @mcp.tool()
    async def create_autoaction(
        ctx: Context,
        queue: str,
        name: str,
        actions: list[dict],
        filter: dict | None = None,
        query: str | None = None,
        active: bool | None = None,
    ) -> str:
        """Create an autoaction in a queue.

        Args:
            queue: Queue key (e.g. "DEV")
            name: Autoaction name
            actions: List of action dicts
            filter: Filter dict
            query: Query string
            active: Whether autoaction is active
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if filter is not None:
            kwargs["filter"] = filter
        if query is not None:
            kwargs["query"] = query
        if active is not None:
            kwargs["active"] = active

        aa = await tracker.automations.autoactions.create(queue, name, actions, **kwargs)
        aid = aa.get("id", "?")
        return f"Autoaction created: [{aid}] {name} in queue {queue}"

    @mcp.tool()
    async def get_autoaction_logs(
        ctx: Context,
        queue: str,
        autoaction_id: int,
    ) -> str:
        """Get autoaction execution logs.

        Args:
            queue: Queue key
            autoaction_id: Autoaction ID
        """
        tracker = ctx.lifespan_context["tracker"]
        logs = await tracker.automations.autoactions.get_logs(queue, autoaction_id)

        if not logs:
            return f"No logs for autoaction {autoaction_id}."

        lines = [f"Autoaction {autoaction_id} logs ({len(logs)} entries):\n"]
        for entry in logs:
            ts = entry.get("timestamp", entry.get("createdAt", ""))
            status = entry.get("status", "?")
            lines.append(f"- [{ts}] {status}")
        return "\n".join(lines)


def _format_macro(macro: dict) -> str:
    mid = macro.get("id", "?")
    name = macro.get("name", "?")
    body = macro.get("body", "")

    lines = [f"**Macro [{mid}]**: {name}"]
    if body:
        lines.append(f"\nBody:\n{body[:500]}")

    issue_update = macro.get("issueUpdate", {})
    if issue_update:
        lines.append(f"\nIssue update: {issue_update}")

    return "\n".join(lines)


def _format_trigger(trigger: dict) -> str:
    tid = trigger.get("id", "?")
    name = trigger.get("name", "?")
    active = trigger.get("active", True)

    lines = [f"**Trigger [{tid}]**: {name} ({'active' if active else 'inactive'})"]

    conditions = trigger.get("conditions", [])
    if conditions:
        lines.append(f"\nConditions: {conditions}")

    actions = trigger.get("actions", [])
    if actions:
        lines.append(f"\nActions: {actions}")

    return "\n".join(lines)


def _format_autoaction(aa: dict) -> str:
    aid = aa.get("id", "?")
    name = aa.get("name", "?")
    active = aa.get("active", True)

    lines = [f"**Autoaction [{aid}]**: {name} ({'active' if active else 'inactive'})"]

    query = aa.get("query", "")
    filt = aa.get("filter", {})
    if query:
        lines.append(f"Query: {query}")
    if filt:
        lines.append(f"Filter: {filt}")

    actions = aa.get("actions", [])
    if actions:
        lines.append(f"\nActions: {actions}")

    interval = aa.get("intervalMillis")
    if interval:
        lines.append(f"Interval: {interval}ms")

    return "\n".join(lines)
