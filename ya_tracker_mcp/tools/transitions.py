from fastmcp import FastMCP, Context


def register_transition_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_transitions(
        ctx: Context,
        issue_key: str,
    ) -> str:
        """List available status transitions for an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
        """
        tracker = ctx.lifespan_context["tracker"]
        transitions = await tracker.issues.transitions.list(issue_key)

        if not transitions:
            return f"No transitions available for {issue_key}."

        lines = [f"Available transitions for {issue_key}:\n"]
        for t in transitions:
            tid = t.get("id", "?")
            display = t.get("display", t.get("to", {}).get("display", "?"))
            to_status = t.get("to", {})
            to_key = to_status.get("key", "") if isinstance(to_status, dict) else ""
            lines.append(f"- [{tid}] {display}" + (f" (-> {to_key})" if to_key else ""))
        return "\n".join(lines)

    @mcp.tool()
    async def transition_issue(
        ctx: Context,
        issue_key: str,
        transition_id: str,
        comment: str | None = None,
    ) -> str:
        """Execute a status transition on an issue.

        Use list_transitions first to get available transition IDs.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            transition_id: Transition ID (from list_transitions)
            comment: Optional comment for the transition
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if comment is not None:
            kwargs["comment"] = comment

        result = await tracker.issues.transitions.update(
            issue_key, transition_id, **kwargs
        )
        return f"Transition '{transition_id}' executed on {issue_key}.\n{_format_transition_result(result)}"


def _format_transition_result(result) -> str:
    if isinstance(result, list):
        return f"Transitions remaining: {len(result)}"
    if isinstance(result, dict):
        status = result.get("status", {})
        if isinstance(status, dict):
            return f"New status: {status.get('display', status.get('key', '?'))}"
        return f"Result: {result}"
    return str(result) if result else "Done."
