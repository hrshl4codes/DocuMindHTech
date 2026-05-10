"""
SQLite persistence for document and chunk metadata.
Vectors live in Pinecone; this stores everything else so documents
survive server restarts.
"""

import sqlite3
import json
import time
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.getenv("DB_PATH", "documind.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist. Safe to call on every startup."""
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS documents (
                id          TEXT PRIMARY KEY,
                title       TEXT,
                source      TEXT,
                doc_type    TEXT,
                upload_time REAL,
                word_count  INTEGER,
                char_count  INTEGER
            );

            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id    TEXT PRIMARY KEY,
                doc_id      TEXT NOT NULL,
                position    INTEGER,
                section     TEXT,
                text        TEXT,
                FOREIGN KEY (doc_id) REFERENCES documents(id)
            );

            CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
        """)


# ── documents ─────────────────────────────────────────────────────────────────

def save_document(doc: Dict[str, Any]):
    with _connect() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO documents
               (id, title, source, doc_type, upload_time, word_count, char_count)
               VALUES (:id, :title, :source, :doc_type, :upload_time, :word_count, :char_count)""",
            {
                "id":          doc["id"],
                "title":       doc.get("title", ""),
                "source":      doc.get("source", ""),
                "doc_type":    doc.get("doc_type", "text"),
                "upload_time": doc.get("upload_time", time.time()),
                "word_count":  doc.get("word_count", 0),
                "char_count":  doc.get("char_count", 0),
            },
        )


def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()
    return dict(row) if row else None


def list_documents() -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, title, source, upload_time FROM documents ORDER BY upload_time DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def delete_document(doc_id: str):
    with _connect() as conn:
        conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))


# ── chunks ────────────────────────────────────────────────────────────────────

def save_chunks(chunks: List[Dict[str, Any]]):
    with _connect() as conn:
        conn.executemany(
            """INSERT OR REPLACE INTO chunks (chunk_id, doc_id, position, section, text)
               VALUES (:chunk_id, :doc_id, :position, :section, :text)""",
            [
                {
                    "chunk_id": c["chunk_id"],
                    "doc_id":   c["doc_id"],
                    "position": c.get("position", 0),
                    "section":  c.get("section", ""),
                    "text":     c.get("text", ""),
                }
                for c in chunks
            ],
        )


def get_chunks(doc_id: str) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM chunks WHERE doc_id = ? ORDER BY position", (doc_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def count_chunks(doc_id: str) -> int:
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM chunks WHERE doc_id = ?", (doc_id,)
        ).fetchone()
    return row[0] if row else 0
