from fastmcp import FastMCP, Context
from ..utils.formatters import format_mcp_item, format_mcp_list


def register_comment_tools(mcp: FastMCP):

    @mcp.tool()
    async def add_comment(
        ctx: Context,
        issue_key: str,
        text: str,
        summonees: list[str] | None = None,
        fields: list[str] | None = None,
    ) -> str:
        """Add a comment to an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            text: Comment text (YFM markdown supported)
            summonees: List of user logins to summon
            fields: Optional list of fields to show in response. Use ["all"] for all fields.
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if summonees is not None:
            kwargs["summonees"] = summonees

        comment = await tracker.issues.comments.create(
            issue_key, text, **kwargs
        )
        return _format_comment_full(comment, fields)

    @mcp.tool()
    async def list_comments(
        ctx: Context,
        issue_key: str,
        fields: list[str] | None = None,
    ) -> str:
        """List all comments on an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            fields: Optional list of fields to show. Use ["all"] for all fields.
        """
        tracker = ctx.lifespan_context["tracker"]
        comments = await tracker.issues.comments.list(issue_key)

        return format_mcp_list(
            comments, f"Comments on {issue_key}",
            basic_fields=["createdBy", "createdAt"],
            extra_fields=fields,
            name_field="text",
            template="[{key}] {basics}:\n{name}"
        )

    @mcp.tool()
    async def update_comment(
        ctx: Context,
        issue_key: str,
        comment_id: str,
        text: str,
        fields: list[str] | None = None,
    ) -> str:
        """Update a comment.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            comment_id: Comment ID
            text: New comment text
            fields: Optional list of fields to show in response.
        """
        tracker = ctx.lifespan_context["tracker"]
        comment = await tracker.issues.comments.update(
            issue_key, comment_id, text
        )
        return _format_comment_full(comment, fields)

    @mcp.tool()
    async def delete_comment(
        ctx: Context,
        issue_key: str,
        comment_id: str,
    ) -> str:
        """Delete a comment.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            comment_id: Comment ID
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.issues.comments.delete(issue_key, comment_id)
        return f"Comment {comment_id} deleted from {issue_key}."


def _format_comment_full(comment: dict, extra_fields: list[str] | None = None) -> str:
    return format_mcp_item(
        comment, "Comment",
        basic_fields=["createdBy", "createdAt"],
        extra_fields=extra_fields,
        name_field="text",
        template="[{key}] {basics}:\n{name}",
        description_field=None # We use name_field for text
    )
