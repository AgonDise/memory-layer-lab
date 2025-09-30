#!/usr/bin/env python3
"""
Demo script to showcase the complete memory layer workflow.

This demonstrates:
1. Input Preprocessing (with embeddings)
2. Memory layer operations (STM, MTM, LTM)
3. Memory aggregation and ranking
4. Context compression
5. Response synthesis
"""

import sys
from config import get_config
from core import (
    ShortTermMemory, MidTermMemory, LongTermMemory,
    Summarizer, MemoryOrchestrator,
    InputPreprocessor, MemoryAggregator, ContextCompressor, ResponseSynthesizer
)
from bot import ChatBot, ResponseGenerator
from utils import setup_logger

def demo_preprocessing():
    """Demo: Input preprocessing with embeddings."""
    print("=" * 60)
    print("DEMO 1: Input Preprocessing")
    print("=" * 60)
    
    preprocessor = InputPreprocessor(embedding_dim=128)
    
    queries = [
        "Find bug in checkpoints.rs",
        "Explain how the AST parser works",
        "Show me the git commit history"
    ]
    
    for query in queries:
        result = preprocessor.preprocess(query)
        print(f"\nQuery: {result['raw_text']}")
        print(f"Intent: {result['intent']}")
        print(f"Keywords: {result['keywords']}")
        print(f"Embedding shape: {len(result['embedding'])} dims")
        print(f"Normalized: {result['normalized_text']}")

def demo_memory_layers():
    """Demo: Memory layer operations."""
    print("\n" + "=" * 60)
    print("DEMO 2: Memory Layer Operations")
    print("=" * 60)
    
    preprocessor = InputPreprocessor(embedding_dim=128)
    stm = ShortTermMemory(max_size=5)
    mtm = MidTermMemory(max_size=10)
    
    # Add messages with embeddings
    messages = [
        ("user", "Hello, how are you?"),
        ("assistant", "I'm doing great! How can I help?"),
        ("user", "Can you help me debug my code?"),
        ("assistant", "Of course! Please share your code."),
        ("user", "Here's the error in my Python script"),
    ]
    
    print("\n--- Adding messages to STM ---")
    for role, content in messages:
        query_obj = preprocessor.preprocess(content)
        stm.add(role, content, embedding=query_obj['embedding'])
        print(f"{role}: {content[:50]}...")
    
    print(f"\nSTM size: {len(stm.messages)}")
    
    # Test embedding search
    print("\n--- Testing Embedding Search ---")
    search_query = "code debugging help"
    query_obj = preprocessor.preprocess(search_query)
    results = stm.search_by_embedding(query_obj['embedding'], top_k=3)
    
    print(f"Search query: '{search_query}'")
    print(f"Top {len(results)} results:")
    for i, msg in enumerate(results, 1):
        print(f"  {i}. [{msg['role']}] {msg['content'][:60]}...")

def demo_aggregation():
    """Demo: Memory aggregation with ranking."""
    print("\n" + "=" * 60)
    print("DEMO 3: Memory Aggregation & Ranking")
    print("=" * 60)
    
    preprocessor = InputPreprocessor(embedding_dim=128)
    aggregator = MemoryAggregator(stm_weight=0.5, mtm_weight=0.3, ltm_weight=0.2)
    
    # Mock contexts
    stm_context = [
        {'role': 'user', 'content': 'Latest message about debugging', 'metadata': {}},
        {'role': 'assistant', 'content': 'Here is how to debug', 'metadata': {}},
    ]
    
    mtm_context = [
        {'summary': 'Previous discussion about code quality', 'metadata': {}, 'timestamp': '2024-01-01'},
        {'summary': 'Conversation about testing strategies', 'metadata': {}, 'timestamp': '2024-01-02'},
    ]
    
    # Test aggregation
    query = "debugging code issues"
    query_obj = preprocessor.preprocess(query)
    
    aggregated = aggregator.aggregate(
        stm_context=stm_context,
        mtm_context=mtm_context,
        query_embedding=query_obj['embedding']
    )
    
    print(f"\nAggregated items: {aggregated['total_items']}")
    print(f"STM items: {aggregated['stm_count']}")
    print(f"MTM items: {aggregated['mtm_count']}")
    
    print("\n--- Top ranked items ---")
    for item in aggregated['items'][:5]:
        print(f"[{item['source']}] Score: {item['final_score']:.3f}")
        print(f"  Content: {item['content'][:70]}...")

