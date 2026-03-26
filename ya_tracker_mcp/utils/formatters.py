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
    
    Args:
        data: List of objects from API/Cache
        title: Title of the list
        basic_fields: Fields to show in the 'basics' section
        extra_fields: Additional fields from user (supports ["all"])
        key_field: Field to use as ID (usually 'id' or 'key')
        name_field: Field to use as main title
        template: Python format string for the main line
    """
    if not data:
        return f"No {title.lower()} found."

    lines = [f"{title}:\n"]
    for item in data:
        key_val = item.get(key_field, "?")
        name_val = _extract_display(item.get(name_field, ""))
        
        # Build basics section (fields shown in brackets/parentheses)
        basics_list = []
        for f in basic_fields:
            if f in item and f not in [key_field, name_field]:
                basics_list.append(f"{f}: {_extract_display(item[f])}")
        
        basics_str = ", ".join(basics_list)
        
        # Format the main part of the line
        try:
            line = template.format(
                key=key_val,
                name=name_val,
                basics=basics_str
            )
        except KeyError:
            # Fallback if template is incompatible
            line = f"- [{key_val}] **{name_val}** ({basics_str})"
            
        # Build extras section (piped fields)
        if extra_fields:
            fields_to_show = extra_fields
            if "all" in extra_fields:
                # Exclude what's already visible or purely technical
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
