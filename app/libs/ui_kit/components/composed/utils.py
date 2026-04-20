from __future__ import annotations

from datetime import datetime


def format_timestamp(ts_str: str) -> str:
    """Format a timestamp string into a readable friendly format."""
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)
        diff = now - dt

        if diff.days == 0:
            if diff.seconds < 60:
                return "Just now"
            if diff.seconds < 3600:
                return f"{diff.seconds // 60}m ago"
            return f"{diff.seconds // 3600}h ago"
        
        if diff.days == 1:
            return "Yesterday"
        if diff.days < 7:
            return f"{diff.days}d ago"
        
        return dt.strftime("%b %d")
    except Exception:
        return ts_str
