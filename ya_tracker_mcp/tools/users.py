import json

from fastmcp import FastMCP, Context
from ..utils.directory_manager import manager
from ..utils.formatters import format_mcp_list


def register_user_tools(mcp: FastMCP):

    @mcp.tool()
    async def get_myself(
        ctx: Context,
        output_format: str = "text",
    ) -> str:
        """Get current authenticated user info.

        Args:
            output_format: Response format: "text" (default, markdown) or "json"
        """
        tracker = ctx.lifespan_context["tracker"]
        user = await tracker.users.get_myself()
        if output_format == "json":
            return json.dumps(user, ensure_ascii=False, default=str)
        return _format_user(user)

    @mcp.tool()
    async def get_user(
        ctx: Context,
        user_id: str,
        output_format: str = "text",
    ) -> str:
        """Get info about a specific user.

        Args:
            user_id: User login or UID
            output_format: Response format: "text" (default, markdown) or "json"
        """
        tracker = ctx.lifespan_context["tracker"]
        user = await tracker.users.get(user_id)
        if output_format == "json":
            return json.dumps(user, ensure_ascii=False, default=str)
        return _format_user(user)

    @mcp.tool()
    async def list_users(
        ctx: Context,
        fields: list[str] | None = None,
        per_page: int | None = None,
        use_cache: bool = True,
        output_format: str = "text",
    ) -> str:
        """List organization users.

        Args:
            fields: Optional list of additional fields (e.g. ["uid", "dismissed"])
            per_page: Results per page (if not using cache)
            use_cache: Whether to use local cache (default: True). Note: per_page is ignored if using cache.
            output_format: Response format: "text" (default, markdown) or "json"
        """
        tracker = ctx.lifespan_context["tracker"]

        if per_page is None:
            users = await manager.get("users", tracker.users.list, force=not use_cache)
        else:
            users = await tracker.users.list(per_page=per_page)

        return format_mcp_list(
            users, "Users",
            basic_fields=["login", "email"],
            extra_fields=fields,
            key_field="login",
            name_field="display",
            template="- **{name}** (@{key}) | {basics}",
            output_format=output_format,
        )


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
