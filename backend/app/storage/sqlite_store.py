"""SQLite persistent storage for conversations, messages, and state (ADR 02)."""
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
                """
            )
            conn.commit()

    def create_conversation(
        self,
        conversation_id: str,
        user_id: str,
        readiness_stage: str = "contemplation",
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO conversations (
                    conversation_id, user_id, readiness_stage, summary, context_tags_json, created_at, updated_at
                ) VALUES (?, ?, ?, '', '{}', ?, ?)
                ON CONFLICT(conversation_id) DO UPDATE SET
                    user_id=excluded.user_id,
                    readiness_stage=excluded.readiness_stage,
                    updated_at=excluded.updated_at
                """,
                (conversation_id, user_id, readiness_stage, now, now),
            )
            conn.commit()
        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "readiness_stage": readiness_stage,
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
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM conversations")
            conn.commit()
