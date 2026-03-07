from fastmcp import FastMCP, Context


def register_import_tools(mcp: FastMCP):

    @mcp.tool()
    async def import_issue(
        ctx: Context,
        queue: str,
        summary: str,
        created_at: str,
        created_by: str,
        key: str | None = None,
        description: str | None = None,
        status: str | None = None,
        issue_type: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        deadline: str | None = None,
        tags: list[str] | None = None,
        resolution: str | None = None,
        resolved_at: str | None = None,
        resolved_by: str | None = None,
    ) -> str:
        """Import an issue preserving original timestamps and author.

        Args:
            queue: Queue key (e.g. "DEV")
            summary: Issue title
            created_at: Original creation time (ISO 8601 with timezone, e.g. "2024-01-15T10:00:00.000+0000")
            created_by: Original author login
            key: Desired issue key (optional, e.g. "DEV-500")
            description: Issue description
            status: Status key
            issue_type: Type key (task, bug, etc.)
            priority: Priority key
            assignee: Assignee login
            deadline: Deadline (YYYY-MM-DD)
            tags: List of tags
            resolution: Resolution key (if resolved)
            resolved_at: Resolution time (ISO 8601)
            resolved_by: Who resolved (login)
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if key is not None:
            kwargs["key"] = key
        if description is not None:
            kwargs["description"] = description
        if status is not None:
            kwargs["status"] = status
        if issue_type is not None:
            kwargs["type"] = issue_type
        if priority is not None:
            kwargs["priority"] = priority
        if assignee is not None:
            kwargs["assignee"] = assignee
        if deadline is not None:
            kwargs["deadline"] = deadline
        if tags is not None:
            kwargs["tags"] = tags
        if resolution is not None:
            kwargs["resolution"] = resolution
        if resolved_at is not None:
            kwargs["resolved_at"] = resolved_at
        if resolved_by is not None:
            kwargs["resolved_by"] = resolved_by

        issue = await tracker.imports.issue(
            queue=queue,
            summary=summary,
            created_at=created_at,
            created_by=created_by,
            **kwargs,
        )

        issue_key = issue.get("key", "?")
        return f"Issue **{issue_key}** imported.\nhttps://tracker.yandex.ru/{issue_key}"

    @mcp.tool()
    async def import_comment(
        ctx: Context,
        issue_key: str,
        text: str,
        created_at: str,
        created_by: str,
    ) -> str:
        """Import a comment with original timestamp and author.

        Args:
            issue_key: Target issue key (e.g. "DEV-123")
            text: Comment text
            created_at: Original creation time (ISO 8601, must be within issue's created-updated interval)
            created_by: Original author login
        """
        tracker = ctx.lifespan_context["tracker"]
        comment = await tracker.imports.comment(
            issue_key, text, created_at, created_by
        )
        cid = comment.get("id", "?")
        return f"Comment [{cid}] imported to {issue_key}."

    @mcp.tool()
    async def import_link(
        ctx: Context,
        issue_key: str,
        relationship: str,
        target: str,
        created_at: str,
        created_by: str,
    ) -> str:
        """Import a link between issues with original timestamp.

        Args:
            issue_key: Source issue key
            relationship: Link type (e.g. "relates", "depends on")
            target: Target issue key
            created_at: Original creation time (ISO 8601, must be within both issues' intervals)
            created_by: Original author login
        """
        tracker = ctx.lifespan_context["tracker"]
        link = await tracker.imports.link(
            issue_key, relationship, target, created_at, created_by
        )
        return f"Link '{relationship}' from {issue_key} to {target} imported."

    @mcp.tool()
    async def import_file(
        ctx: Context,
        issue_key: str,
        filename: str,
        created_at: str,
        created_by: str,
        file_data: str,
    ) -> str:
        """Import a file attachment with original timestamp and author.

        Args:
            issue_key: Target issue key (e.g. "DEV-123")
            filename: File name
            created_at: Original creation time (ISO 8601 with +0000 timezone)
            created_by: Original author login
            file_data: File content as text (for binary files use base64)
        """
        tracker = ctx.lifespan_context["tracker"]
        result = await tracker.imports.file(
            issue_key, file_data.encode("utf-8"), filename, created_at, created_by
        )
        fid = result.get("id", "?") if isinstance(result, dict) else "?"
        return f"File '{filename}' [{fid}] imported to {issue_key}."
