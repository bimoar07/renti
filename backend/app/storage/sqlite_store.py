"""SQLite persistent storage for conversations, messages, state, and readiness events (ADR 02, 06)."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import sqlite3
from typing import Any, Generator, Optional


class SQLiteStore:
    def __init__(self, db_path: str = "renti.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    readiness_stage TEXT NOT NULL DEFAULT 'contemplation',
                    tone TEXT NOT NULL DEFAULT 'standard',
                    summary TEXT NOT NULL DEFAULT '',
                    context_tags_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    raw_content TEXT NOT NULL,
                    canonical_content TEXT NOT NULL DEFAULT '',
                    route TEXT NOT NULL DEFAULT '',
                    policy_action TEXT NOT NULL DEFAULT 'ALLOW',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_messages_conv_id ON messages(conversation_id);

                CREATE TABLE IF NOT EXISTS readiness_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    from_stage TEXT NOT NULL,
                    to_stage TEXT NOT NULL,
                    evidence TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_readiness_events_conv_id ON readiness_events(conversation_id);
                """
            )
            # Safe migration: ensure 'tone' column exists if table was created in older schema
            columns = [row[1] for row in conn.execute("PRAGMA table_info(conversations)").fetchall()]
            if "tone" not in columns:
                conn.execute("ALTER TABLE conversations ADD COLUMN tone TEXT NOT NULL DEFAULT 'standard';")
            conn.commit()

    def create_conversation(
        self,
        conversation_id: str,
        user_id: str,
        readiness_stage: str = "contemplation",
        tone: str = "standard",
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO conversations (
                    conversation_id, user_id, readiness_stage, tone, summary, context_tags_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, '', '{}', ?, ?)
                ON CONFLICT(conversation_id) DO UPDATE SET
                    user_id=excluded.user_id,
                    readiness_stage=excluded.readiness_stage,
                    tone=excluded.tone,
                    updated_at=excluded.updated_at
                """,
                (conversation_id, user_id, readiness_stage, tone, now, now),
            )
            conn.commit()
        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "readiness_stage": readiness_stage,
            "tone": tone,
            "created_at": now,
        }

    def get_conversation(self, conversation_id: str) -> Optional[dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM conversations WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()
            if not row:
                return None
            data = dict(row)
            if "tone" not in data or data["tone"] is None:
                data["tone"] = "standard"
            try:
                data["context_tags"] = json.loads(data.get("context_tags_json", "{}"))
            except Exception:
                data["context_tags"] = {}
            return data

    def conversation_exists(self, conversation_id: str) -> bool:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM conversations WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()
            return row is not None

    def update_readiness(self, conversation_id: str, readiness_stage: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE conversations
                SET readiness_stage = ?, updated_at = ?
                WHERE conversation_id = ?
                """,
                (readiness_stage, now, conversation_id),
            )
            conn.commit()

    def update_tone(self, conversation_id: str, tone: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE conversations
                SET tone = ?, updated_at = ?
                WHERE conversation_id = ?
                """,
                (tone, now, conversation_id),
            )
            conn.commit()

    def update_summary_and_tags(
        self,
        conversation_id: str,
        summary: str,
        context_tags: dict[str, str],
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        tags_json = json.dumps(context_tags)
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE conversations
                SET summary = ?, context_tags_json = ?, updated_at = ?
                WHERE conversation_id = ?
                """,
                (summary, tags_json, now, conversation_id),
            )
            conn.commit()

    def record_readiness_event(
        self,
        conversation_id: str,
        from_stage: str,
        to_stage: str,
        evidence: str = "",
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO readiness_events (
                    conversation_id, from_stage, to_stage, evidence, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (conversation_id, from_stage, to_stage, evidence, now),
            )
            event_id = cursor.lastrowid
            conn.commit()
        return {
            "id": event_id,
            "conversation_id": conversation_id,
            "from_stage": from_stage,
            "to_stage": to_stage,
            "evidence": evidence,
            "created_at": now,
        }

    def get_readiness_events(self, conversation_id: str) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, conversation_id, from_stage, to_stage, evidence, created_at
                FROM readiness_events
                WHERE conversation_id = ?
                ORDER BY id ASC
                """,
                (conversation_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def add_message(
        self,
        conversation_id: str,
        role: str,
        raw_content: str,
        canonical_content: str = "",
        route: str = "",
        policy_action: str = "ALLOW",
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO messages (
                    conversation_id, role, raw_content, canonical_content, route, policy_action, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    role,
                    raw_content,
                    canonical_content or raw_content,
                    route,
                    policy_action,
                    now,
                ),
            )
            conn.commit()

    def get_messages(self, conversation_id: str, limit: int = 50) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT role, raw_content, canonical_content, route, policy_action, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (conversation_id, limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def clear_all(self) -> None:
        """Utility for test suites."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM readiness_events")
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM conversations")
            conn.commit()
