"""Memory service for rolling summary, context assembly, and tags (ADR 02)."""
import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

PRESETS_PATH = Path(__file__).resolve().parent.parent / "data" / "refusal_presets.json"


class MemoryService:
    def __init__(self, presets_path: Optional[Path] = None):
        self.presets_path = presets_path or PRESETS_PATH

    def build_context_window(
        self,
        old_summary: str,
        past_messages: list[dict[str, Any]],
        current_msg: str,
        limit: int = 6,
    ) -> tuple[str, list[dict[str, str]]]:
        """Assemble context notes and message history for LLM generation."""
        summary = old_summary.strip()
        context_notes = f"Ringkasan riwayat percakapan: {summary}" if summary else ""

        # Take up to limit past messages
        recent = past_messages[-limit:] if len(past_messages) > limit else past_messages
        history_for_llm = [
            {"role": m.get("role", "user"), "content": m.get("raw_content", "")}
            for m in recent
        ]
        history_for_llm.append({"role": "user", "content": current_msg})

        return context_notes, history_for_llm

    def update_rolling_summary(
        self,
        old_summary: str,
        raw_msg: str,
        current_readiness: str,
        current_tone: str,
        route: str,
        max_chars: int = 300,
    ) -> str:
        """Update rolling summary incrementally with clean word/boundary truncation."""
        clean_msg = raw_msg.strip()
        if not old_summary:
            summary = f"Pengguna ({current_readiness}, {current_tone}): {clean_msg[:120]}"
        else:
            summary = f"{old_summary} | User: {clean_msg[:60]} -> Asisten ({route})"

        if len(summary) > max_chars:
            # Clean boundary trim: find first delimiter after truncation point
            cut_idx = len(summary) - max_chars
            tail = summary[cut_idx:]
            # Find first separator '|' or space to start with a clean segment
            sep_pos = tail.find("|")
            if sep_pos != -1 and sep_pos < 40:
                summary = tail[sep_pos + 1:].strip()
            else:
                space_pos = tail.find(" ")
                if space_pos != -1 and space_pos < 20:
                    summary = tail[space_pos + 1:].strip()
                else:
                    summary = tail.strip()

        return summary

    def merge_tags(
        self,
        existing_tags: dict[str, str],
        new_tags: dict[str, str],
    ) -> dict[str, str]:
        """Merge context tags dictionary."""
        return {**existing_tags, **new_tags}

    def load_refusal_presets(self) -> list[dict[str, Any]]:
        """Load 30 offline refusal script presets."""
        try:
            if self.presets_path.exists():
                with open(self.presets_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as exc:
            logger.warning("Failed to load refusal presets: %s", exc)
        return []
