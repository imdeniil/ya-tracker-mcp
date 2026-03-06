from fastmcp import FastMCP


def register_prompts(mcp: FastMCP):

    @mcp.prompt()
    def my_tasks() -> str:
        """Show my active tasks with priorities and deadlines."""
        return """Find and display my active tasks. Use these steps:
1. Call get_myself to get the current user
2. Call search_issues with query: 'Assignee: me() Resolution: empty() "Sort By": Priority ASC, Updated DESC'
3. Present results grouped by priority, showing deadline warnings for tasks due within 3 days.
"""

    @mcp.prompt()
    def create_task_wizard() -> str:
        """Step-by-step task creation wizard with preset selection."""
        return """Help the user create a task step by step:
1. Ask what needs to be done
2. Call list_presets and suggest a matching preset (or offer to create without preset)
3. If using a preset, call get_preset to see rules and template
4. Collect required input values through conversation
5. Show a preview of the task before creating
6. After confirmation, call create_from_preset or create_issue
7. Return the created issue link
"""

    @mcp.prompt()
    def issue_decomposition(issue_key: str) -> str:
        """Decompose an issue into subtasks.

        Args:
            issue_key: Issue key to decompose (e.g. "DEV-123")
        """
        return f"""Decompose issue {issue_key} into subtasks:
1. Call issue_overview for {issue_key} to understand the task
2. Analyze the description, checklist, and comments
3. Propose a breakdown into 3-7 subtasks, each completable in 1-2 days
4. For each subtask show: summary, estimated SP, suggested assignee (use find_assignee)
5. After user approval, create subtasks with link_issues using "is subtask for" relationship
"""

    @mcp.prompt()
    def overdue_report() -> str:
        """Show overdue tasks report."""
        return """Generate an overdue tasks report:
1. Search for overdue tasks: search_issues with query 'Deadline: <today() Resolution: empty() "Sort By": Deadline ASC'
2. Group by queue and assignee
3. For each task show: key, summary, how many days overdue, priority
4. Highlight critical/blocker priority tasks
5. Suggest actions (reassign, extend deadline, escalate)
"""
