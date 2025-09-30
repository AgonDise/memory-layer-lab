#!/usr/bin/env python3
"""
Quick test of evaluation and metrics system.
"""

import sys
from evaluation import MemoryEvaluator, MetricsCollector, QueryMetrics
from datetime import datetime

def test_evaluator():
    """Test evaluation framework."""
    print("=" * 70)
    print("Testing Evaluation Framework")
    print("=" * 70)
    
    evaluator = MemoryEvaluator()
    
    # Create test case
    test_cases = [
        {
            'query': 'Tell me about login_user function',
            'retrieved_items': [
                {'id': '1', 'content': 'login_user handles authentication'},
                {'id': '2', 'content': 'creates JWT token'},
                {'id': '3', 'content': 'manages session state'},
            ],
            'ground_truth_items': [
                {'id': '1', 'content': 'login_user handles authentication'},
                {'id': '2', 'content': 'creates JWT token'},
                {'id': '4', 'content': 'validates credentials'},
            ],
            'original_items': [
                {'content': 'Long text about login function and how it works with authentication system'},
                {'content': 'Another long piece of context about JWT tokens and session management'},
                {'content': 'More detailed information about the authentication flow'},
                {'content': 'Additional context that might be less relevant'},
                {'content': 'Even more context about related topics'},
            ],
            'compressed_items': [
                {'content': 'login_user handles authentication'},
                {'content': 'creates JWT token'},
            ],
            'token_budget': 2000,
            'context': 'login_user handles authentication and creates JWT tokens for session management',
            'response': 'The login_user function is responsible for user authentication. It validates credentials, creates JWT tokens for authenticated sessions, and manages the session state.',
        }
    ]
    
    # Run evaluation
    print("\n📊 Running evaluation suite...")
    results = evaluator.run_evaluation_suite(test_cases)
    
    # Generate report
    print("\n" + evaluator.generate_report(results))
    
    # Check metrics
    if results['summary']:
        print("\n✅ Evaluation completed successfully!")
        print(f"   Avg Precision: {results['summary'].get('avg_precision', 0):.3f}")
        print(f"   Avg Recall: {results['summary'].get('avg_recall', 0):.3f}")
        print(f"   Avg F1: {results['summary'].get('avg_f1', 0):.3f}")
        print(f"   Avg Compression: {results['summary'].get('avg_compression_ratio', 0):.2%}")
        print(f"   Avg Efficiency: {results['summary'].get('avg_efficiency', 0):.3f}")
    
    return True

def test_metrics_collector():
    """Test metrics collection."""
    print("\n" + "=" * 70)
    print("Testing Metrics Collector")
    print("=" * 70)
    
    collector = MetricsCollector()
    
    # Simulate some queries
    print("\n📈 Simulating queries...")
    intents = ['general', 'debug', 'documentation', 'code_search', 'general']
    
    for i in range(5):
        metrics = QueryMetrics(
            timestamp=datetime.now().isoformat(),
            query=f"Test query {i+1}",
            intent=intents[i],
            stm_hits=3,
            mtm_hits=2,
            ltm_hits=0,
            total_retrieved=5,
            original_items=10,
            compressed_items=4,
            compression_ratio=0.4,
            preprocessing_time=0.05,
            retrieval_time=0.15,
            generation_time=0.8,
            total_time=1.0,
            response_length=180,
            context_utilization=0.65
        )
        collector.record_query(metrics)
        print(f"  ✓ Query {i+1} recorded")
    
    # Generate report
    print("\n" + collector.generate_report())
    
    # Save metrics
    try:
        collector.save('test_metrics.json')
        print("\n✅ Metrics saved to test_metrics.json")
    except Exception as e:
        print(f"\n⚠️  Could not save metrics: {e}")
    
    return True

def main():
    """Run all tests."""
    print("\n🧪 Memory Layer Lab - Evaluation System Test\n")
    
    try:
        # Test evaluator
        if test_evaluator():
            print("\n✅ Evaluator test passed!")
        
        # Test metrics collector
        if test_metrics_collector():
            print("\n✅ Metrics collector test passed!")
        
        print("\n" + "=" * 70)
        print("🎉 All tests passed!")
        print("=" * 70)
        
        print("\n💡 Next steps:")
        print("  • Use evaluator for system evaluation")
        print("  • Use collector for runtime metrics")
        print("  • Launch UI: python ui_chat.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
