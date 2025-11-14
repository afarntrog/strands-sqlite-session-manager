# SQLite Session Manager Examples

This directory contains cookbook examples demonstrating how to use the `strands_sqlite_session_manager` package with Strands agents.

## Examples Overview

### 01_basic_usage.py
**Basic Usage and Configuration**
- Creating a session manager with custom database path
- Basic conversation with automatic persistence
- Resuming previous sessions
- Using environment variables for configuration
- In-memory database for temporary sessions

### 02_multi_agent.py
**Multi-Agent Workflows**
- Multiple agents sharing a session
- Agent-to-agent conversations (interview simulation)
- Collaborative workflows (researcher, writer, reviewer)
- Agent handoff patterns (support escalation)
- Shared context between agents

### 03_streaming_and_tools.py
**Streaming and Tool Integration**
- Streaming responses with persistence
- Using tools with session management
- Async/await patterns with streaming
- Stateful tools with session persistence
- Parallel tool execution

### 04_session_management.py
**Advanced Session Management**
- Complete session lifecycle management
- Error handling and recovery
- Multiple database organization
- Session migration patterns
- Cleanup and maintenance
- Concurrent access handling
- Backup and restore strategies

## Quick Start

Install the required packages:
```bash
pip install strands-sqlite-session-manager strands
```

Run any example:
```bash
python examples/01_basic_usage.py
```

## Key Features Demonstrated

### Session Persistence
- All conversations are automatically saved to SQLite
- Resume sessions by using the same session ID
- Supports multiple agents per session

### Database Configuration
- Custom database paths
- Environment variable configuration (`STRANDS_SQLITE_DB_PATH`)
- In-memory databases for temporary sessions
- Multiple database files for organization

### Agent Patterns
- Single agent with history
- Multi-agent collaboration
- Agent handoff workflows
- Shared context between agents

### Error Handling
- Graceful handling of duplicate sessions
- Session not found errors
- Database connection management

## Database Schema

The SQLite database uses the following schema:

- **sessions**: Stores session metadata
- **agents**: Stores agent configurations per session
- **messages**: Stores conversation messages
- **multi_agents**: Stores multi-agent state

All tables include automatic timestamps for creation and updates.

## Best Practices

1. **Use meaningful session IDs**: Make them descriptive and unique
2. **Organize databases**: Use different database files for different purposes
3. **Handle errors gracefully**: Wrap operations in try-except blocks
4. **Clean up old sessions**: Implement retention policies for old data
5. **Backup important data**: Regular backups for production sessions

## Environment Variables

- `STRANDS_SQLITE_DB_PATH`: Default database path (default: `./sessions.db`)

## Notes

- SQLite uses WAL (Write-Ahead Logging) mode for better concurrency
- Foreign key constraints ensure data integrity
- Indexes optimize query performance for large conversations
- Thread-safe operations with proper connection handling

## License

See the main package LICENSE file for details.