def demo_compression():
    """Demo: Context compression."""
    print("\n" + "=" * 60)
    print("DEMO 4: Context Compression")
    print("=" * 60)
    
    compressor = ContextCompressor(max_tokens=500, strategy='score_based')
    
    # Mock aggregated context
    aggregated_context = {
        'items': [
            {'content': 'This is message 1 ' * 20, 'source': 'short_term', 'final_score': 0.9},
            {'content': 'This is message 2 ' * 20, 'source': 'short_term', 'final_score': 0.8},
            {'content': 'This is message 3 ' * 20, 'source': 'mid_term', 'final_score': 0.7},
            {'content': 'This is message 4 ' * 20, 'source': 'mid_term', 'final_score': 0.6},
            {'content': 'This is message 5 ' * 20, 'source': 'long_term', 'final_score': 0.5},
        ]
    }
    
    compressed = compressor.compress(aggregated_context, preserve_recent=True)
    
    print(f"\nOriginal tokens: {compressed['original_tokens']}")
    print(f"Compressed tokens: {compressed['total_tokens']}")
    print(f"Compression ratio: {compressed['compression_ratio']:.1%}")
    print(f"Items kept: {compressed['items_kept']}/{len(aggregated_context['items'])}")
    print(f"Strategy: {compressed['strategy']}")

def demo_synthesis():
    """Demo: Response synthesis."""
    print("\n" + "=" * 60)
    print("DEMO 5: Response Synthesis")
    print("=" * 60)
    
    synthesizer = ResponseSynthesizer(output_format='markdown')
    
    raw_response = """Here's how to fix your bug:
    
1. Check the variable scope
2. Ensure proper initialization
3. Add error handling

This should resolve the issue."""
    
    context_metadata = {
        'total_tokens': 450,
        'compression_ratio': 0.65,
        'items_kept': 3,
    }
    
    query_info = {
        'intent': 'debug',
        'keywords': ['bug', 'fix', 'error'],
    }
    
    response_dict = synthesizer.synthesize(
        raw_response,
        context_metadata=context_metadata,
        query_info=query_info
    )
    
    print("\n--- Synthesized Response ---")
    print(f"Format: {response_dict['format']}")
    print(f"Timestamp: {response_dict['timestamp']}")
    
    if 'context_info' in response_dict:
        print(f"\nContext used:")
        print(f"  Tokens: {response_dict['context_info']['total_tokens']}")
        print(f"  Compression: {response_dict['context_info']['compression_ratio']:.1%}")
    
    if 'query_info' in response_dict:
        print(f"\nQuery info:")
        print(f"  Intent: {response_dict['query_info']['intent']}")
        print(f"  Keywords: {response_dict['query_info']['keywords']}")
    
    print(f"\nFormatted response:\n{response_dict['response']}")

def demo_full_workflow():
    """Demo: Complete workflow end-to-end."""
    print("\n" + "=" * 60)
    print("DEMO 6: Complete Workflow")
    print("=" * 60)
    
    # Setup
    config = get_config()
    from main import create_chatbot
    
    chatbot = create_chatbot(config, use_advanced_workflow=True)
    
    print("\n--- Starting Chatbot with Advanced Workflow ---")
    print(chatbot.start())
    
    # Conversation
    test_messages = [
        "Hello! I need help with debugging.",
        "I have a bug in my Python code.",
        "The error says 'undefined variable'.",
        "How do I fix this?",
        "Thanks for your help!",
    ]
    
    print("\n--- Conversation ---")
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        response = chatbot.chat(msg, use_embedding_search=False)
        print(f"🤖 Bot: {response}")
    
    # Show stats
    print("\n--- Conversation Statistics ---")
    stats = chatbot.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("Memory Layer Lab - Workflow Demo")
    print("=" * 60)
    
    # Setup logging
    setup_logger('memory_layer', level='WARNING')  # Reduce noise
    
    try:
        demo_preprocessing()
        demo_memory_layers()
        demo_aggregation()
        demo_compression()
        demo_synthesis()
        demo_full_workflow()
        
        print("\n" + "=" * 60)
        print("✅ All demos completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
