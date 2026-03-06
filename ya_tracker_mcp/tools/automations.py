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
