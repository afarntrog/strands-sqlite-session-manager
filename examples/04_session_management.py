"""
Session management patterns for SQLiteSessionManager with Strands.

This example demonstrates various session management patterns including
error handling, session cleanup, and migration scenarios.
"""

import os
from pathlib import Path

from strands import Agent
from strands.types.exceptions import SessionException

from strands_sqlite_session_manager import SQLiteSessionManager


def session_lifecycle_example():
    """Demonstrate complete session lifecycle management."""
    
    db_path = "./lifecycle_sessions.db"
    session_id = "lifecycle-session-001"
    
    print("=== Session Lifecycle Example ===\n")
    
    # Create a new session
    session_manager = SQLiteSessionManager(
        session_id=session_id,
        db_path=db_path
    )
    
    agent = Agent(
        session_manager=session_manager,
        system_prompt="You are a helpful assistant."
    )
    
    # Initial conversation
    response1 = agent("Hello! Remember that my favorite color is blue.")
    print(f"Initial: {response1}")
    
    # Verify session exists
    print(f"\nSession database exists: {Path(db_path).exists()}")
    
    # Create a new session manager with the same ID to verify persistence
    session_manager2 = SQLiteSessionManager(
        session_id=session_id,
        db_path=db_path
    )
    
    agent2 = Agent(
        session_manager=session_manager2
    )
    
    response2 = agent2("What's my favorite color?")
    print(f"Resumed: {response2}")
    
    # Clean up specific session
    try:
        session_manager2.delete_session(session_id)
        print(f"\nSession {session_id} deleted successfully")
    except SessionException as e:
        print(f"Error deleting session: {e}")


def error_handling_example():
    """Demonstrate error handling with session operations."""
    
    print("=== Error Handling Example ===\n")
    
    db_path = "./error_handling.db"
    
    # Attempt to create duplicate session
    session_manager1 = SQLiteSessionManager(
        session_id="duplicate-test-001",
        db_path=db_path
    )
    
    agent1 = Agent(
        session_manager=session_manager1
    )
    
    # First agent works fine
    agent1("First message")
    print("First agent created successfully")
    
    # Try to create another agent with same session ID
    # This should handle the existing session gracefully
    try:
        session_manager2 = SQLiteSessionManager(
            session_id="duplicate-test-001",
            db_path=db_path
        )
        
        agent2 = Agent(
            session_manager=session_manager2
        )
        
        # This will work - it resumes the existing session
        response = agent2("Can you see the previous message?")
        print(f"Second agent resumed session: {response[:100]}...")
        
    except SessionException as e:
        print(f"Session error: {e}")


def multiple_databases_example():
    """Demonstrate using multiple database files for organization."""
    
    print("=== Multiple Databases Example ===\n")
    
    # Different databases for different purposes
    databases = {
        "customer_support": "./databases/support_sessions.db",
        "internal_tools": "./databases/tool_sessions.db",
        "development": "./databases/dev_sessions.db"
    }
    
    # Create sessions in different databases
    for purpose, db_path in databases.items():
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        session_manager = SQLiteSessionManager(
            session_id=f"{purpose}-session-001",
            db_path=db_path
        )
        
        agent = Agent(
            session_manager=session_manager,
            system_prompt=f"You are an agent for {purpose.replace('_', ' ')}."
        )
        
        response = agent(f"Initialize {purpose} session")
        print(f"{purpose}: {response[:50]}...")
    
    print(f"\nCreated {len(databases)} separate database files")


def session_migration_example():
    """Demonstrate migrating sessions between databases."""
    
    print("=== Session Migration Example ===\n")
    
    # Original database
    old_db = "./migration_old.db"
    session_id = "migration-session-001"
    
    # Create original session
    old_session_manager = SQLiteSessionManager(
        session_id=session_id,
        db_path=old_db
    )
    
    old_agent = Agent(
        session_manager=old_session_manager,
        system_prompt="You are a helpful assistant."
    )
    
    # Build conversation history
    old_agent("My name is Bob and I work at TechCorp.")
    old_agent("I need help with Python programming.")
    print("Original session created with conversation history")
    
    # To migrate, you would typically:
    # 1. Export from old database
    # 2. Import to new database
    # For this example, we'll just demonstrate using a new database
    
    new_db = "./migration_new.db"
    
    # Create new session with same ID in new database
    # In a real migration, you'd copy the data
    new_session_manager = SQLiteSessionManager(
        session_id=f"{session_id}-migrated",
        db_path=new_db
    )
    
    new_agent = Agent(
        session_manager=new_session_manager,
        system_prompt="You are a helpful assistant (migrated)."
    )
    
    response = new_agent("I've been migrated to a new database.")
    print(f"New session created: {response[:100]}...")
    
    print(f"\nOld database: {Path(old_db).exists()}")
    print(f"New database: {Path(new_db).exists()}")


