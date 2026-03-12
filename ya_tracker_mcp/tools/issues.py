from fastmcp import FastMCP, Context


def register_issue_tools(mcp: FastMCP):

    @mcp.tool()
    async def create_issue(
        ctx: Context,
        queue: str,
        summary: str,
        description: str | None = None,
        issue_type: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        parent: str | None = None,
        sprint: str | None = None,
        tags: list[str] | None = None,
        project: int | None = None,
        followers: list[str] | None = None,
        deadline: str | None = None,
        story_points: float | None = None,
        original_estimation: str | None = None,
        extra_fields: dict | None = None,
    ) -> str:
        """Create a new issue in Yandex Tracker.

        Args:
            queue: Queue key (e.g. "DEV")
            summary: Issue title (max 255 chars)
            description: Issue description (YFM markdown supported)
            issue_type: Issue type key: "task", "bug", "story", "epic"
            priority: Priority key: "blocker", "critical", "normal", "minor", "trivial"
            assignee: Assignee login
            parent: Parent issue key (e.g. "DEV-123")
            sprint: Sprint ID
            tags: List of tags
            project: Project shortId (number)
            followers: List of follower logins
            deadline: Deadline date (YYYY-MM-DD)
            story_points: Story points estimate
            original_estimation: Original estimation in ISO 8601 (e.g. "PT2H", "P1D")
            extra_fields: Additional/custom/local fields as dict (e.g. {"coAssignees": ["user1"], "myCustomField": "value"})
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if description is not None:
            kwargs["description"] = description
        if issue_type is not None:
            kwargs["issue_type"] = issue_type
        if priority is not None:
            kwargs["priority"] = priority
        if assignee is not None:
            kwargs["assignee"] = assignee
        if parent is not None:
            kwargs["parent"] = parent
        if sprint is not None:
            kwargs["sprint"] = [{"id": int(sprint)}]
        if tags is not None:
            kwargs["tags"] = tags
        if project is not None:
            kwargs["project"] = {"primary": project}
        if followers is not None:
            kwargs["followers"] = followers
        if deadline is not None:
            kwargs["deadline"] = deadline
        if story_points is not None:
            kwargs["story_points"] = story_points
        if original_estimation is not None:
            kwargs["original_estimation"] = original_estimation
        if extra_fields is not None:
            kwargs.update(extra_fields)

        issue = await tracker.issues.create(
            summary=summary,
            queue=queue,
            **kwargs,
        )

        return _format_issue(issue)

    @mcp.tool()
    async def get_issue(
        ctx: Context,
        issue_key: str,
        expand: str | None = None,
    ) -> str:
        """Get issue details by key.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            expand: Expand additional fields: "transitions", "attachments", or "transitions,attachments"
        """
        tracker = ctx.lifespan_context["tracker"]
        issue = await tracker.issues.get(issue_key, expand=expand)
        return _format_issue(issue)

    @mcp.tool()
    async def update_issue(
        ctx: Context,
        issue_key: str,
        summary: str | None = None,
        description: str | None = None,
        issue_type: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        parent: str | None = None,
        sprint: str | None = None,
        tags: list[str] | None = None,
        project: int | None = None,
        followers: list[str] | None = None,
        deadline: str | None = None,
        story_points: float | None = None,
        extra_fields: dict | None = None,
    ) -> str:
        """Update an existing issue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            summary: New title
            description: New description
            issue_type: New type key
            priority: New priority key
            assignee: New assignee login
            parent: Parent issue key
            sprint: Sprint ID
            tags: Replace all tags
            project: Project shortId (number)
            followers: Replace all followers
            deadline: Deadline (YYYY-MM-DD)
            story_points: Story points
            extra_fields: Additional/custom/local fields as dict (e.g. {"coAssignees": ["user1"], "myCustomField": "value"})
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if summary is not None:
            kwargs["summary"] = summary
        if description is not None:
            kwargs["description"] = description
        if issue_type is not None:
            kwargs["issue_type"] = issue_type
        if priority is not None:
            kwargs["priority"] = priority
        if assignee is not None:
            kwargs["assignee"] = assignee
        if parent is not None:
            kwargs["parent"] = parent
        if sprint is not None:
            kwargs["sprint"] = [{"id": int(sprint)}]
        if tags is not None:
            kwargs["tags"] = tags
        if project is not None:
            kwargs["project"] = {"primary": project}
        if followers is not None:
            kwargs["followers"] = followers
        if deadline is not None:
            kwargs["deadline"] = deadline
        if story_points is not None:
            kwargs["story_points"] = story_points
        if extra_fields is not None:
            kwargs.update(extra_fields)

        issue = await tracker.issues.update(issue_key, **kwargs)
        return _format_issue(issue)

    @mcp.tool()
    async def search_issues(
        ctx: Context,
        query: str | None = None,
        queue: str | None = None,
        keys: str | None = None,
        order: str | None = None,
        per_page: int | None = None,
        page: int | None = None,
    ) -> str:
        """Search issues using query language or filters.

        Args:
            query: Query string (e.g. 'Assignee: me() Resolution: empty()')
            queue: Filter by queue key
            keys: Comma-separated issue keys (e.g. "DEV-1,DEV-2")
            order: Sort order (e.g. "Created DESC", "Priority ASC")
            per_page: Results per page (default 50)
            page: Page number (1-based)
        """
        tracker = ctx.lifespan_context["tracker"]

        kwargs = {}
        if query is not None:
            kwargs["query"] = query
        if queue is not None:
            kwargs["queue"] = queue
        if keys is not None:
            kwargs["keys"] = keys
        if order is not None:
            kwargs["order"] = order
        if per_page is not None:
            kwargs["per_page"] = per_page
        if page is not None:
            kwargs["page"] = page

        issues = await tracker.issues.search(**kwargs)

        if not issues:
            return "No issues found."

        lines = [f"Found {len(issues)} issue(s):\n"]
        for issue in issues:
            lines.append(_format_issue_short(issue))
        return "\n".join(lines)

    @mcp.tool()
    async def count_issues(
        ctx: Context,
        query: str | None = None,
    ) -> str:
        """Count issues matching a query.

        Args:
            query: Query string (e.g. 'Queue: DEV Resolution: empty()')
        """
        tracker = ctx.lifespan_context["tracker"]
        count = await tracker.issues.count(query=query)
        return f"Count: {count}"

    @mcp.tool()
    async def issue_changelog(
        ctx: Context,
        issue_key: str,
        field: str | None = None,
        per_page: int | None = None,
    ) -> str:
        """Get issue changelog (history of changes).

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            field: Filter by field name (e.g. "status", "assignee")
            per_page: Results per page
        """
        tracker = ctx.lifespan_context["tracker"]
        kwargs = {}
        if field is not None:
            kwargs["field"] = field
        if per_page is not None:
            kwargs["per_page"] = per_page

        changes = await tracker.issues.changelog(issue_key, **kwargs)

        if not changes:
            return f"No changelog entries for {issue_key}."

        lines = [f"Changelog for {issue_key} ({len(changes)} entries):\n"]
        for entry in changes:
            updated = entry.get("updatedAt", "")
            updater = entry.get("updatedBy", {})
            if isinstance(updater, dict):
                updater = updater.get("display", "?")
            fields = entry.get("fields", [])
            field_changes = []
            for f in fields:
                fname = f.get("field", {})
                if isinstance(fname, dict):
                    fname = fname.get("display", fname.get("id", "?"))
                frm = f.get("from", "")
                if isinstance(frm, dict):
                    frm = frm.get("display", str(frm))
                to = f.get("to", "")
                if isinstance(to, dict):
                    to = to.get("display", str(to))
                field_changes.append(f"{fname}: {frm} → {to}")
            changes_str = "; ".join(field_changes) if field_changes else "no field details"
            lines.append(f"- [{updated}] {updater}: {changes_str}")
        return "\n".join(lines)

    @mcp.tool()
    async def move_issue(
        ctx: Context,
        issue_key: str,
        queue: str,
    ) -> str:
        """Move issue to another queue.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
            queue: Target queue key (e.g. "SUPPORT")
        """
        tracker = ctx.lifespan_context["tracker"]
        issue = await tracker.issues.move(issue_key, queue)
        return _format_issue(issue)


