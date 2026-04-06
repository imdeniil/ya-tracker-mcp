import json
import os

import yaml
from fastmcp import FastMCP, Context

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "ya-tracker-mcp")
TEAM_PATH = os.path.join(CACHE_DIR, "team.yaml")


def _load_team() -> list[dict]:
    if not os.path.exists(TEAM_PATH):
        return []
    with open(TEAM_PATH) as f:
        data = yaml.safe_load(f)
    return data.get("team", []) or []


def register_team_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_team(
        ctx: Context,
        output_format: str = "text",
    ) -> str:
        """List team members from the team directory.

        Args:
            output_format: Response format: "text" (default, markdown) or "json"
        """
        team = _load_team()
        if not team:
            if output_format == "json":
                return "[]"
            return f"No team members configured. Edit {TEAM_PATH} to add your team."

        if output_format == "json":
            return json.dumps(team, ensure_ascii=False, default=str)

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
        output_format: str = "text",
    ) -> str:
        """Get team member details.

        Args:
            login: Member login
            output_format: Response format: "text" (default, markdown) or "json"
        """
        team = _load_team()
        member = next((m for m in team if m.get("login") == login), None)
        if not member:
            return f"Team member '{login}' not found."

        if output_format == "json":
            return json.dumps(member, ensure_ascii=False, default=str)

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
        output_format: str = "text",
    ) -> str:
        """Find a team member by area of expertise or queue.

        Args:
            area: Area keyword (e.g. "API", "React", "testing")
            queue: Queue key (e.g. "DEV")
            output_format: Response format: "text" (default, markdown) or "json"
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

        if output_format == "json":
            return json.dumps([m for _, m in matches], ensure_ascii=False, default=str)

        lines = ["Suggested assignees:\n"]
        for score, m in matches:
            login = m.get("login", "?")
            name = m.get("name", "")
            role = m.get("role", "")
            areas = ", ".join(m.get("areas", []))
            lines.append(f"- **{name}** (@{login}) — {role} [{areas}]")
        return "\n".join(lines)
