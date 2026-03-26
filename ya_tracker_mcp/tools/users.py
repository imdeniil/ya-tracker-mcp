from fastmcp import FastMCP, Context
from ..utils.directory_manager import manager


def register_user_tools(mcp: FastMCP):

    @mcp.tool()
    async def get_myself(ctx: Context) -> str:
        """Get current authenticated user info."""
        tracker = ctx.lifespan_context["tracker"]
        user = await tracker.users.get_myself()
        return _format_user(user)

    @mcp.tool()
    async def get_user(
        ctx: Context,
        user_id: str,
    ) -> str:
        """Get info about a specific user.

        Args:
            user_id: User login or UID
        """
        tracker = ctx.lifespan_context["tracker"]
        user = await tracker.users.get(user_id)
        return _format_user(user)

    @mcp.tool()
    async def list_users(
        ctx: Context,
        per_page: int | None = None,
        use_cache: bool = True,
    ) -> str:
        """List organization users.

        Args:
            per_page: Results per page (if not using cache)
            use_cache: Whether to use local cache (default: True). Note: per_page is ignored if using cache.
        """
        tracker = ctx.lifespan_context["tracker"]

        if per_page is None:
            users = await manager.get("users", tracker.users.list, force=not use_cache)
        else:
            users = await tracker.users.list(per_page=per_page)

        if not users:
            return "No users found."

        lines = [f"Users ({len(users)}):\n"]
        for u in users:
            lines.append(_format_user_short(u))
        return "\n".join(lines)


def _format_user(user: dict) -> str:
    uid = user.get("uid", user.get("id", "?"))
    login = user.get("login", "")
    display = user.get("display", "")
    email = user.get("email", "")
    dismissed = user.get("dismissed", False)

    lines = [
        f"**{display}**",
        f"Login: {login} | UID: {uid}",
    ]
    if email:
        lines.append(f"Email: {email}")
    if dismissed:
        lines.append("Status: dismissed")
    return "\n".join(lines)


def _format_user_short(user: dict) -> str:
    login = user.get("login", "?")
    display = user.get("display", "")
    email = user.get("email", "")
    return f"- {display} (@{login})" + (f" <{email}>" if email else "")
