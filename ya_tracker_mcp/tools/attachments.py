from fastmcp import FastMCP, Context


def register_attachment_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_attachments(
        ctx: Context,
        issue_key: str,
    ) -> str:
        """List attachments of an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
        """
        tracker = ctx.lifespan_context["tracker"]
        attachments = await tracker.issues.attachments.list(issue_key)

        if not attachments:
            return f"No attachments on {issue_key}."

        lines = [f"Attachments on {issue_key} ({len(attachments)}):\n"]
        for a in attachments:
            aid = a.get("id", "?")
            name = a.get("name", "?")
            size = a.get("size", 0)
            mimetype = a.get("mimetype", "")
            created = a.get("createdAt", "")
            author = a.get("createdBy", {})
            if isinstance(author, dict):
                author = author.get("display", "?")

            size_str = _human_size(size)
            lines.append(f"- [{aid}] {name} ({size_str}, {mimetype}) by {author} at {created}")
        return "\n".join(lines)

    @mcp.tool()
    async def delete_attachment(
        ctx: Context,
        issue_key: str,
        attachment_id: str,
    ) -> str:
        """Delete an attachment from an issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            attachment_id: Attachment ID (from list_attachments)
        """
        tracker = ctx.lifespan_context["tracker"]
        await tracker.issues.attachments.delete(issue_key, attachment_id)
        return f"Attachment {attachment_id} deleted from {issue_key}."


def _human_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"
