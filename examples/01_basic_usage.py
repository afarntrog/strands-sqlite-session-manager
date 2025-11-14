"""
Basic usage example for SQLiteSessionManager with Strands.

This example demonstrates how to create a session manager and use it
with a simple Strands agent for maintaining conversation history.
"""

from strands import Agent

from strands_sqlite_session_manager import SQLiteSessionManager

def basic_chat_example():
    """Demonstrate basic chat with session persistence."""
    
    # Create a SQLite session manager with a unique session ID
    # The database will be created at ./sessions.db by default
    session_manager = SQLiteSessionManager(
        session_id="chat-session-001",
        db_path="./my_sessions.db"  # Optional: specify custom path
    )
    
    # Create a Strands agent with the session manager
    agent = Agent(
        session_manager=session_manager,
        system_prompt="You are a helpful assistant."
    )
    
    # Have a conversation - history is automatically persisted
    response1 = agent("Hello! My name is Alice.")
    print(f"Agent: {response1}")
    
    response2 = agent("What's my name?")
    print(f"Agent: {response2}")  # Should remember "Alice"
    
    # The conversation is automatically saved to SQLite
    print("\nSession persisted to SQLite database!")


def resume_session_example():
    """Demonstrate resuming a previous session."""
    
    # Resume a previous session by using the same session ID
    session_manager = SQLiteSessionManager(
        session_id="chat-session-001",
        db_path="./my_sessions.db"
    )
    
    # Create a new agent instance with the same session manager
    # It will automatically load the conversation history
    agent = Agent(
        session_manager=session_manager,
        system_prompt="You are a helpful assistant."
    )
    
    # Continue the conversation - agent has access to previous context
    response = agent("Do you remember what we talked about earlier?")
    print(f"Agent: {response}")


def environment_variable_example():
    """Demonstrate using environment variable for database path."""
    import os
    
    # Set the environment variable for database path
    os.environ["STRANDS_SQLITE_DB_PATH"] = "/tmp/strands_sessions.db"
    
    # Create session manager without specifying db_path
    # It will use the environment variable
    session_manager = SQLiteSessionManager(
        session_id="env-session-001"
    )
    
    agent = Agent(
        session_manager=session_manager
    )
    
    response = agent("Hello from environment variable example!")
    print(f"Agent: {response}")


def memory_database_example():
    """Demonstrate using in-memory database for temporary sessions."""
    
    # Use ":memory:" for an in-memory SQLite database
    # Useful for testing or temporary sessions
    session_manager = SQLiteSessionManager(
        session_id="temp-session-001",
        db_path=":memory:"
    )
    
    agent = Agent(
        session_manager=session_manager,
        system_prompt="You are a helpful assistant for temporary tasks."
    )
    
    response = agent("This conversation exists only in memory!")
    print(f"Agent: {response}")
    
    # Note: Data will be lost when the program ends


if __name__ == "__main__":
    print("=== Basic Chat Example ===")
    basic_chat_example()
    
    print("\n=== Resume Session Example ===")
    resume_session_example()
    
    print("\n=== Environment Variable Example ===")
    environment_variable_example()
    
    print("\n=== In-Memory Database Example ===")
    memory_database_example()
