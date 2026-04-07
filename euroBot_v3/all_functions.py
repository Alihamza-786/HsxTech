from typing import Any, Dict, List, Optional, Tuple, TypedDict


# -----------------------------
# Token-efficient history format
# -----------------------------
def _squash_ws(s: str) -> str:
    return " ".join((s or "").split())


def _truncate(s: str, max_chars: int) -> str:
    s = _squash_ws(s)
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 1].rstrip() + "…"


def format_history_compact(
    history: List[Dict[str, Any]],
    max_items: int = 5,
    keep_sql_last_n: int = 2,
    q_chars: int = 1400,
    sql_chars: int = 2600,
) -> str:
    """
    Very compact:
      H1 Q: ...
      H2 Q: ...
      H4 Q: ... | SQL: ...
      H5 Q: ... | SQL: ...
    """
    if not history:
        return "H: (none)"

    history = history[-max_items:]
    n = len(history)
    sql_cutoff = max(0, n - keep_sql_last_n)

    lines: List[str] = []
    for i, h in enumerate(history, start=1):
        q = _truncate(h.get("question", ""), q_chars)
        sql = h.get("sql") or ""
        if i > sql_cutoff and sql:
            sql = _truncate(sql, sql_chars)
            lines.append(f"H{i} Q: {q} | SQL: {sql}")
        else:
            lines.append(f"H{i} Q: {q}")

    return "\n".join(lines)


def make_history_user_block(state: Dict[str, Any], keep_sql_last_n=2) -> str:
    # Keep this block short and consistent so the model learns it.
    return format_history_compact(
        history=state.get("history") or [],
        max_items=5,
        keep_sql_last_n=keep_sql_last_n,
        q_chars=140,
        sql_chars=260,
    )


def extract_text(resp):
    if isinstance(resp.content, str):
        return resp.content.strip()

    if isinstance(resp.content, list):
        texts = []
        for block in resp.content:
            if isinstance(block, dict):
                if block.get("type") == "output_text":
                    texts.append(block.get("text", ""))
                elif block.get("type") == "message":
                    for sub in block.get("content", []):
                        if sub.get("type") == "output_text":
                            texts.append(sub.get("text", ""))
        return "".join(texts).strip()

    return ""
