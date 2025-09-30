#!/usr/bin/env python3
"""
Simple test to verify all modules can be imported and instantiated.
"""

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from core import (
            ShortTermMemory, MidTermMemory, LongTermMemory,
            Summarizer, MemoryOrchestrator,
            InputPreprocessor, MemoryAggregator, 
            ContextCompressor, ResponseSynthesizer
        )
        print("✓ Core modules imported successfully")
        
        from bot import ChatBot, ResponseGenerator
        print("✓ Bot modules imported successfully")
        
        from utils import setup_logger, MemoryStorage
        print("✓ Utils modules imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_instantiation():
    """Test that all classes can be instantiated."""
    print("\nTesting instantiation...")
    
    try:
        from core import (
            ShortTermMemory, MidTermMemory, LongTermMemory,
            Summarizer, InputPreprocessor, 
            MemoryAggregator, ContextCompressor, ResponseSynthesizer
        )
        
        # Test memory layers
        stm = ShortTermMemory(max_size=10)
        print("✓ ShortTermMemory created")
        
        mtm = MidTermMemory(max_size=100)
        print("✓ MidTermMemory created")
        
        ltm = LongTermMemory(enabled=False)
        print("✓ LongTermMemory created")
        
        # Test core components
        summarizer = Summarizer(strategy='simple')
        print("✓ Summarizer created")
        
        preprocessor = InputPreprocessor(embedding_dim=128)
        print("✓ InputPreprocessor created")
        
        aggregator = MemoryAggregator()
        print("✓ MemoryAggregator created")
        
        compressor = ContextCompressor(max_tokens=1000)
        print("✓ ContextCompressor created")
        
        synthesizer = ResponseSynthesizer()
        print("✓ ResponseSynthesizer created")
        
        return True
    except Exception as e:
        print(f"✗ Instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_workflow():
    """Test basic workflow operations."""
    print("\nTesting basic workflow...")
    
    try:
        from core import InputPreprocessor, ShortTermMemory
        
        # Test preprocessing
        preprocessor = InputPreprocessor(embedding_dim=128)
        query_obj = preprocessor.preprocess("Test query about debugging")
        
        assert 'embedding' in query_obj
        assert 'intent' in query_obj
        assert 'keywords' in query_obj
        assert len(query_obj['embedding']) == 128
        print("✓ Input preprocessing works")
        
        # Test memory operations
        stm = ShortTermMemory(max_size=5)
        stm.add('user', 'Hello', embedding=query_obj['embedding'])
        stm.add('assistant', 'Hi there!')
        
        messages = stm.get_recent()
        assert len(messages) == 2
        print("✓ Short-term memory operations work")
        
        # Test embedding search
        results = stm.search_by_embedding(query_obj['embedding'], top_k=2)
        assert len(results) <= 2
        print("✓ Embedding search works")
        
        return True
    except Exception as e:
        print(f"✗ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Memory Layer Lab - Simple Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Instantiation", test_instantiation()))
    results.append(("Basic Workflow", test_basic_workflow()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed!")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
