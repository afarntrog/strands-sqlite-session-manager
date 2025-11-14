"""
Streaming and tools example for SQLiteSessionManager with Strands.

This example demonstrates how to use streaming responses and tools
with agents that persist their state to SQLite.
"""

from strands import Agent

from strands_sqlite_session_manager import SQLiteSessionManager


def streaming_example():
    """Demonstrate streaming responses with session persistence."""
    
    session_manager = SQLiteSessionManager(
        session_id="streaming-session-001",
        db_path="./streaming_sessions.db"
    )
    
    agent = Agent(
        session_manager=session_manager,
        system_prompt="You are a storyteller who creates engaging narratives."
    )
    
    print("=== Streaming Response Example ===\n")
    print("Generating story (streaming):")
    
    # Stream a response - each chunk is still saved to the session
    full_response = ""
    for chunk in agent("Tell me a short story about a robot learning to paint", stream=True):
        print(chunk, end="", flush=True)
        full_response += chunk
    
    print("\n\n=== Full response saved to session ===")
    
    # Follow-up question to verify persistence
    response = agent("What was the robot's name in the story?")
    print(f"\nFollow-up: {response}")


def tool_usage_example():
    """Demonstrate using tools with persistent sessions."""
    
    def calculate_sum(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b
    
    def get_weather(city: str) -> str:
        """Get weather for a city (mock function)."""
        # Mock weather data
        weather_data = {
            "New York": "Sunny, 72°F",
            "London": "Cloudy, 59°F",
            "Tokyo": "Rainy, 65°F",
            "Paris": "Partly cloudy, 68°F"
        }
        return weather_data.get(city, f"Weather data not available for {city}")
    
    # Create session manager
    session_manager = SQLiteSessionManager(
        session_id="tools-session-001",
        db_path="./tools_sessions.db"
    )
    
    # Create agent with tools
    agent = Agent(
        session_manager=session_manager,
        system_prompt="You are a helpful assistant with access to calculation and weather tools.",
        tools=[calculate_sum, get_weather]
    )
    
    print("=== Tool Usage Example ===\n")
    
    # Use calculation tool
    calc_response = agent("What is 157 plus 239?")
    print(f"Calculation: {calc_response}")
    
    # Use weather tool
    weather_response = agent("What's the weather like in Paris and Tokyo?")
    print(f"\nWeather: {weather_response}")
    
    # Verify tool usage is persisted
    history_response = agent("What calculations and weather queries did we just do?")
    print(f"\nHistory check: {history_response}")


def async_streaming_example():
    """Demonstrate async streaming with session persistence."""
    import asyncio
    
    async def async_stream_chat():
        session_manager = SQLiteSessionManager(
            session_id="async-stream-session-001",
            db_path="./async_sessions.db"
        )
        
        agent = Agent(
            session_manager=session_manager,
            system_prompt="You are a technical explainer."
        )
        
        print("=== Async Streaming Example ===\n")
        print("Explaining concept (async streaming):")
        
        # Async streaming
        full_response = ""
        async for chunk in agent(
            "Explain quantum computing in simple terms", 
            stream=True
        ):
            print(chunk, end="", flush=True)
            full_response += chunk
        
        print("\n\n=== Response saved asynchronously ===")
        
        # Async follow-up
        response = await agent("What are the main applications you mentioned?")
        print(f"\nFollow-up: {response}")
    
    # Run async example
    asyncio(async_stream_chat())


def custom_tool_with_state():
    """Demonstrate stateful tools with session persistence."""
    
    class TaskManager:
        """A stateful task manager tool."""
        
        def __init__(self):
            self.tasks = []
        
        def add_task(self, task: str) -> str:
            """Add a task to the list."""
            self.tasks.append(task)
            return f"Task added: {task}. Total tasks: {len(self.tasks)}"
        
        def list_tasks(self) -> str:
            """List all tasks."""
            if not self.tasks:
                return "No tasks in the list."
            return "Tasks:\n" + "\n".join(f"- {task}" for task in self.tasks)
        
        def complete_task(self, task_index: int) -> str:
            """Mark a task as complete."""
            if 0 <= task_index < len(self.tasks):
                completed = self.tasks.pop(task_index)
                return f"Completed: {completed}"
            return "Invalid task index."
    
    # Create task manager instance
    task_manager = TaskManager()
    
    session_manager = SQLiteSessionManager(
        session_id="stateful-tools-001",
        db_path="./stateful_tools.db"
    )
    
    agent = Agent(
        session_manager=session_manager,
        system_prompt="You are a task management assistant.",
        tools=[
            task_manager.add_task,
            task_manager.list_tasks,
            task_manager.complete_task
        ]
    )
    
    print("=== Stateful Tool Example ===\n")
    
    # Add tasks
    response1 = agent("Add these tasks: 'Review code', 'Write documentation', 'Run tests'")
    print(f"Adding tasks: {response1}")
    
    # List tasks
    response2 = agent("Show me all my tasks")
    print(f"\nListing: {response2}")
    
    # Complete a task
    response3 = agent("Mark the first task as complete")
    print(f"\nCompleting: {response3}")
    
    # Check remaining tasks
    response4 = agent("What tasks are left?")
    print(f"\nRemaining: {response4}")


def parallel_tool_execution():
    """Demonstrate parallel tool execution with session management."""
    import time
    
    def slow_operation_1(value: str) -> str:
        """Simulate a slow operation."""
        time.sleep(1)  # Simulate delay
        return f"Operation 1 result: {value.upper()}"
    
    def slow_operation_2(value: str) -> str:
        """Simulate another slow operation."""
        time.sleep(1)  # Simulate delay
        return f"Operation 2 result: {value[::-1]}"  # Reverse string
    
    session_manager = SQLiteSessionManager(
        session_id="parallel-tools-001",
        db_path="./parallel_tools.db"
    )
    
    agent = Agent(
        session_manager=session_manager,
        system_prompt="You are an assistant that can run operations in parallel.",
        tools=[slow_operation_1, slow_operation_2],
        parallel_tool_calls=True  # Enable parallel execution
    )
    
    print("=== Parallel Tool Execution ===\n")
    
    start_time = time.time()
    response = agent(
        "Run both operations on the word 'hello' and tell me the results"
    )
    end_time = time.time()
    
    print(f"Response: {response}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    print("(Should be ~1 second with parallel execution, ~2 seconds without)")


if __name__ == "__main__":
    print("Running Streaming and Tools Examples...\n")
    
    print("\n" + "="*60 + "\n")
    streaming_example()
    
    print("\n" + "="*60 + "\n")
    tool_usage_example()
    
    print("\n" + "="*60 + "\n")
    async_streaming_example()
    
    print("\n" + "="*60 + "\n")
    custom_tool_with_state()
    
    print("\n" + "="*60 + "\n")
    parallel_tool_execution()
