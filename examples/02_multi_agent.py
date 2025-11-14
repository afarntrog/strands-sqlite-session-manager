"""
Multi-agent example for SQLiteSessionManager with Strands.

This example demonstrates how to use multiple agents with the same session
manager, enabling complex workflows and agent collaboration.
"""

from strands import Agent

from strands_sqlite_session_manager import SQLiteSessionManager


def multi_agent_conversation():
    """Demonstrate conversation between multiple agents."""
    
    # Create a shared session manager
    session_manager = SQLiteSessionManager(
        session_id="multi-agent-session-001",
        db_path="./multi_agent_sessions.db"
    )
    
    # Create multiple agents with different roles
    interviewer = Agent(
        session_manager=session_manager,
        system_prompt="You are an interviewer conducting a job interview.",
        agent_id="interviewer"  # Unique agent ID
    )
    
    candidate = Agent(
        model="gpt-4o-mini",
        session_manager=session_manager,
        system_prompt="You are a software engineer interviewing for a position.",
        agent_id="candidate"  # Unique agent ID
    )
    
    # Simulate an interview conversation
    print("=== Job Interview Simulation ===\n")
    
    # Interviewer asks first question
    question1 = interviewer("Please tell me about your experience with Python.")
    print(f"Interviewer: {question1}")
    
    # Candidate responds
    answer1 = candidate(question1)
    print(f"Candidate: {answer1}")
    
    # Interviewer follows up
    question2 = interviewer(answer1)
    print(f"Interviewer: {question2}")
    
    # Candidate responds again
    answer2 = candidate(question2)
    print(f"Candidate: {answer2}")
    
    print("\n=== All conversations are saved in the same session ===")


def collaborative_agents():
    """Demonstrate agents collaborating on a task."""
    
    session_manager = SQLiteSessionManager(
        session_id="collaborative-session-001",
        db_path="./collaborative_sessions.db"
    )
    
    # Create specialized agents
    researcher = Agent(
        session_manager=session_manager,
        system_prompt="You are a research specialist who gathers information.",
        agent_id="researcher"
    )
    
    writer = Agent(
        session_manager=session_manager,
        system_prompt="You are a technical writer who creates documentation.",
        agent_id="writer"
    )
    
    reviewer = Agent(
        session_manager=session_manager,
        system_prompt="You are a quality reviewer who provides feedback.",
        agent_id="reviewer"
    )
    
    print("=== Collaborative Documentation Creation ===\n")
    
    # Research phase
    topic = "Python async programming"
    research = researcher(f"Research the key concepts of {topic}")
    print(f"Researcher: {research[:200]}...")
    
    # Writing phase
    doc = writer(f"Based on this research, write a brief guide: {research}")
    print(f"\nWriter: {doc[:200]}...")
    
    # Review phase
    feedback = reviewer(f"Review this documentation and provide feedback: {doc}")
    print(f"\nReviewer: {feedback[:200]}...")
    
    # Writer incorporates feedback
    final_doc = writer(f"Incorporate this feedback into the documentation: {feedback}")
    print(f"\nWriter (Final): {final_doc[:200]}...")


def agent_handoff_example():
    """Demonstrate agent handoff in customer support scenario."""
    
    session_manager = SQLiteSessionManager(
        session_id="support-session-001",
        db_path="./support_sessions.db"
    )
    
    # Initial support agent
    level1_support = Agent(
        model="gpt-4o-mini",
        session_manager=session_manager,
        system_prompt="You are a level 1 customer support agent. Handle basic queries.",
        agent_id="level1_support"
    )
    
    # Specialist agent
    technical_specialist = Agent(
        session_manager=session_manager,
        system_prompt="You are a technical specialist. Handle complex technical issues.",
        agent_id="technical_specialist"
    )
    
    print("=== Customer Support Handoff ===\n")
    
    # Customer initial query
    customer_query = "My application crashes when I try to process large files over 2GB."
    
    # Level 1 attempts to help
    initial_response = level1_support(customer_query)
    print(f"Level 1 Support: {initial_response}")
    
    # Escalation decision
    escalation = level1_support(
        "Should this issue be escalated to technical specialist? Reply with YES or NO and brief reason."
    )
    print(f"\nLevel 1 Decision: {escalation}")
    
    # Handoff to specialist
    if "YES" in escalation.upper():
        print("\n--- Escalating to Technical Specialist ---\n")
        
        # Specialist reviews the conversation and provides solution
        specialist_response = technical_specialist(
            f"Customer issue: {customer_query}\n"
            f"Initial support response: {initial_response}\n"
            "Please provide a technical solution."
        )
        print(f"Technical Specialist: {specialist_response}")


def shared_context_example():
    """Demonstrate agents sharing context through session manager."""
    
    session_manager = SQLiteSessionManager(
        session_id="shared-context-001",
        db_path="./shared_context.db"
    )
    
    # Create agents that build on each other's work
    planner = Agent(
        session_manager=session_manager,
        system_prompt="You are a project planner.",
        agent_id="planner"
    )
    
    developer = Agent(
        session_manager=session_manager,
        system_prompt="You are a software developer.",
        agent_id="developer"
    )
    
    tester = Agent(
        session_manager=session_manager,
        system_prompt="You are a QA tester.",
        agent_id="tester"
    )
    
    print("=== Shared Context Workflow ===\n")
    
    # Planning phase
    project = "a simple todo list API"
    plan = planner(f"Create a development plan for {project}")
    print(f"Planner: {plan[:150]}...")
    
    # Development phase - developer can see the plan
    code_outline = developer(
        "Based on the plan above, create a Python code outline for the main components"
    )
    print(f"\nDeveloper: {code_outline[:150]}...")
    
    # Testing phase - tester can see both plan and code
    test_plan = tester(
        "Based on the plan and code outline above, create a test strategy"
    )
    print(f"\nTester: {test_plan[:150]}...")
    
    print("\n=== All agents share the same session context ===")


if __name__ == "__main__":
    print("Running Multi-Agent Examples...\n")
    
    print("\n" + "="*60 + "\n")
    multi_agent_conversation()
    
    print("\n" + "="*60 + "\n")
    collaborative_agents()
    
    print("\n" + "="*60 + "\n")
    agent_handoff_example()
    
    print("\n" + "="*60 + "\n")
    shared_context_example()
