import json
from typing import Any, List, Dict, Optional


def _extract_display(val: Any) -> str:
    """Extract a human-readable string from a field value."""
    if val is None:
        return ""
    if isinstance(val, dict):
        for key in ["display", "name", "key", "id"]:
            if key in val:
                return str(val[key])
        return str(val)
    if isinstance(val, list):
        return ", ".join([_extract_display(i) for i in val])
    return str(val)


def _extract_json_val(val: Any) -> Any:
    """Extract a clean value for JSON output."""
    if val is None:
        return None
    if isinstance(val, dict):
        for key in ["display", "name", "key", "id"]:
            if key in val:
                return val[key]
        return val
    if isinstance(val, list):
        return [_extract_json_val(i) for i in val]
    return val


def _build_json_item(
    item: Dict[str, Any],
    basic_fields: List[str],
    extra_fields: Optional[List[str]],
    key_field: str,
    name_field: str,
    description_field: Optional[str],
    full_description: bool,
) -> Dict[str, Any]:
    """Build a clean dict for JSON output."""
    result = {}
    result[key_field] = item.get(key_field, "?")
    if name_field in item:
        result[name_field] = _extract_json_val(item.get(name_field))

    for f in basic_fields:
        if f in item and f not in [key_field, name_field, description_field]:
            result[f] = _extract_json_val(item[f])

    if extra_fields:
        fields_to_show = extra_fields
        if "all" in extra_fields:
            excluded = [key_field, name_field, description_field, "self", "version"] + basic_fields
            fields_to_show = [k for k in item.keys() if k not in excluded]
        for f in fields_to_show:
            if f in item and f not in [key_field, name_field, description_field] and f not in basic_fields:
                result[f] = _extract_json_val(item[f])

    if description_field and item.get(description_field):
        desc = item[description_field]
        if not full_description and len(desc) > 1000:
            desc = desc[:1000] + "..."
        result[description_field] = desc

    return result


def format_mcp_item(
    item: Dict[str, Any],
    title: str,
    basic_fields: List[str],
    extra_fields: Optional[List[str]] = None,
    key_field: str = "id",
    name_field: str = "name",
    template: str = "**{key}**: {name}\n{basics}",
    description_field: Optional[str] = "description",
    output_format: str = "text",
    full_description: bool = False,
) -> str:
    """Standard formatter for a single Yandex Tracker entity."""
    if output_format == "json":
        obj = _build_json_item(item, basic_fields, extra_fields, key_field, name_field, description_field, full_description)
        return json.dumps(obj, ensure_ascii=False, default=str)

    key_val = item.get(key_field, "?")
    name_val = _extract_display(item.get(name_field, ""))

    lines = []
    for f in basic_fields:
        if f in item and f not in [key_field, name_field, description_field]:
            lines.append(f"**{f}**: {_extract_display(item[f])}")

    basics_str = "\n".join(lines)

    res = template.format(
        key=key_val,
        name=name_val,
        basics=basics_str
    ).strip() + "\n"

    if extra_fields:
        fields_to_show = extra_fields
        if "all" in extra_fields:
            excluded = [key_field, name_field, description_field, "self", "version"] + basic_fields
            fields_to_show = [k for k in item.keys() if k not in excluded]

        extras = []
        for f in fields_to_show:
            if f in item and f not in [key_field, name_field, description_field] and f not in basic_fields:
                extras.append(f"**{f}**: {_extract_display(item[f])}")

        if extras:
            res += "\n" + "\n".join(extras) + "\n"

    if description_field and item.get(description_field):
        desc = item[description_field]
        if not full_description and len(desc) > 1000:
            desc = desc[:1000] + "..."
        res += f"\nDescription:\n{desc}\n"

    return res.strip()


def format_mcp_list(
    data: List[Dict[str, Any]],
    title: str,
    basic_fields: List[str],
    extra_fields: Optional[List[str]] = None,
    key_field: str = "id",
    name_field: str = "name",
    template: str = "- [{key}] **{name}** ({basics})",
    output_format: str = "text",
    full_description: bool = False,
) -> str:
    """Standard formatter for Yandex Tracker entity lists."""
    if not data:
        if output_format == "json":
            return "[]"
        return f"No {title.lower()} found."

    if output_format == "json":
        items = [
            _build_json_item(item, basic_fields, extra_fields, key_field, name_field, None, full_description)
            for item in data
        ]
        return json.dumps(items, ensure_ascii=False, default=str)

    lines = [f"{title}:\n"]
    for item in data:
        key_val = item.get(key_field, "?")
        name_val = _extract_display(item.get(name_field, ""))

        basics_list = []
        for f in basic_fields:
            if f in item and f not in [key_field, name_field]:
                basics_list.append(f"{f}: {_extract_display(item[f])}")

        basics_str = ", ".join(basics_list)

        try:
            line = template.format(
                key=key_val,
                name=name_val,
                basics=basics_str
            )
        except KeyError:
            line = f"- [{key_val}] **{name_val}** ({basics_str})"

        if extra_fields:
            fields_to_show = extra_fields
            if "all" in extra_fields:
                excluded = [key_field, name_field, "self", "version"] + basic_fields
                fields_to_show = [k for k in item.keys() if k not in excluded]

            extras_list = []
            for f in fields_to_show:
                if f in item and f not in [key_field, name_field] and f not in basic_fields:
                    val = _extract_display(item[f])
                    extras_list.append(f"{f}: {val}")

            if extras_list:
                line += f" | {', '.join(extras_list)}"

        lines.append(line)

    return "\n".join(lines)
