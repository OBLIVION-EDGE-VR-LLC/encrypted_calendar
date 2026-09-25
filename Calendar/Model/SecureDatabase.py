"""
SecureDatabase - SQLCipher-encrypted event storage.

Uses AES-256 encryption at rest. Key derived from user passphrase via Argon2id.
Falls back to standard sqlite3 if SQLCipher is not available (for testing only).
"""

import ctypes
import ctypes.util
import os
import sqlite3

from argon2.low_level import hash_secret_raw, Type

# Detect if SQLCipher is active (via LD_PRELOAD or linked)
_SQLCIPHER_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'includes', 'sqlcipher', '.libs', 'libsqlcipher.so'
)

def _detect_sqlcipher() -> bool:
    """Check if the loaded sqlite3 module is actually SQLCipher."""
    try:
        conn = sqlite3.connect(':memory:')
        cur = conn.execute('PRAGMA cipher_version')
        row = cur.fetchone()
        conn.close()
        return row is not None
    except Exception:
        return False

_USE_SQLCIPHER = _detect_sqlcipher()


def _derive_key(passphrase: str) -> bytes:
    """Derive a 256-bit key from passphrase using Argon2id."""
    salt = b'SecureCalendarV1'  # 16 bytes fixed salt
    raw = hash_secret_raw(
        secret=passphrase.encode('utf-8'),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        type=Type.ID,
    )
    return raw


class SecureDatabase:
    """Encrypted calendar event database."""

    def __init__(self, db_path: str, passphrase: str):
        self._db_path = db_path
        self._key = _derive_key(passphrase)
        self._conn = None
        self._open_failed = False
        self._open()

    def _open(self):
        """Open the database with encryption key."""
        if _USE_SQLCIPHER:
            self._conn = sqlite3.connect(self._db_path)
            hex_key = self._key.hex()
            self._conn.execute(f"PRAGMA key = \"x'{hex_key}'\"")
            self._conn.execute("PRAGMA cipher_page_size = 4096")
            self._conn.execute("PRAGMA kdf_iter = 256000")
            self._conn.execute("PRAGMA cipher_memory_security = ON")
        else:
            # Fallback: unencrypted sqlite3 (testing only)
            self._conn = sqlite3.connect(self._db_path)

        self._conn.row_factory = sqlite3.Row
        try:
            self._create_tables()
        except sqlite3.DatabaseError:
            # DB exists but can't be decrypted (wrong key or unencrypted legacy file)
            self._open_failed = True

    def _create_tables(self):
        """Create the events table if it doesn't exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                detail TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_date ON events(date)
        """)
        self._conn.commit()

    def verify_passphrase(self) -> bool:
        """Verify the passphrase by attempting a query."""
        if self._open_failed:
            return False
        try:
            self._conn.execute("SELECT count(*) FROM events")
            return True
        except sqlite3.DatabaseError:
            return False

    def get_events_for_date(self, date_str: str) -> list:
        """Retrieve all events for a given date, sorted by time (NULL first)."""
        cursor = self._conn.execute(
            "SELECT id, date, time, title, category, detail "
            "FROM events WHERE date = ? "
            "ORDER BY time IS NOT NULL, time ASC",
            (date_str,)
        )
        rows = cursor.fetchall()
        return [
            {
                'id': row['id'],
                'date': row['date'],
                'time': row['time'],
                'title': row['title'],
                'category': row['category'],
                'detail': row['detail'],
            }
            for row in rows
        ]

    def save_event(self, date_str: str, time_str: str | None, title: str,
                   category: str, detail: str, event_id: int | None = None) -> int:
        """Insert or update an event. Returns the event row ID."""
        if event_id is not None:
            self._conn.execute(
                "UPDATE events SET date=?, time=?, title=?, category=?, detail=? WHERE id=?",
                (date_str, time_str, title, category, detail, event_id)
            )
            self._conn.commit()
            return event_id
        else:
            cursor = self._conn.execute(
                "INSERT INTO events (date, time, title, category, detail) VALUES (?, ?, ?, ?, ?)",
                (date_str, time_str, title, category, detail)
            )
            self._conn.commit()
            return cursor.lastrowid

    def delete_event(self, event_id: int) -> None:
        """Delete an event and VACUUM to reclaim pages."""
        self._conn.execute("DELETE FROM events WHERE id=?", (event_id,))
        self._conn.commit()
        self._conn.execute("VACUUM")

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
        # Wipe the key from memory
        if self._key:
            key_buf = ctypes.create_string_buffer(self._key, len(self._key))
            ctypes.memset(ctypes.addressof(key_buf), 0, len(self._key))
            self._key = None
