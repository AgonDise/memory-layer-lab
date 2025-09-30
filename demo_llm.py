#!/usr/bin/env python3
"""
Demo: Complete workflow with real LLM integration.

This demonstrates the full memory layer system with LLM API.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import sys
from config import get_config
from utils import FakeEmbeddingGenerator, get_llm_client
from core import (
    ShortTermMemory, MidTermMemory, LongTermMemory,
    InputPreprocessor, MemoryOrchestrator, Summarizer,
    MemoryAggregator, ContextCompressor, ResponseSynthesizer
)
from bot import ResponseGenerator

def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main():
    """Run LLM demo."""
    print_section("🚀 Memory Layer Lab - LLM Integration Demo")
    
    # Get configuration
    config = get_config()
    llm_config = config['llm']
    
    # Check for API keys
    print("\n📋 Checking LLM Configuration...")
    provider = llm_config['provider']
    
    if provider == 'openai':
        api_key = llm_config['openai']['api_key'] or os.getenv('OPENAI_API_KEY')
        if api_key:
            print(f"✓ OpenAI API key found (starts with: {api_key[:10]}...)")
        else:
            print("⚠️  No OpenAI API key found")
            print("   Set OPENAI_API_KEY environment variable or edit config.py")
            print("   Using mock LLM for demo...")
            provider = 'mock'
    
    elif provider == 'anthropic':
        api_key = llm_config['anthropic']['api_key'] or os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            print(f"✓ Anthropic API key found (starts with: {api_key[:10]}...)")
        else:
            print("⚠️  No Anthropic API key found")
            print("   Set ANTHROPIC_API_KEY environment variable or edit config.py")
            print("   Using mock LLM for demo...")
            provider = 'mock'
    
    # Initialize LLM client
    print(f"\n🤖 Initializing LLM Client ({provider})...")
    if provider == 'openai':
        llm_client = get_llm_client('openai', 
                                     api_key=api_key,
                                     model=llm_config['openai']['model'])
    elif provider == 'anthropic':
        llm_client = get_llm_client('anthropic',
                                      api_key=api_key,
                                      model=llm_config['anthropic']['model'])
    else:
        llm_client = get_llm_client('mock')
    
    print(f"✓ LLM client ready: {llm_client.__class__.__name__}")
    
    # Initialize memory layers
    print("\n💾 Initializing Memory Layers...")
    stm = ShortTermMemory(max_size=10)
    mtm = MidTermMemory(max_size=100)
    ltm = LongTermMemory(enabled=False)
    summarizer = Summarizer()
    print("✓ Memory layers initialized")
    
    # Initialize other components
    print("\n🔧 Initializing Components...")
    preprocessor = InputPreprocessor(embedding_dim=384)
    orchestrator = MemoryOrchestrator(stm, mtm, ltm, summarizer)
    aggregator = MemoryAggregator()
    compressor = ContextCompressor(max_tokens=2000)
    synthesizer = ResponseSynthesizer(output_format='markdown')
    
    # Initialize response generator with LLM
    response_generator = ResponseGenerator(
        mode='llm',
        llm_config=llm_config,
        llm_client=llm_client
    )
    print("✓ All components initialized")
    
    # Populate some data for context
    print_section("📊 Populating Sample Data")
    
    sample_conversations = [
        {
            'role': 'user',
            'content': 'Hãy phân tích hàm login_user trong file auth_service.py'
        },
        {
            'role': 'assistant',
            'content': 'Hàm login_user xử lý xác thực người dùng, tạo JWT token và quản lý session.'
        },
        {
            'role': 'user',
            'content': 'Commit abc123 có bug gì không?'
        },
        {
            'role': 'assistant',
            'content': 'Commit abc123 fix bug undefined variable trong checkpoints.rs và thêm OAuth2 support.'
        }
    ]
    
    for msg in sample_conversations:
        # Preprocess
        preprocessed = preprocessor.preprocess(msg['content'])
        
        # Add to memory
        orchestrator.add_message(
            role=msg['role'],
            content=msg['content'],
            embedding=preprocessed['embedding']
        )
        print(f"✓ Added: [{msg['role']}] {msg['content'][:50]}...")
    
    print(f"\n✓ STM: {len(stm.messages)} messages")
    print(f"✓ MTM: {len(mtm.chunks)} chunks")
    
    # Demo queries
    print_section("💬 Demo Conversations with LLM")
    
    test_queries = [
        "Tell me about the login_user function",
        "What bug was fixed in commit abc123?",
        "Explain OAuth2 authentication",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─' * 70}")
        print(f"Query {i}: {query}")
        print(f"{'─' * 70}")
        
        # 1. Preprocess query
        preprocessed = preprocessor.preprocess(query)
        print(f"\n  Intent: {preprocessed['intent']}")
        print(f"  Keywords: {', '.join(preprocessed['keywords'][:5])}")
        
        # 2. Retrieve from memory layers
        memory_context = orchestrator.get_context(
            query=query,
            n_recent=3,
            n_chunks=2
        )
        
        # 3. Get aggregated and compressed context
        aggregated = memory_context['aggregated']
        compressed = memory_context['compressed']
        
        print(f"\n  📝 Retrieved {aggregated.get('stm_count', 0)} STM + {aggregated.get('mtm_count', 0)} MTM items")
        
        # 4. Build context text for LLM
        context_items = compressed.get('items', [])
        context_text = "\n".join([
            f"- {item.get('content', item.get('summary', 'N/A'))}"
            for item in context_items[:5]
        ])
        
        # 5. Generate response with LLM
        print(f"\n  🤖 Generating response with {llm_client.__class__.__name__}...")
        
        raw_response = response_generator.generate(
            user_message=query,
            context=context_text
        )
        
        # 6. Synthesize final response
        final_response = synthesizer.synthesize(
            raw_response=raw_response,
            context_metadata={
                'stm_count': aggregated.get('stm_count', 0),
                'mtm_count': aggregated.get('mtm_count', 0),
                'compressed_items': len(context_items),
                'llm_provider': provider
            }
        )
        
        # Display response
        print(f"\n  💬 Response:")
        print(f"  {'-' * 66}")
        for line in final_response['response'].split('\n'):
            print(f"  {line}")
        print(f"  {'-' * 66}")
        
        # Add to memory
        orchestrator.add_message(
            role='user',
            content=query,
            embedding=preprocessed['embedding']
        )
        orchestrator.add_message(
            role='assistant',
            content=raw_response,
            embedding=preprocessor.preprocess(raw_response)['embedding']
        )
    
    # Summary
    print_section("📈 Demo Summary")
    print(f"✓ Processed {len(test_queries)} queries")
    print(f"✓ STM: {len(stm.messages)} messages")
    print(f"✓ MTM: {len(mtm.chunks)} chunks")
    print(f"✓ LLM Provider: {provider}")
    print(f"✓ Memory retrieval working")
    print(f"✓ Context compression working")
    print(f"✓ LLM generation working")
    
    print("\n" + "=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    
    print("\n💡 Next Steps:")
    if provider == 'mock':
        print("  • Set your API key to use real LLM:")
        print("    export OPENAI_API_KEY='your-key-here'")
        print("    or")
        print("    export ANTHROPIC_API_KEY='your-key-here'")
        print("  • Edit config.py to set provider and model")
    else:
        print("  • Try your own queries")
        print("  • Add more data to schema.yaml")
        print("  • Adjust LLM parameters in config.py")
    print("  • Run: python main.py for interactive chat")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
