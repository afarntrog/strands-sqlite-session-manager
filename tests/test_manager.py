"""Tests for SQLiteSessionManager."""

import pytest
from strands.types.exceptions import SessionException
from strands.types.session import Session, SessionAgent, SessionMessage

from strands_sqlite_session_manager import SQLiteSessionManager


@pytest.fixture
def manager():
    """Create in-memory session manager for testing."""
    return SQLiteSessionManager(session_id="test-session", db_path=":memory:")


@pytest.fixture
def session():
    """Create test session."""
    from strands.types.session import SessionType
    return Session(session_id="test-session", session_type=SessionType.AGENT)


@pytest.fixture
def agent():
    """Create test agent."""
    return SessionAgent(agent_id="test-agent", state={}, conversation_manager_state={})


@pytest.fixture
def message():
    """Create test message."""
    from strands.types.content import Message
    return SessionMessage(
        message_id=1,
        message=Message(role="user", content=[{"text": "Hello"}])
    )


class TestSessionOperations:
    """Test session CRUD operations."""

    def test_create_session(self, manager, session):
        manager.create_session(session)
        retrieved = manager.read_session(session.session_id)
        assert retrieved.session_id == session.session_id

    def test_create_duplicate_session(self, manager, session):
        manager.create_session(session)
        with pytest.raises(SessionException, match="already exists"):
            manager.create_session(session)

    def test_read_nonexistent_session(self, manager):
        result = manager.read_session("nonexistent")
        assert result is None

    def test_delete_session(self, manager, session):
        manager.create_session(session)
        manager.delete_session(session.session_id)
        with pytest.raises(SessionException, match="not found"):
            manager.read_session(session.session_id)

    def test_delete_nonexistent_session(self, manager):
        with pytest.raises(SessionException, match="not found"):
            manager.delete_session("nonexistent")


class TestAgentOperations:
    """Test agent CRUD operations."""

    def test_read_agent(self, manager, session, agent):
        manager.create_session(session)
        manager.create_agent(session.session_id, agent)
        retrieved = manager.read_agent(session.session_id, agent.agent_id)
        assert retrieved.agent_id == agent.agent_id
        assert retrieved.state == agent.state

    def test_create_agent_without_session(self, manager, agent):
        with pytest.raises(SessionException, match="not found"):
            manager.create_agent("nonexistent", agent)

    def test_create_duplicate_agent(self, manager, session, agent):
        manager.create_session(session)
        manager.create_agent(session.session_id, agent)
        with pytest.raises(SessionException, match="already exists"):
            manager.create_agent(session.session_id, agent)

    def test_read_nonexistent_agent(self, manager, session):
        manager.create_session(session)
        with pytest.raises(SessionException, match="not found"):
            manager.read_agent(session.session_id, "nonexistent")

    def test_update_agent(self, manager, session, agent):
        manager.create_session(session)
        manager.create_agent(session.session_id, agent)
        
        agent.state = {"updated": "value"}
        manager.update_agent(session.session_id, agent)
        
        retrieved = manager.read_agent(session.session_id, agent.agent_id)
        assert retrieved.state == {"updated": "value"}

    def test_update_nonexistent_agent(self, manager, session, agent):
        manager.create_session(session)
        with pytest.raises(SessionException, match="not found"):
            manager.update_agent(session.session_id, agent)

    def test_cascade_delete_agents(self, manager, session, agent):
        manager.create_session(session)
        manager.create_agent(session.session_id, agent)
        manager.delete_session(session.session_id)
        
        # Agent should be deleted with session
        with pytest.raises(SessionException, match="not found"):
            manager.read_agent(session.session_id, agent.agent_id)


class TestMessageOperations:
    """Test message CRUD operations."""

    def test_create_message(self, manager, session, agent, message):
        manager.create_session(session)
        manager.create_agent(session.session_id, agent)
        manager.create_message(session.session_id, agent.agent_id, message)
        
        retrieved = manager.read_message(session.session_id, agent.agent_id, message.message_id)
        assert retrieved.message_id == message.message_id

    def test_create_message_without_agent(self, manager, session, message):
        manager.create_session(session)
        with pytest.raises(SessionException, match="not found"):
            manager.create_message(session.session_id, "nonexistent", message)

    def test_read_nonexistent_message(self, manager, session, agent):
        manager.create_session(session)
        manager.create_agent(session.session_id, agent)
        with pytest.raises(SessionException, match="not found"):
            manager.read_message(session.session_id, agent.agent_id, 999)

    def test_update_message(self, manager, session, agent, message):
        from strands.types.content import Message
        manager.create_session(session)
        manager.create_agent(session.session_id, agent)
        manager.create_message(session.session_id, agent.agent_id, message)
        
        message.message = Message(role="user", content=[{"text": "Updated"}])
        manager.update_message(session.session_id, agent.agent_id, message)
        
        retrieved = manager.read_message(session.session_id, agent.agent_id, message.message_id)
        # Message is a dict after deserialization
        assert retrieved.message["content"][0]["text"] == "Updated"

    def test_list_messages(self, manager, session, agent):
        from strands.types.content import Message
        manager.create_session(session)
        manager.create_agent(session.session_id, agent)
        
        for i in range(5):
            msg = SessionMessage(
                message_id=i,
                message=Message(role="user", content=[{"text": f"Message {i}"}])
            )
            manager.create_message(session.session_id, agent.agent_id, msg)
        
        messages = manager.list_messages(session.session_id, agent.agent_id)
        assert len(messages) == 5
        assert messages[0].message_id == 0
        assert messages[4].message_id == 4

    def test_list_messages_with_pagination(self, manager, session, agent):
        from strands.types.content import Message
        manager.create_session(session)
        manager.create_agent(session.session_id, agent)
        
        for i in range(10):
            msg = SessionMessage(
                message_id=i,
                message=Message(role="user", content=[{"text": f"Message {i}"}])
            )
            manager.create_message(session.session_id, agent.agent_id, msg)
        
        messages = manager.list_messages(session.session_id, agent.agent_id, limit=3, offset=2)
        assert len(messages) == 3
        assert messages[0].message_id == 2
        assert messages[2].message_id == 4


class TestMultiAgentOperations:
    """Test multi-agent state operations."""

    def test_create_multi_agent(self, manager, session):
        manager.create_session(session)
        state = {"agents": ["agent1", "agent2"], "current": "agent1"}
        manager.create_multi_agent(session.session_id, "multi-1", state)
        
        retrieved = manager.read_multi_agent(session.session_id, "multi-1")
        assert retrieved == state

    def test_create_multi_agent_without_session(self, manager):
        with pytest.raises(SessionException, match="not found"):
            manager.create_multi_agent("nonexistent", "multi-1", {})

    def test_read_nonexistent_multi_agent(self, manager, session):
        manager.create_session(session)
        with pytest.raises(SessionException, match="not found"):
            manager.read_multi_agent(session.session_id, "nonexistent")

    def test_update_multi_agent(self, manager, session):
        manager.create_session(session)
        state = {"agents": ["agent1"], "current": "agent1"}
        manager.create_multi_agent(session.session_id, "multi-1", state)
        
        new_state = {"agents": ["agent1", "agent2"], "current": "agent2"}
        manager.update_multi_agent(session.session_id, "multi-1", new_state)
        
        retrieved = manager.read_multi_agent(session.session_id, "multi-1")
        assert retrieved == new_state

    def test_update_nonexistent_multi_agent(self, manager, session):
        manager.create_session(session)
        with pytest.raises(SessionException, match="not found"):
            manager.update_multi_agent(session.session_id, "nonexistent", {})
