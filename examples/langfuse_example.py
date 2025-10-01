#!/usr/bin/env python3
"""
Example usage of Langfuse integration.

Demonstrates:
- Basic tracing
- LLM call tracing
- Memory retrieval tracing
- Full pipeline tracing
"""

import sys
sys.path.insert(0, '..')

from utils.langfuse_client import create_langfuse_client, LangfuseTracer
import time


def example_basic_tracing():
    """Example 1: Basic tracing"""
    print("\n" + "="*80)
    print("📊 Example 1: Basic Tracing")
    print("="*80)
    
    # Create client
    client = create_langfuse_client()
    
    if not client.is_enabled():
        print("⚠️  Langfuse is disabled. Enable it in config/langfuse_config.yaml")
        return
    
    # Create a trace
    trace = client.create_trace(
        name="example_conversation",
        user_id="user_123",
        session_id="session_456",
        metadata={"source": "example"},
        tags=["demo", "test"]
    )
    
    print(f"✅ Created trace: {trace}")
    
    # Log an event
    client.log_event(
        trace_id="current",
        name="user_message_received",
        metadata={"message": "Hello, how are you?"}
    )
    
    print("✅ Logged event")
    
    # Flush to Langfuse
    client.flush()
    print("✅ Flushed to Langfuse")


def example_llm_tracing():
    """Example 2: LLM call tracing"""
    print("\n" + "="*80)
    print("🤖 Example 2: LLM Call Tracing")
    print("="*80)
    
    client = create_langfuse_client()
    tracer = LangfuseTracer(client)
    
    # Simulate LLM call
    @tracer.trace_llm_call(model="gpt-4")
    def generate_response(prompt: str) -> str:
        """Simulated LLM generation"""
        time.sleep(0.1)  # Simulate API call
        return f"This is a response to: {prompt}"
    
    # Call the traced function
    prompt = "What is the capital of France?"
    response = generate_response(prompt)
    
    print(f"📝 Prompt: {prompt}")
    print(f"💬 Response: {response}")
    print("✅ LLM call traced")
    
    client.flush()


def example_memory_tracing():
    """Example 3: Memory retrieval tracing"""
    print("\n" + "="*80)
    print("🧠 Example 3: Memory Retrieval Tracing")
    print("="*80)
    
    client = create_langfuse_client()
    tracer = LangfuseTracer(client)
    
    # Simulate memory retrieval
    @tracer.trace_operation(name="memory_retrieval")
    def retrieve_context(query: str):
        """Simulated memory retrieval"""
        time.sleep(0.05)
        return {
            "stm_items": 5,
            "mtm_items": 3,
            "ltm_items": 2,
            "total_relevance": 0.85
        }
    
    # Call the traced function
    query = "AI machine learning"
    context = retrieve_context(query)
    
    print(f"🔍 Query: {query}")
    print(f"📊 Context: {context}")
    print("✅ Memory retrieval traced")
    
    client.flush()


def example_pipeline_tracing():
    """Example 4: Full pipeline tracing"""
    print("\n" + "="*80)
    print("🔄 Example 4: Full Pipeline Tracing")
    print("="*80)
    
    client = create_langfuse_client()
    tracer = LangfuseTracer(client)
    
    # Simulate full conversation pipeline
    with tracer.trace_context("full_conversation_pipeline", metadata={"user": "test_user"}):
        print("1️⃣ Preprocessing input...")
        time.sleep(0.02)
        
        print("2️⃣ Retrieving context from memory...")
        time.sleep(0.05)
        
        print("3️⃣ Generating response...")
        time.sleep(0.1)
        
        print("4️⃣ Post-processing...")
        time.sleep(0.02)
    
    print("✅ Full pipeline traced")
    client.flush()


def example_error_handling():
    """Example 5: Error handling in traced functions"""
    print("\n" + "="*80)
    print("⚠️  Example 5: Error Handling")
    print("="*80)
    
    client = create_langfuse_client()
    tracer = LangfuseTracer(client)
    
    @tracer.trace_operation(name="risky_operation")
    def risky_function():
        """Function that might fail"""
        import random
        if random.random() < 0.5:
            raise ValueError("Simulated error!")
        return "Success!"
    
    # Try calling the function
    try:
        result = risky_function()
        print(f"✅ Result: {result}")
    except ValueError as e:
        print(f"❌ Error caught: {e}")
        print("✅ Error was also traced to Langfuse")
    
    client.flush()


def example_with_metadata():
    """Example 6: Rich metadata logging"""
    print("\n" + "="*80)
    print("📋 Example 6: Rich Metadata")
    print("="*80)
    
    client = create_langfuse_client()
    
    # Create trace with rich metadata
    trace = client.create_trace(
        name="conversation_with_metadata",
        user_id="user_789",
        session_id="session_101",
        metadata={
            "user_tier": "premium",
            "model_version": "v2.1",
            "features": ["semantic_search", "ltm"],
            "performance": {
                "expected_latency": "<200ms",
                "priority": "high"
            }
        },
        tags=["production", "premium_user", "high_priority"]
    )
    
    print("✅ Created trace with rich metadata")
    
    # Log generation with usage info
    client.log_generation(
        trace_id="current",
        name="main_response",
        model="gpt-4",
        input_text="Explain quantum computing",
        output_text="Quantum computing is...",
        metadata={
            "temperature": 0.7,
            "max_tokens": 500,
            "retrieval_context": "Used 3 LTM facts"
        },
        usage={
            "prompt_tokens": 150,
            "completion_tokens": 300,
            "total_tokens": 450
        },
        start_time=time.time() - 1.5,
        end_time=time.time()
    )
    
    print("✅ Logged generation with usage metrics")
    client.flush()


def main():
    """Run all examples"""
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "LANGFUSE INTEGRATION EXAMPLES" + " "*29 + "║")
    print("╚" + "="*78 + "╝")
    
    examples = [
        ("Basic Tracing", example_basic_tracing),
        ("LLM Call Tracing", example_llm_tracing),
        ("Memory Retrieval Tracing", example_memory_tracing),
        ("Full Pipeline Tracing", example_pipeline_tracing),
        ("Error Handling", example_error_handling),
        ("Rich Metadata", example_with_metadata),
    ]
    
    for name, example_func in examples:
        try:
            example_func()
        except KeyboardInterrupt:
            print("\n\n⚠️  Examples interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error in example '{name}': {e}")
    
    print("\n" + "="*80)
    print("🎉 All examples completed!")
    print("="*80)
    print("\n💡 Next steps:")
    print("   1. Check your Langfuse dashboard to see the traces")
    print("   2. Explore trace details, timings, and metadata")
    print("   3. Set up alerts and monitoring")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
