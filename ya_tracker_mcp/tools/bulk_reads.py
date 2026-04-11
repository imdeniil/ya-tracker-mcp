import asyncio
import json

from fastmcp import FastMCP, Context


def register_bulk_reads_tools(mcp: FastMCP):

    @mcp.tool()
    async def bulk_list_links(
        ctx: Context,
        issue_keys: list[str],
        link_types: list[str] | None = None,
        include_closed: bool = True,
        compact: bool = True,
        max_concurrency: int = 10,
        output_format: str = "text",
    ) -> str:
        """Fetch links for multiple issues in a single call (parallel fan-out).

        Use this instead of calling list_links N times — returns one compact
        structure instead of N separate tool result blocks. Ideal for flows
        like "my tasks" where you need links for many issues at once.

        Args:
            issue_keys: List of issue keys (e.g. ["DEV-1", "DEV-2", "DEV-3"])
            link_types: Optional filter by link type id (e.g. ["subtask", "relates",
                "depends on"]). If None, returns all link types.
            include_closed: If False, exclude links whose target issue has a resolution.
                Default: True.
            compact: If True (default), each link is reduced to {key, display, type,
                direction, status} — cuts ~70% of bytes vs full objects. Set False to
                get raw API objects.
            max_concurrency: Max parallel API requests. Default: 10.
            output_format: "text" (default, grouped markdown) or "json" (structured).

        Returns:
            text: Grouped by issue with compact one-liners.
            json: {"ISSUE-1": [links...], "ISSUE-2": [...], "_errors": {...}}
        """
        tracker = ctx.lifespan_context["tracker"]
        sem = asyncio.Semaphore(max_concurrency)

        async def fetch_one(key: str) -> tuple[str, list | None, str | None]:
            async with sem:
                try:
                    links = await tracker.issues.links.list(key)
                    return key, links or [], None
                except Exception as e:
                    return key, None, f"{type(e).__name__}: {e}"

        results = await asyncio.gather(*[fetch_one(k) for k in issue_keys])

        data: dict = {}
        errors: dict = {}
        for key, links, err in results:
            if err is not None:
                errors[key] = err
                continue
            if links is None:
                data[key] = []
                continue

            filtered = []
            for link in links:
                if link_types and not _link_type_matches(link, link_types):
                    continue
                if not include_closed and _link_target_closed(link):
                    continue
                filtered.append(_compact_link(link) if compact else link)

            data[key] = filtered

        if output_format == "json":
            out = dict(data)
            if errors:
                out["_errors"] = errors
            return json.dumps(out, ensure_ascii=False, default=str)

        return _format_bulk_links_text(data, errors)


def _link_type_matches(link: dict, link_types: list[str]) -> bool:
    t = link.get("type")
    if isinstance(t, dict):
        type_id = t.get("id") or t.get("key") or ""
    else:
        type_id = str(t) if t else ""
    return type_id in link_types


def _link_target_closed(link: dict) -> bool:
    target = link.get("object")
    if not isinstance(target, dict):
        return False
    return bool(target.get("resolution"))


def _compact_link(link: dict) -> dict:
    t = link.get("type")
    if isinstance(t, dict):
        type_id = t.get("id") or t.get("key") or ""
    else:
        type_id = str(t) if t else ""

    raw_target = link.get("object")
    target: dict = raw_target if isinstance(raw_target, dict) else {}
    target_key = target.get("key", "?")
    target_display = target.get("display") or target.get("summary") or ""

    status = target.get("status")
    if isinstance(status, dict):
        status_id = status.get("key") or status.get("display") or ""
    else:
        status_id = str(status) if status else ""

    return {
        "key": target_key,
        "display": target_display,
        "type": type_id,
        "direction": link.get("direction", ""),
        "status": status_id,
    }


def _format_bulk_links_text(data: dict, errors: dict) -> str:
    lines: list[str] = []
    total_links = sum(len(v) for v in data.values())
    lines.append(f"Bulk links for {len(data)} issues ({total_links} links total):\n")

    for key, links in data.items():
        if not links:
            lines.append(f"**{key}** — no links")
            continue
        lines.append(f"**{key}** ({len(links)}):")
        for link in links:
            lines.append(f"  {_format_one_line(link)}")

    if errors:
        lines.append(f"\n**Errors ({len(errors)}):**")
        for k, e in errors.items():
            lines.append(f"- {k}: {e}")

    return "\n".join(lines)


def _format_one_line(link: dict) -> str:
    # Compact dict (from _compact_link)
    if "key" in link and "type" in link and "direction" in link:
        arrow = "→" if link.get("direction") == "outward" else "←"
        status = f" [{link['status']}]" if link.get("status") else ""
        display = f" {link['display']}" if link.get("display") else ""
        return f"{arrow} {link['type']} {link['key']}{status}{display}"

    # Raw API link (compact=False) — fallback to minimal rendering
    t = link.get("type")
    type_id = t.get("id", "?") if isinstance(t, dict) else str(t)
    direction = link.get("direction", "")
    arrow = "→" if direction == "outward" else "←"
    raw_target = link.get("object")
    target: dict = raw_target if isinstance(raw_target, dict) else {}
    target_key = target.get("key", "?")
    target_display = target.get("display") or target.get("summary") or ""
    return f"{arrow} {type_id} {target_key} {target_display}"
