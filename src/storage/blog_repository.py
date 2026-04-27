import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class BlogRepository:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///data/blogs.db")
        self.database_path = self._sqlite_path(self.database_url)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS blogs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    language TEXT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    research_notes TEXT,
                    outline TEXT,
                    editor_notes TEXT,
                    sources TEXT,
                    retrieval_warning TEXT,
                    seo TEXT,
                    tone TEXT,
                    audience TEXT,
                    length TEXT,
                    status TEXT NOT NULL DEFAULT 'draft',
                    created_at TEXT NOT NULL
                )
                """
            )
            self._ensure_column(connection, "blogs", "editor_notes", "TEXT")
            self._ensure_column(connection, "blogs", "sources", "TEXT")
            self._ensure_column(connection, "blogs", "retrieval_warning", "TEXT")
            self._ensure_column(connection, "blogs", "seo", "TEXT")
            self._ensure_column(connection, "blogs", "tone", "TEXT")
            self._ensure_column(connection, "blogs", "audience", "TEXT")
            self._ensure_column(connection, "blogs", "length", "TEXT")

    def create(self, state: dict[str, Any]) -> dict[str, Any]:
        blog = state["blog"]
        created_at = datetime.now(UTC).isoformat()
        values = {
            "topic": state["topic"],
            "language": state.get("current_language"),
            "title": blog["title"],
            "content": blog["content"],
            "research_notes": state.get("research_notes"),
            "outline": state.get("outline"),
            "editor_notes": state.get("editor_notes"),
            "sources": json.dumps(state.get("sources", [])),
            "retrieval_warning": state.get("retrieval_warning"),
            "seo": json.dumps(state.get("seo", {})),
            "tone": state.get("tone"),
            "audience": state.get("audience"),
            "length": state.get("length"),
            "status": "draft",
            "created_at": created_at,
        }

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO blogs (
                    topic, language, title, content, research_notes, outline, editor_notes,
                    sources, retrieval_warning, seo, tone, audience, length, status, created_at
                )
                VALUES (
                    :topic, :language, :title, :content, :research_notes, :outline, :editor_notes,
                    :sources, :retrieval_warning, :seo, :tone, :audience, :length, :status, :created_at
                )
                """,
                values,
            )
            values["id"] = cursor.lastrowid

        return self._deserialize(values)

    def list(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, topic, language, title, content, research_notes, outline,
                       editor_notes, sources, retrieval_warning, seo, tone, audience, length,
                       status, created_at
                FROM blogs
                ORDER BY id DESC
                """
            ).fetchall()

        return [self._deserialize(dict(row)) for row in rows]

    def get(self, blog_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, topic, language, title, content, research_notes, outline,
                       editor_notes, sources, retrieval_warning, seo, tone, audience, length,
                       status, created_at
                FROM blogs
                WHERE id = ?
                """,
                (blog_id,),
            ).fetchone()

        if row is None:
            return None

        return self._deserialize(dict(row))

    def delete(self, blog_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM blogs WHERE id = ?", (blog_id,))

        return cursor.rowcount > 0

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _ensure_column(connection, table_name: str, column_name: str, column_type: str):
        columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        if column_name not in {column["name"] for column in columns}:
            connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")

    @staticmethod
    def _sqlite_path(database_url: str) -> Path:
        if not database_url.startswith("sqlite:///"):
            raise ValueError("Only sqlite:/// DATABASE_URL values are currently supported.")

        return Path(database_url.replace("sqlite:///", "", 1))

    @staticmethod
    def _deserialize(record: dict[str, Any]) -> dict[str, Any]:
        record["seo"] = json.loads(record.get("seo") or "{}")
        record["sources"] = json.loads(record.get("sources") or "[]")
        return record
