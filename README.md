# SQLite Session Manager for Strands Agents

A lightweight, local SQLite-based session manager for Strands agents. Provides a drop-in replacement for S3SessionManager with offline capability and zero cloud dependencies.

## Features

- **Local Storage**: All session data stored in a single SQLite database file
- **Drop-in Replacement**: Compatible with S3SessionManager interface
- **Offline Operation**: No network or cloud dependencies required
- **ACID Transactions**: Reliable data integrity with SQLite
- **Thread-Safe**: WAL mode enabled for concurrent access
- **Zero Configuration**: Works out of the box with sensible defaults

## Installation

```bash
pip install "git+https://github.com/afarntrog/strands-sqlite-session-manager"
```

## Quick Start

```python
from strands import Agent
from strands_sqlite_session_manager import SQLiteSessionManager

# Create agent with SQLite session manager
agent = Agent(
    session_manager=SQLiteSessionManager(
        session_id="my-session",
        db_path="./sessions.db"  # Optional, defaults to ./sessions.db
    )
)

# Use agent normally - sessions are stored locally
response = agent("Hello, how are you?")
```

## Configuration

### Database Path

Configure the database location in three ways:

1. **Constructor parameter** (highest priority):
```python
manager = SQLiteSessionManager(session_id="test", db_path="/path/to/sessions.db")
```

2. **Environment variable**:
```bash
export STRANDS_SQLITE_DB_PATH=/path/to/sessions.db
```

3. **Default**: `./sessions.db` in current directory

### In-Memory Database

For testing or temporary sessions:

```python
manager = SQLiteSessionManager(session_id="test", db_path=":memory:")
```

## Migration from S3SessionManager

Simply replace the import and remove S3-specific parameters:

```python
# Before (S3)
from strands.session import S3SessionManager
manager = S3SessionManager(session_id="test", bucket="my-bucket", prefix="sessions/")

# After (SQLite)
from strands_sqlite_session_manager import SQLiteSessionManager
manager = SQLiteSessionManager(session_id="test", db_path="./sessions.db")
```

All session data and operations remain identical.

## Database Schema

The SQLite database contains four tables:

- **sessions**: Session metadata and data
- **agents**: Agent configurations within sessions
- **messages**: Conversation messages
- **multi_agents**: Multi-agent state data

All tables include automatic timestamps and proper foreign key relationships with cascading deletes.

## License

Apache License 2.0

# Disclaimer
This is strictly a **community** created package. This is not supported/affiliated or built by AWS.