def _format_issue(issue: dict) -> str:
    key = issue.get("key", "?")
    summary = issue.get("summary", "")
    status = _extract_display(issue.get("status"))
    priority = _extract_display(issue.get("priority"))
    issue_type = _extract_display(issue.get("type"))
    assignee = _extract_display(issue.get("assignee"))
    author = _extract_display(issue.get("createdBy"))
    created = issue.get("createdAt", "")
    updated = issue.get("updatedAt", "")
    deadline = issue.get("deadline", "")
    description = issue.get("description", "")
    tags = issue.get("tags", [])
    sp = issue.get("storyPoints")

    lines = [
        f"**{key}**: {summary}",
        f"Status: {status} | Type: {issue_type} | Priority: {priority}",
    ]
    if assignee:
        lines.append(f"Assignee: {assignee}")
    if author:
        lines.append(f"Author: {author}")
    if deadline:
        lines.append(f"Deadline: {deadline}")
    if sp is not None:
        lines.append(f"Story Points: {sp}")
    if tags:
        lines.append(f"Tags: {', '.join(tags)}")
    if created:
        lines.append(f"Created: {created}")
    if updated:
        lines.append(f"Updated: {updated}")
    if description:
        desc_preview = description[:500]
        if len(description) > 500:
            desc_preview += "..."
        lines.append(f"\nDescription:\n{desc_preview}")

    # Transitions if expanded
    transitions = issue.get("transitions")
    if transitions:
        trans_names = [t.get("display", t.get("id", "?")) for t in transitions]
        lines.append(f"\nAvailable transitions: {', '.join(trans_names)}")

    lines.append(f"\nhttps://tracker.yandex.ru/{key}")
    return "\n".join(lines)


def _format_issue_short(issue: dict) -> str:
    key = issue.get("key", "?")
    summary = issue.get("summary", "")
    status = _extract_display(issue.get("status"))
    priority = _extract_display(issue.get("priority"))
    assignee = _extract_display(issue.get("assignee"))
    deadline = issue.get("deadline", "")

    line = f"- **{key}** [{status}] {summary}"
    parts = []
    if priority:
        parts.append(f"P:{priority}")
    if assignee:
        parts.append(f"@{assignee}")
    if deadline:
        parts.append(f"DL:{deadline}")
    if parts:
        line += f" ({', '.join(parts)})"
    return line


def _extract_display(obj) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return obj.get("display", obj.get("name", obj.get("key", obj.get("id", str(obj)))))
    return str(obj)
