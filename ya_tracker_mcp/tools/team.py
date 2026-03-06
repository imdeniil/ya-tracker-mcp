import os

import yaml
from fastmcp import FastMCP, Context

TEAM_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "team.yaml")


def _load_team() -> list[dict]:
    with open(TEAM_PATH) as f:
        data = yaml.safe_load(f)
    return data.get("team", []) or []


def register_team_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_team(ctx: Context) -> str:
        """List team members from the team directory."""
        team = _load_team()
        if not team:
            return "No team members configured. Edit config/team.yaml to add your team."

        lines = ["Team directory:\n"]
        for m in team:
            login = m.get("login", "?")
            name = m.get("name", "")
            role = m.get("role", "")
            lines.append(f"- **{name}** (@{login}) — {role}")
        return "\n".join(lines)

    @mcp.tool()
    async def get_team_member(
        ctx: Context,
        login: str,
    ) -> str:
        """Get team member details.

        Args:
            login: Member login
        """
        team = _load_team()
        member = next((m for m in team if m.get("login") == login), None)
        if not member:
            return f"Team member '{login}' not found."

        lines = [f"**{member.get('name', login)}** (@{login})"]
        lines.append(f"Role: {member.get('role', '?')}")

        areas = member.get("areas", [])
        if areas:
            lines.append(f"Areas: {', '.join(areas)}")

        queues = member.get("queues", [])
        if queues:
            lines.append(f"Queues: {', '.join(queues)}")

        notes = member.get("notes", "")
        if notes:
            lines.append(f"Notes: {notes}")

        return "\n".join(lines)

    @mcp.tool()
    async def find_assignee(
        ctx: Context,
        area: str | None = None,
        queue: str | None = None,
    ) -> str:
        """Find a team member by area of expertise or queue.

        Args:
            area: Area keyword (e.g. "API", "React", "testing")
            queue: Queue key (e.g. "DEV")
        """
        team = _load_team()
        if not team:
            return "No team members configured."

        matches = []
        for m in team:
            score = 0
            if area:
                for a in m.get("areas", []):
                    if area.lower() in a.lower():
                        score += 2
            if queue:
                if queue.upper() in [q.upper() for q in m.get("queues", [])]:
                    score += 1
            if score > 0:
                matches.append((score, m))

        matches.sort(key=lambda x: x[0], reverse=True)

        if not matches:
            return f"No team members found for area='{area}', queue='{queue}'."

        lines = ["Suggested assignees:\n"]
        for score, m in matches:
            login = m.get("login", "?")
            name = m.get("name", "")
            role = m.get("role", "")
            areas = ", ".join(m.get("areas", []))
            lines.append(f"- **{name}** (@{login}) — {role} [{areas}]")
        return "\n".join(lines)
