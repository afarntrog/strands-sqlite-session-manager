"""SQLite session manager implementation."""

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from strands.session import RepositorySessionManager, SessionRepository
from strands.types.exceptions import SessionException
from strands.types.session import Session, SessionAgent, SessionMessage


class SQLiteSessionManager(RepositorySessionManager, SessionRepository):
    """SQLite-based session manager for local storage."""

    def __init__(
        self,
        session_id: str,
        db_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize SQLite session manager.

        Args:
            session_id: Session identifier
            db_path: Path to SQLite database file (default: ./sessions.db or STRANDS_SQLITE_DB_PATH env var)
            **kwargs: Additional arguments passed to parent
        """
        self._db_path = db_path or os.getenv("STRANDS_SQLITE_DB_PATH", "./sessions.db")
        self._conn: sqlite3.Connection | None = None
        self._initialize_db()

        # Initialize parent with self as the repository
        super().__init__(session_id=session_id, session_repository=self, **kwargs)

    def _initialize_db(self) -> None:
        """Initialize database connection and schema."""
        if self._db_path != ":memory:":
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")

        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS agents (
                session_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (session_id, agent_id),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS messages (
                session_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (session_id, agent_id, message_id),
                FOREIGN KEY (session_id, agent_id) REFERENCES agents(session_id, agent_id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS multi_agents (
                session_id TEXT NOT NULL,
                multi_agent_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (session_id, multi_agent_id),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_messages_session_agent ON messages(session_id, agent_id, message_id);
            CREATE INDEX IF NOT EXISTS idx_agents_session ON agents(session_id);
            CREATE INDEX IF NOT EXISTS idx_multi_agents_session ON multi_agents(session_id);
        """)
        self._conn.commit()

    def create_session(self, session: Session) -> None:
        """Create a new session."""
        try:
            data = json.dumps(session.to_dict())
            self._conn.execute(
                "INSERT INTO sessions (session_id, data) VALUES (?, ?)",
                (session.session_id, data),
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            raise SessionException(f"Session {session.session_id} already exists")
        except Exception as e:
            raise SessionException(f"Failed to create session: {e}")

    def read_session(self, session_id: str) -> Session | None:
        """Read a session."""
        cursor = self._conn.execute("SELECT data FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None

        try:
            return Session.from_dict(json.loads(row[0]))
        except Exception as e:
            raise SessionException(f"Failed to read session: {e}")

    def delete_session(self, session_id: str) -> None:
        """Delete a session and all related data."""
        cursor = self._conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        self._conn.commit()
        if cursor.rowcount == 0:
            raise SessionException(f"Session {session_id} not found")

    def create_agent(self, session_id: str, agent: SessionAgent) -> None:
        """Create an agent in a session."""
        try:
            data = json.dumps(agent.to_dict())
            self._conn.execute(
                "INSERT INTO agents (session_id, agent_id, data) VALUES (?, ?, ?)",
                (session_id, agent.agent_id, data),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY" in str(e):
                raise SessionException(f"Session {session_id} not found")
            raise SessionException(f"Agent {agent.agent_id} already exists in session {session_id}")
        except Exception as e:
            raise SessionException(f"Failed to create agent: {e}")

    def read_agent(self, session_id: str, agent_id: str) -> SessionAgent | None:
        """Read an agent from a session."""
        cursor = self._conn.execute(
            "SELECT data FROM agents WHERE session_id = ? AND agent_id = ?",
            (session_id, agent_id),
        )
        row = cursor.fetchone()
        if not row:
            return None

        try:
            return SessionAgent.from_dict(json.loads(row[0]))
        except Exception as e:
            raise SessionException(f"Failed to read agent: {e}")

    def update_agent(self, session_id: str, agent: SessionAgent) -> None:
        """Update an agent in a session."""
        cursor = self._conn.execute(
            "SELECT created_at FROM agents WHERE session_id = ? AND agent_id = ?",
            (session_id, agent.agent_id),
        )
        row = cursor.fetchone()
        if not row:
            raise SessionException(f"Agent {agent.agent_id} not found in session {session_id}")

        try:
            data = json.dumps(agent.to_dict())
            self._conn.execute(
                "UPDATE agents SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE session_id = ? AND agent_id = ?",
                (data, session_id, agent.agent_id),
            )
            self._conn.commit()
        except Exception as e:
            raise SessionException(f"Failed to update agent: {e}")

    def create_message(self, session_id: str, agent_id: str, message: SessionMessage) -> None:
        """Create a message in an agent."""
        try:
            data = json.dumps(message.to_dict())
            self._conn.execute(
                "INSERT INTO messages (session_id, agent_id, message_id, data) VALUES (?, ?, ?, ?)",
                (session_id, agent_id, message.message_id, data),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY" in str(e):
                raise SessionException(f"Agent {agent_id} not found in session {session_id}")
            raise SessionException(f"Message {message.message_id} already exists")
        except Exception as e:
            raise SessionException(f"Failed to create message: {e}")

    def read_message(self, session_id: str, agent_id: str, message_id: int) -> SessionMessage:
        """Read a message from an agent."""
        cursor = self._conn.execute(
            "SELECT data FROM messages WHERE session_id = ? AND agent_id = ? AND message_id = ?",
            (session_id, agent_id, message_id),
        )
        row = cursor.fetchone()
        if not row:
            raise SessionException(f"Message {message_id} not found")

        try:
            return SessionMessage.from_dict(json.loads(row[0]))
        except Exception as e:
            raise SessionException(f"Failed to read message: {e}")

    def update_message(self, session_id: str, agent_id: str, message: SessionMessage) -> None:
        """Update a message in an agent."""
        cursor = self._conn.execute(
            "SELECT created_at FROM messages WHERE session_id = ? AND agent_id = ? AND message_id = ?",
            (session_id, agent_id, message.message_id),
        )
        row = cursor.fetchone()
        if not row:
            raise SessionException(f"Message {message.message_id} not found")

        try:
            data = json.dumps(message.to_dict())
            self._conn.execute(
                "UPDATE messages SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE session_id = ? AND agent_id = ? AND message_id = ?",
                (data, session_id, agent_id, message.message_id),
            )
            self._conn.commit()
        except Exception as e:
            raise SessionException(f"Failed to update message: {e}")

    def list_messages(
        self, session_id: str, agent_id: str, limit: int | None = None, offset: int = 0
    ) -> list[SessionMessage]:
        """List messages for an agent with pagination."""
        query = """
            SELECT data FROM messages 
            WHERE session_id = ? AND agent_id = ? 
            ORDER BY message_id
        """
        params = [session_id, agent_id]

        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        cursor = self._conn.execute(query, params)

        try:
            return [SessionMessage.from_dict(json.loads(row[0])) for row in cursor.fetchall()]
        except Exception as e:
            raise SessionException(f"Failed to list messages: {e}")

    def create_multi_agent(self, session_id: str, multi_agent_id: str, state: dict[str, Any]) -> None:
        """Create multi-agent state."""
        try:
            data = json.dumps(state)
            self._conn.execute(
                "INSERT INTO multi_agents (session_id, multi_agent_id, data) VALUES (?, ?, ?)",
                (session_id, multi_agent_id, data),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as e:
            if "FOREIGN KEY" in str(e):
                raise SessionException(f"Session {session_id} not found")
            raise SessionException(f"Multi-agent {multi_agent_id} already exists")
        except Exception as e:
            raise SessionException(f"Failed to create multi-agent: {e}")

    def read_multi_agent(self, session_id: str, multi_agent_id: str) -> dict[str, Any]:
        """Read multi-agent state."""
        cursor = self._conn.execute(
            "SELECT data FROM multi_agents WHERE session_id = ? AND multi_agent_id = ?",
            (session_id, multi_agent_id),
        )
        row = cursor.fetchone()
        if not row:
            raise SessionException(f"Multi-agent {multi_agent_id} not found")

        try:
            return json.loads(row[0])
        except Exception as e:
            raise SessionException(f"Failed to read multi-agent: {e}")

    def update_multi_agent(self, session_id: str, multi_agent_id: str, state: dict[str, Any]) -> None:
        """Update multi-agent state."""
        cursor = self._conn.execute(
            "SELECT created_at FROM multi_agents WHERE session_id = ? AND multi_agent_id = ?",
            (session_id, multi_agent_id),
        )
        row = cursor.fetchone()
        if not row:
            raise SessionException(f"Multi-agent {multi_agent_id} not found")

        try:
            data = json.dumps(state)
            self._conn.execute(
                "UPDATE multi_agents SET data = ?, updated_at = CURRENT_TIMESTAMP WHERE session_id = ? AND multi_agent_id = ?",
                (data, session_id, multi_agent_id),
            )
            self._conn.commit()
        except Exception as e:
            raise SessionException(f"Failed to update multi-agent: {e}")

    def __del__(self) -> None:
        """Close database connection on cleanup."""
        if self._conn:
            self._conn.close()
