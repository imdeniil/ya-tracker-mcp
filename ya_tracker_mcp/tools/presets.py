import os

import yaml
from fastmcp import FastMCP, Context

PRESETS_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "presets.yaml")


def _load_presets() -> dict:
    with open(PRESETS_PATH) as f:
        data = yaml.safe_load(f)
    return data.get("presets", {})


def register_preset_tools(mcp: FastMCP):

    @mcp.tool()
    async def list_presets(ctx: Context) -> str:
        """List available task presets with their descriptions."""
        presets = _load_presets()
        if not presets:
            return "No presets configured. Edit config/presets.yaml to add presets."

        lines = ["Available presets:\n"]
        for key, p in presets.items():
            name = p.get("name", key)
            desc = p.get("description", "")
            lines.append(f"- **{key}** — {name}: {desc}")
        return "\n".join(lines)

    @mcp.tool()
    async def get_preset(
        ctx: Context,
        preset_name: str,
    ) -> str:
        """Get preset details: params, template, and rules.

        Args:
            preset_name: Preset key (from list_presets)
        """
        presets = _load_presets()
        preset = presets.get(preset_name)
        if not preset:
            return f"Preset '{preset_name}' not found. Use list_presets to see available presets."

        lines = [f"**{preset.get('name', preset_name)}**\n"]

        params = preset.get("params", {})
        if params:
            lines.append("Parameters:")
            for k, v in params.items():
                lines.append(f"  {k}: {v}")

        template = preset.get("description_template", "")
        if template:
            lines.append(f"\nTemplate:\n{template}")

        rules = preset.get("rules", [])
        if rules:
            lines.append("Rules:")
            for r in rules:
                lines.append(f"  - {r}")

        notes = preset.get("notes", "")
        if notes:
            lines.append(f"\nNotes: {notes}")

        return "\n".join(lines)

    @mcp.tool()
    async def create_from_preset(
        ctx: Context,
        preset_name: str,
        queue: str,
        input_values: dict,
        overrides: dict | None = None,
    ) -> str:
        """Create an issue from a preset template.

        Args:
            preset_name: Preset key (from list_presets)
            queue: Queue key (e.g. "DEV")
            input_values: Dict of template placeholders (e.g. {"description": "...", "steps": "..."})
            overrides: Optional dict to override preset params (e.g. {"priority": "normal"})
        """
        presets = _load_presets()
        preset = presets.get(preset_name)
        if not preset:
            return f"Preset '{preset_name}' not found."

        tracker = ctx.lifespan_context["tracker"]

        params = dict(preset.get("params", {}))
        if overrides:
            params.update(overrides)

        # Build description from template
        template = preset.get("description_template", "")
        description = template
        for key, value in input_values.items():
            description = description.replace(f"{{input.{key}}}", str(value))

        kwargs = {"description": description}

        if "type" in params:
            kwargs["issue_type"] = params.pop("type")
        if "priority" in params:
            kwargs["priority"] = params.pop("priority")
        if "assignee" in params:
            kwargs["assignee"] = params.pop("assignee")
        if "tags" in params:
            kwargs["tags"] = params.pop("tags")
        if "components" in params:
            kwargs["components"] = params.pop("components")
        if "sprint" in params:
            kwargs["sprint"] = params.pop("sprint")

        summary = input_values.get("summary", input_values.get("what", input_values.get("description", "")[:100]))

        issue = await tracker.issues.create(
            summary=summary,
            queue=queue,
            **kwargs,
        )

        key = issue.get("key", "?")
        return f"Issue **{key}** created from preset '{preset_name}'.\nhttps://tracker.yandex.ru/{key}"
