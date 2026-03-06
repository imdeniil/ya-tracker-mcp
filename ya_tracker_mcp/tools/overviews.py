from fastmcp import FastMCP, Context


def register_overview_tools(mcp: FastMCP):

    @mcp.tool()
    async def issue_overview(
        ctx: Context,
        issue_key: str,
    ) -> str:
        """Get a comprehensive overview of an issue including status, comments, links, checklist and worklog.

        Args:
            issue_key: Issue key (e.g. "DEV-123")
        """
        tracker = ctx.lifespan_context["tracker"]

        issue = await tracker.issues.get(issue_key, expand="transitions,attachments")

        comments = await tracker.issues.comments.list(issue_key)
        links = await tracker.issues.links.list(issue_key)

        try:
            checklists = await tracker.issues.checklists.list(issue_key)
        except Exception:
            checklists = []

        try:
            worklogs = await tracker.worklog.list(issue_key)
        except Exception:
            worklogs = []

        return _build_issue_overview(issue, comments, links, checklists, worklogs)

    @mcp.tool()
    async def queue_overview(
        ctx: Context,
        queue_key: str,
    ) -> str:
        """Get an overview of a queue: open issues count, top priority issues.

        Args:
            queue_key: Queue key (e.g. "DEV")
        """
        tracker = ctx.lifespan_context["tracker"]

        queue = await tracker.queues.get(queue_key)

        open_count = await tracker.issues.count(
            query=f'Queue: {queue_key} Resolution: empty()'
        )

        top_issues = await tracker.issues.search(
            query=f'Queue: {queue_key} Resolution: empty() "Sort By": Priority ASC',
            per_page=10,
        )

        return _build_queue_overview(queue, open_count, top_issues)


def _build_issue_overview(
    issue: dict,
    comments: list,
    links: list,
    checklists: list,
    worklogs: list,
) -> str:
    key = issue.get("key", "?")
    summary = issue.get("summary", "")
    status = _extract_display(issue.get("status"))
    priority = _extract_display(issue.get("priority"))
    issue_type = _extract_display(issue.get("type"))
    assignee = _extract_display(issue.get("assignee"))
    author = _extract_display(issue.get("createdBy"))
    created = issue.get("createdAt", "")
    deadline = issue.get("deadline", "")
    sp = issue.get("storyPoints")
    description = issue.get("description", "")
    tags = issue.get("tags", [])
    estimation = issue.get("estimation", "")
    spent = issue.get("spent", "")

    lines = [f"## {key}: {summary}\n"]
    lines.append(f"Status: **{status}**  |  Type: {issue_type}  |  Priority: {priority}")

    if assignee:
        lines.append(f"Assignee: {assignee}")
    if author:
        lines.append(f"Author: {author}  |  Created: {created}")
    if deadline:
        lines.append(f"Deadline: {deadline}")
    if sp is not None:
        lines.append(f"Story Points: {sp}")
    if tags:
        lines.append(f"Tags: {', '.join(tags)}")

    # Transitions
    transitions = issue.get("transitions", [])
    if transitions:
        trans_names = [t.get("display", t.get("id", "?")) for t in transitions]
        lines.append(f"Available transitions: {', '.join(trans_names)}")

    # Description
    if description:
        desc = description[:500]
        if len(description) > 500:
            desc += "..."
        lines.append(f"\n**Description:**\n{desc}")

    # Links
    if links:
        lines.append(f"\n**Links ({len(links)}):**")
        for link in links:
            rel = link.get("type", {})
            rel_name = rel.get("id", "?") if isinstance(rel, dict) else str(rel)
            target = link.get("object", {})
            if isinstance(target, dict):
                t_key = target.get("key", "?")
                t_summary = target.get("display", "")
                t_status = _extract_display(target.get("status"))
                lines.append(f"  -> {rel_name} {t_key} ({t_summary}) [{t_status}]")
            else:
                lines.append(f"  -> {rel_name} {target}")

    # Comments
    if comments:
        lines.append(f"\n**Comments ({len(comments)}):**")
        last = comments[-1] if comments else None
        if last:
            c_author = last.get("createdBy", {})
            if isinstance(c_author, dict):
                c_author = c_author.get("display", "?")
            c_text = last.get("text", "")[:200]
            lines.append(f"  Last from {c_author}:")
            lines.append(f"  {c_text}")

    # Checklist
    if checklists:
        items = checklists if isinstance(checklists, list) else []
        done = sum(1 for i in items if i.get("checked"))
        total = len(items)
        lines.append(f"\n**Checklist ({done}/{total}):**")
        for item in items:
            mark = "x" if item.get("checked") else " "
            text = item.get("text", "?")
            lines.append(f"  [{mark}] {text}")

    # Worklog
    if worklogs:
        lines.append(f"\n**Worklog ({len(worklogs)} entries):**")
        if estimation or spent:
            lines.append(f"  Spent: {spent or '?'}  |  Estimation: {estimation or '?'}")

    lines.append(f"\nhttps://tracker.yandex.ru/{key}")
    return "\n".join(lines)


def _build_queue_overview(queue: dict, open_count, top_issues: list) -> str:
    key = queue.get("key", "?")
    name = queue.get("name", "")
    lead = _extract_display(queue.get("lead"))

    lines = [f"## Queue: {key} — {name}\n"]
    lines.append(f"Lead: {lead}")
    lines.append(f"Open issues: **{open_count}**\n")

    if top_issues:
        lines.append("**Top priority open issues:**")
        for issue in top_issues:
            i_key = issue.get("key", "?")
            i_summary = issue.get("summary", "")
            i_status = _extract_display(issue.get("status"))
            i_priority = _extract_display(issue.get("priority"))
            i_assignee = _extract_display(issue.get("assignee"))
            line = f"- **{i_key}** [{i_status}] {i_summary} (P:{i_priority})"
            if i_assignee:
                line += f" @{i_assignee}"
            lines.append(line)

    return "\n".join(lines)


def _extract_display(obj) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return obj.get("display", obj.get("name", obj.get("key", obj.get("id", str(obj)))))
    return str(obj)
