import os

import yaml
from fastmcp import FastMCP, Context

PRESETS_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "presets.yaml")


def _load_presets() -> dict:
    if not os.path.exists(PRESETS_PATH):
        return {}
    with open(PRESETS_PATH) as f:
        data = yaml.safe_load(f)
    return data.get("presets", {}) if data else {}


def _save_presets(presets: dict):
    os.makedirs(os.path.dirname(PRESETS_PATH), exist_ok=True)
    with open(PRESETS_PATH, "w") as f:
        yaml.dump({"presets": presets}, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


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
        extra_fields: dict | None = None,
    ) -> str:
        """Create an issue from a preset template.

        Args:
            preset_name: Preset key (from list_presets)
            queue: Queue key (e.g. "DEV")
            input_values: Dict of template placeholders (e.g. {"description": "...", "steps": "..."})
            overrides: Optional dict to override preset params (e.g. {"priority": "normal"})
            extra_fields: Additional/custom/local fields as dict
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

        # Handle special mappings and formatting
        if "type" in params:
            kwargs["issue_type"] = params.pop("type")
        if "sprint" in params:
            kwargs["sprint"] = [{"id": int(params.pop("sprint"))}]

        # Pass all remaining params (priority, assignee, tags, components, parent, etc.)
        kwargs.update(params)

        # Explicit extra_fields take precedence
        if extra_fields:
            kwargs.update(extra_fields)

        summary = input_values.get("summary", input_values.get("what", input_values.get("description", "")[:100]))

        issue = await tracker.issues.create(
            summary=summary,
            queue=queue,
            **kwargs,
        )

        key = issue.get("key", "?")
        return f"Issue **{key}** created from preset '{preset_name}'.\nhttps://tracker.yandex.ru/{key}"

    @mcp.tool()
    async def add_preset(
        ctx: Context,
        preset_name: str,
        name: str,
        params: dict | None = None,
        description_template: str | None = None,
        rules: list[str] | None = None,
        description: str | None = None,
        notes: str | None = None,
    ) -> str:
        """Add or update a task preset.

        Args:
            preset_name: Preset key (e.g. "bug_report")
            name: Human-readable preset name
            params: Default issue params (e.g. {"type": "bug", "priority": "critical"}). Supports all fields from create_issue.
            description_template: Template with {input.field} placeholders
            rules: List of rules for the AI assistant
            description: Short description of the preset
            notes: Additional notes
        """
        presets = _load_presets()

        preset = {"name": name}
        if description:
            preset["description"] = description
        if params:
            preset["params"] = params
        if description_template:
            preset["description_template"] = description_template
        if rules:
            preset["rules"] = rules
        if notes:
            preset["notes"] = notes

        action = "updated" if preset_name in presets else "added"
        presets[preset_name] = preset
        _save_presets(presets)

        return f"Preset '{preset_name}' {action}. Total presets: {len(presets)}."

    @mcp.tool()
    async def remove_preset(
        ctx: Context,
        preset_name: str,
    ) -> str:
        """Remove a task preset.

        Args:
            preset_name: Preset key to remove (from list_presets)
        """
        presets = _load_presets()

        if preset_name not in presets:
            return f"Preset '{preset_name}' not found. Use list_presets to see available presets."

        del presets[preset_name]
        _save_presets(presets)

        return f"Preset '{preset_name}' removed. Remaining presets: {len(presets)}."