def cleanup_old_sessions():
    """Demonstrate cleaning up old session files."""
    
    print("=== Session Cleanup Example ===\n")
    
    import glob
    import time
    from datetime import datetime, timedelta
    
    # Create some test sessions
    test_sessions = [
        ("old-session-001", "./cleanup/old_sessions.db"),
        ("old-session-002", "./cleanup/old_sessions.db"),
        ("recent-session-001", "./cleanup/recent_sessions.db"),
    ]
    
    for session_id, db_path in test_sessions:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        manager = SQLiteSessionManager(
            session_id=session_id,
            db_path=db_path
        )
        
        agent = Agent(
            session_manager=manager
        )
        
        agent(f"Test message for {session_id}")
    
    print(f"Created {len(test_sessions)} test sessions")
    
    # Find and clean old database files
    cleanup_dir = "./cleanup"
    db_files = glob.glob(f"{cleanup_dir}/*.db")
    
    for db_file in db_files:
        file_path = Path(db_file)
        
        # Check file age (for demo, we'll just check if "old" is in the name)
        if "old" in file_path.name:
            print(f"Would delete old database: {file_path.name}")
            # file_path.unlink()  # Uncomment to actually delete
        else:
            print(f"Keeping recent database: {file_path.name}")


def concurrent_access_example():
    """Demonstrate handling concurrent access to the same session."""
    
    print("=== Concurrent Access Example ===\n")
    
    db_path = "./concurrent_sessions.db"
    session_id = "concurrent-session-001"
    
    # Create multiple agents accessing the same session
    # SQLite handles this with WAL mode
    agents = []
    
    for i in range(3):
        session_manager = SQLiteSessionManager(
            session_id=session_id,
            db_path=db_path
        )
        
        agent = Agent(
            session_manager=session_manager,
            system_prompt=f"You are assistant number {i+1}.",
            agent_id=f"agent_{i+1}"  # Different agent IDs
        )
        
        agents.append(agent)
    
    # Each agent adds to the conversation
    for i, agent in enumerate(agents):
        response = agent(f"Hello from agent {i+1}")
        print(f"Agent {i+1}: {response[:50]}...")
    
    # Verify all messages are in the session
    final_response = agents[0]("How many agents have said hello?")
    print(f"\nFinal check: {final_response}")


def backup_and_restore_example():
    """Demonstrate backing up and restoring session databases."""
    
    print("=== Backup and Restore Example ===\n")
    
    import shutil
    
    original_db = "./backup_example/sessions.db"
    backup_db = "./backup_example/sessions_backup.db"
    
    # Ensure directory exists
    Path(original_db).parent.mkdir(parents=True, exist_ok=True)
    
    # Create original session
    session_manager = SQLiteSessionManager(
        session_id="backup-session-001",
        db_path=original_db
    )
    
    agent = Agent(
        session_manager=session_manager
    )
    
    agent("Important data that needs backing up")
    print("Original session created")
    
    # Create backup
    if Path(original_db).exists():
        shutil.copy2(original_db, backup_db)
        print(f"Backup created at {backup_db}")
    
    # Simulate data loss (don't actually delete)
    print("Simulating data loss...")
    
    # Restore from backup
    if Path(backup_db).exists():
        # In real scenario, you'd copy backup back to original
        print(f"Backup available at {backup_db}")
        print("Session can be restored from backup")


if __name__ == "__main__":
    print("Running Session Management Examples...\n")
    
    print("\n" + "="*60 + "\n")
    session_lifecycle_example()
    
    print("\n" + "="*60 + "\n")
    error_handling_example()
    
    print("\n" + "="*60 + "\n")
    multiple_databases_example()
    
    print("\n" + "="*60 + "\n")
    session_migration_example()
    
    print("\n" + "="*60 + "\n")
    cleanup_old_sessions()
    
    print("\n" + "="*60 + "\n")
    concurrent_access_example()
    
    print("\n" + "="*60 + "\n")
    backup_and_restore_example()
