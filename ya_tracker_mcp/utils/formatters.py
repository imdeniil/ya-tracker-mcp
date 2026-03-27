from typing import Any, List, Dict, Optional

def _extract_display(val: Any) -> str:
    """Extract a human-readable string from a field value."""
    if val is None:
        return ""
    if isinstance(val, dict):
        # Prefer display, then name, then key, then id
        for key in ["display", "name", "key", "id"]:
            if key in val:
                return str(val[key])
        return str(val)
    if isinstance(val, list):
        return ", ".join([_extract_display(i) for i in val])
    return str(val)

def format_mcp_item(
    item: Dict[str, Any],
    title: str,
    basic_fields: List[str],
    extra_fields: Optional[List[str]] = None,
    key_field: str = "id",
    name_field: str = "name",
    template: str = "**{key}**: {name}\n{basics}",
    description_field: Optional[str] = "description"
) -> str:
    """
    Standard formatter for a single Yandex Tracker entity.
    """
    key_val = item.get(key_field, "?")
    name_val = _extract_display(item.get(name_field, ""))
    
    # Build basics section
    lines = []
    for f in basic_fields:
        if f in item and f not in [key_field, name_field, description_field]:
            lines.append(f"**{f}**: {_extract_display(item[f])}")
    
    basics_str = "\n".join(lines)
    
    # Main header
    res = template.format(
        key=key_val,
        name=name_val,
        basics=basics_str
    ).strip() + "\n"
    
    # Extra fields
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

    # Description
    if description_field and item.get(description_field):
        desc = item[description_field]
        if len(desc) > 1000:
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
    template: str = "- [{key}] **{name}** ({basics})"
) -> str:
    """
    Standard formatter for Yandex Tracker entity lists.
    """
    if not data:
        return f"No {title.lower()} found."

    lines = [f"{title}:\n"]
    for item in data:
        key_val = item.get(key_field, "?")
        name_val = _extract_display(item.get(name_field, ""))
        
        # Build basics section
        basics_list = []
        for f in basic_fields:
            if f in item and f not in [key_field, name_field]:
                basics_list.append(f"{f}: {_extract_display(item[f])}")
        
        basics_str = ", ".join(basics_list)
        
        # Format main line
        try:
            line = template.format(
                key=key_val,
                name=name_val,
                basics=basics_str
            )
        except KeyError:
            line = f"- [{key_val}] **{name_val}** ({basics_str})"
            
        # Build extras section
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
