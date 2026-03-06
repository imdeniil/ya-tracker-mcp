from fastmcp import FastMCP, Context


def register_comment_tools(mcp: FastMCP):

    @mcp.tool()
    async def add_comment(
        ctx: Context,
        issue_key: str,
        text: str,
        summonees: list[str] | None = None,
    ) -> str:
        """Add a comment to an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            text: Comment text (YFM markdown supported)
            summonees: List of user logins to summon
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if summonees is not None:
            kwargs["summonees"] = summonees

        comment = await tracker.issues.comments.create(
            issue_key, text, **kwargs
        )
        return _format_comment(comment)

    @mcp.tool()
    async def list_comments(
        ctx: Context,
        issue_key: str,
    ) -> str:
        """List all comments on an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
        """
        tracker = ctx.lifespan_context["tracker"]
        comments = await tracker.issues.comments.list(issue_key)

        if not comments:
            return f"No comments on {issue_key}."

        lines = [f"Comments on {issue_key} ({len(comments)}):\n"]
        for c in comments:
            lines.append(_format_comment(c))
            lines.append("")
        return "\n".join(lines)

    @mcp.tool()
    async def update_comment(
        ctx: Context,
        issue_key: str,
        comment_id: str,
        text: str,
    ) -> str:
        """Update a comment.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            comment_id: Comment ID
            text: New comment text
        """
        tracker = ctx.lifespan_context["tracker"]
        comment = await tracker.issues.comments.update(
            issue_key, comment_id, text
        )
        return _format_comment(comment)

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


def _format_comment(comment: dict) -> str:
    cid = comment.get("id", "?")
    text = comment.get("text", "")
    author = comment.get("createdBy", {})
    if isinstance(author, dict):
        author = author.get("display", author.get("id", "?"))
    created = comment.get("createdAt", "")

    text_preview = text[:300]
    if len(text) > 300:
        text_preview += "..."

    return f"[{cid}] {author} ({created}):\n{text_preview}"
