#!/usr/bin/env python3
"""
Comprehensive Test Suite for Memory Layer Lab
Test all layers (STM, MTM, LTM) with detailed analysis and metrics.
"""

import os
import json
import time
from typing import Dict, Any, List, Tuple
from datetime import datetime
from collections import defaultdict
import statistics

from config import get_config
from utils import FakeEmbeddingGenerator, get_llm_client
from core import (
    ShortTermMemory, MidTermMemory, LongTermMemory,
    InputPreprocessor, MemoryOrchestrator, Summarizer,
    MemoryAggregator, ContextCompressor, ResponseSynthesizer
)
from bot import ResponseGenerator
from evaluation import MemoryEvaluator, MetricsCollector


class ComprehensiveTest:
    """Comprehensive test suite for memory layers."""
    
    def __init__(self):
        """Initialize test suite."""
        self.config = get_config()
        self.setup_components()
        self.results = {
            'stm_tests': [],
            'mtm_tests': [],
            'ltm_tests': [],
            'integration_tests': [],
            'performance_metrics': [],
            'memory_retrieval_analysis': [],
            'compression_analysis': []
        }
        self.evaluator = MemoryEvaluator()
        self.metrics_collector = MetricsCollector()
        
    def setup_components(self):
        """Setup all components."""
        print("🔧 Setting up components...")
        
        # Core components
        self.embedding_gen = FakeEmbeddingGenerator()
        self.preprocessor = InputPreprocessor(use_mock_embeddings=True)
        self.summarizer = Summarizer()
        self.aggregator = MemoryAggregator()
        self.compressor = ContextCompressor()
        self.synthesizer = ResponseSynthesizer()
        
        # Memory layers
        self.stm = ShortTermMemory(
            max_size=self.config['memory']['short_term']['max_size']
        )
        self.mtm = MidTermMemory(
            max_size=self.config['memory']['mid_term']['max_size']
        )
        self.ltm = LongTermMemory()
        
        # Orchestrator
        self.orchestrator = MemoryOrchestrator(
            short_term=self.stm,
            mid_term=self.mtm,
            long_term=self.ltm,
            aggregator=self.aggregator,
            compressor=self.compressor,
            preprocessor=self.preprocessor,
            summarizer=self.summarizer
        )
        
        # Response generator (use mock mode for testing)
        self.bot = ResponseGenerator(mode='mock')
        
        print("✅ Components ready!\n")
    
    def load_test_data(self, filepath: str = 'short_term.json') -> List[Dict[str, Any]]:
        """Load test data from JSON file."""
        print(f"📂 Loading test data from {filepath}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {len(data)} messages\n")
            return data
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return []
    
    def test_stm_layer(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test Short-Term Memory layer."""
        print("=" * 80)
        print("🧪 Testing Short-Term Memory (STM) Layer")
        print("=" * 80)
        
        results = {
            'total_messages': len(messages),
            'added_count': 0,
            'retrieval_tests': [],
            'performance': []
        }
        
        # Add messages to STM
        print("\n1️⃣ Adding messages to STM...")
        for msg in messages[:20]:  # Test with first 20 messages
            if msg.get('role') in ['user', 'assistant']:
                start_time = time.time()
                self.stm.add(
                    role=msg['role'],
                    content=msg['content'],
                    embedding=self.embedding_gen.generate(msg['content'])
                )
                elapsed = time.time() - start_time
                results['added_count'] += 1
                results['performance'].append(elapsed)
        
        print(f"   ✓ Added {results['added_count']} messages")
        print(f"   ⏱️  Avg time: {statistics.mean(results['performance']):.4f}s")
        
        # Test retrieval
        print("\n2️⃣ Testing STM retrieval...")
        test_queries = [
            "Tôi là ai?",
            "Tôi làm nghề gì?",
            "Hướng dẫn nấu gà chiên",
            "OpenAI API",
            "Valorant"
        ]
        
        for query in test_queries:
            start_time = time.time()
            # Simply get recent messages (STM doesn't filter by embedding)
            retrieved = self.stm.get_recent(n=5)
            elapsed = time.time() - start_time
            
            results['retrieval_tests'].append({
                'query': query,
                'retrieved_count': len(retrieved),
                'time': elapsed
            })
            print(f"   Query: '{query[:40]}...' → {len(retrieved)} results ({elapsed:.4f}s)")
        
        # Memory status
        print("\n3️⃣ STM Memory Status:")
        print(f"   Total items: {len(self.stm.messages)}")
        print(f"   Max capacity: {self.stm.max_size}")
        print(f"   Fill rate: {len(self.stm.messages) / self.stm.max_size * 100:.1f}%")
        
        self.results['stm_tests'].append(results)
        return results
    
    def test_mtm_layer(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test Mid-Term Memory layer."""
        print("\n" + "=" * 80)
        print("🧪 Testing Mid-Term Memory (MTM) Layer")
        print("=" * 80)
        
        results = {
            'total_messages': len(messages),
            'chunks_created': 0,
            'summarization_tests': [],
            'retrieval_tests': [],
            'performance': []
        }
        
        # Add chunks to MTM
        print("\n1️⃣ Creating and adding summary chunks...")
        # Group messages into chunks and add to MTM
        chunk_size = 5
        for i in range(0, min(30, len(messages)), chunk_size):
            chunk_messages = messages[i:i+chunk_size]
            # Create a summary from messages
            summary_text = f"Summary of {len(chunk_messages)} messages about: "
            topics = []
            for msg in chunk_messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '')[:50]
                    topics.append(content)
            summary_text += ', '.join(topics[:3])
            
            start_time = time.time()
            self.mtm.add_chunk(
                summary=summary_text,
                metadata={
                    'message_count': len(chunk_messages),
                    'timestamp': datetime.now().isoformat()
                }
            )
            elapsed = time.time() - start_time
            results['performance'].append(elapsed)
            results['chunks_created'] += 1
        
        print(f"   ✓ Processed {len(messages[:30])} messages")
        print(f"   ✓ Created {results['chunks_created']} summary chunks")
        print(f"   ⏱️  Avg time: {statistics.mean(results['performance']):.4f}s")
        
        # Test retrieval
        print("\n2️⃣ Testing MTM retrieval...")
        test_queries = [
            "AI Engineer",
            "đầu bếp Sasukekeke",
            "Cognee AI chatbot",
            "món ăn Nhật Bản"
        ]
        
        for query in test_queries:
            start_time = time.time()
            # Get recent chunks from MTM
            retrieved = self.mtm.get_recent_chunks(n=3)
            elapsed = time.time() - start_time
            
            results['retrieval_tests'].append({
                'query': query,
                'retrieved_count': len(retrieved),
                'time': elapsed
            })
            print(f"   Query: '{query}' → {len(retrieved)} chunks ({elapsed:.4f}s)")
        
        # MTM status
        print("\n3️⃣ MTM Memory Status:")
        print(f"   Total chunks: {len(self.mtm.chunks)}")
        print(f"   Max capacity: {self.mtm.max_size}")
        
        self.results['mtm_tests'].append(results)
        return results
    
    def test_ltm_layer(self) -> Dict[str, Any]:
        """Test Long-Term Memory layer."""
        print("\n" + "=" * 80)
        print("🧪 Testing Long-Term Memory (LTM) Layer")
        print("=" * 80)
        
        results = {
            'enabled': self.ltm.enabled,
            'status': 'placeholder'
        }
        
        print("\n⚠️  LTM is currently a placeholder implementation")
        print("   Future: Will store semantic knowledge graphs")
        
        self.results['ltm_tests'].append(results)
        return results
    
    def test_memory_orchestrator(self) -> Dict[str, Any]:
        """Test Memory Orchestrator integration."""
        print("\n" + "=" * 80)
        print("🧪 Testing Memory Orchestrator (Integration)")
        print("=" * 80)
        
        results = {
            'context_retrieval_tests': [],
            'aggregation_tests': [],
            'compression_tests': []
        }
        
        test_queries = [
            {
                'query': 'Tôi là ai?',
                'expected_context': ['AI Engineer', 'đầu bếp', 'Sasukekeke']
            },
            {
                'query': 'Hướng dẫn tôi nấu món gà chiên',
                'expected_context': ['gà chiên', 'nguyên liệu', 'cách làm']
            },
            {
                'query': 'OpenAI API trong Python',
                'expected_context': ['OpenAI', 'API', 'Python', 'openai']
            },
            {
                'query': 'Valorant agents',
                'expected_context': ['Valorant', 'agent', 'nhân vật']
            }
        ]
        
        print("\n1️⃣ Testing context retrieval...")
        for test_case in test_queries:
            query = test_case['query']
            expected = test_case['expected_context']
            
            start_time = time.time()
            context = self.orchestrator.get_context(query=query, n_recent=5, n_chunks=3)
            elapsed = time.time() - start_time
            
            aggregated = context['aggregated']
            compressed = context['compressed']
            
            # Check if expected context is present
            context_text = json.dumps(aggregated, ensure_ascii=False).lower()
            found_keywords = sum(1 for kw in expected if kw.lower() in context_text)
            relevance_score = found_keywords / len(expected) if expected else 0
            
            # Get actual items from aggregated context
            aggregated_items = aggregated.get('items', [])
            compressed_items = compressed.get('compressed_items', [])
            
            result = {
                'query': query,
                'stm_count': aggregated.get('stm_count', 0),
                'mtm_count': aggregated.get('mtm_count', 0),
                'compressed_items': len(compressed_items),
                'original_items': len(aggregated_items),
                'compression_ratio': compressed.get('compression_ratio', 0),
                'relevance_score': relevance_score,
                'time': elapsed
            }
            
            results['context_retrieval_tests'].append(result)
            
            print(f"\n   Query: '{query}'")
            print(f"   ├─ STM: {result['stm_count']} items")
            print(f"   ├─ MTM: {result['mtm_count']} items")
            print(f"   ├─ Compressed: {result['original_items']} → {result['compressed_items']} items")
            print(f"   ├─ Compression: {result['compression_ratio']:.1%}")
            print(f"   ├─ Relevance: {relevance_score:.1%}")
            print(f"   └─ Time: {elapsed:.4f}s")
        
        self.results['integration_tests'].append(results)
        return results
    
    def test_end_to_end_queries(self) -> Dict[str, Any]:
        """Test end-to-end query processing."""
        print("\n" + "=" * 80)
        print("🧪 Testing End-to-End Query Processing")
        print("=" * 80)
        
        results = {
            'queries': []
        }
        
        test_queries = [
            "Tôi là ai và làm nghề gì?",
            "Hãy nhắc lại thông tin về nhà hàng tôi làm việc",
            "Tôi đã hỏi gì về Valorant?",
            "Cho tôi biết về các món ăn tôi đã hỏi",
        ]
        
        print("\n1️⃣ Processing queries with full pipeline...")
        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            
            start_time = time.time()
            try:
                # Use orchestrator to get context
                context = self.orchestrator.get_context(query=query, n_recent=5, n_chunks=3)
                
                # Generate mock response based on context
                aggregated = context['aggregated']
                compressed = context['compressed']
                
                compressed_items = compressed.get('compressed_items', [])
                response = f"Mock response for '{query[:30]}...' using {aggregated.get('stm_count', 0)} STM + {aggregated.get('mtm_count', 0)} MTM items"
                
                elapsed = time.time() - start_time
                
                result = {
                    'query': query,
                    'response': response,
                    'stm_count': aggregated.get('stm_count', 0),
                    'mtm_count': aggregated.get('mtm_count', 0),
                    'compressed_items': len(compressed_items),
                    'original_items': len(aggregated.get('items', [])),
                    'compression_ratio': compressed.get('compression_ratio', 0),
                    'time': elapsed,
                    'success': True
                }
                
                print(f"   ✓ Context: {result['stm_count']} STM + {result['mtm_count']} MTM")
                print(f"   ✓ Compressed to: {result['compressed_items']} items")
                print(f"   ⏱️  Time: {elapsed:.4f}s")
                
            except Exception as e:
                result = {
                    'query': query,
                    'error': str(e),
                    'time': 0,
                    'success': False
                }
                print(f"   ❌ Error: {e}")
            
            results['queries'].append(result)
        
        return results
    
    def analyze_compression_effectiveness(self) -> Dict[str, Any]:
        """Analyze compression effectiveness across tests."""
        print("\n" + "=" * 80)
        print("📊 Analyzing Compression Effectiveness")
        print("=" * 80)
        
        if not self.results['integration_tests']:
            print("⚠️  No integration test data available")
            return {}
        
        compression_data = []
        for test in self.results['integration_tests']:
            for result in test.get('context_retrieval_tests', []):
                if result.get('compression_ratio'):
                    compression_data.append({
                        'original': result['original_items'],
                        'compressed': result['compressed_items'],
                        'ratio': result['compression_ratio'],
                        'query': result['query']
                    })
        
        if not compression_data:
            print("⚠️  No compression data available")
            return {}
        
        avg_ratio = statistics.mean([d['ratio'] for d in compression_data])
        avg_original = statistics.mean([d['original'] for d in compression_data])
        avg_compressed = statistics.mean([d['compressed'] for d in compression_data])
        
        analysis = {
            'total_tests': len(compression_data),
            'avg_compression_ratio': avg_ratio,
            'avg_original_items': avg_original,
            'avg_compressed_items': avg_compressed,
            'compression_details': compression_data
        }
        
        print(f"\n📈 Compression Analysis:")
        print(f"   Total tests: {analysis['total_tests']}")
        print(f"   Avg original items: {avg_original:.1f}")
        print(f"   Avg compressed items: {avg_compressed:.1f}")
        print(f"   Avg compression ratio: {avg_ratio:.1%}")
        
        if avg_ratio >= 0.30 and avg_ratio <= 0.50:
            print(f"   ✅ Compression is GOOD (30-50% range)")
        elif avg_ratio < 0.30:
            print(f"   ⚠️  Compression is HIGH (may lose context)")
        else:
            print(f"   ⚠️  Compression is LOW (may be inefficient)")
        
        self.results['compression_analysis'].append(analysis)
        return analysis
    
    def analyze_memory_retrieval_quality(self) -> Dict[str, Any]:
        """Analyze memory retrieval quality."""
        print("\n" + "=" * 80)
        print("📊 Analyzing Memory Retrieval Quality")
        print("=" * 80)
        
        if not self.results['integration_tests']:
            print("⚠️  No integration test data available")
            return {}
        
        retrieval_data = []
        for test in self.results['integration_tests']:
            for result in test.get('context_retrieval_tests', []):
                retrieval_data.append({
                    'relevance': result.get('relevance_score', 0),
                    'stm_count': result.get('stm_count', 0),
                    'mtm_count': result.get('mtm_count', 0),
                    'time': result.get('time', 0),
                    'query': result['query']
                })
        
        if not retrieval_data:
            print("⚠️  No retrieval data available")
            return {}
        
        avg_relevance = statistics.mean([d['relevance'] for d in retrieval_data])
        avg_stm = statistics.mean([d['stm_count'] for d in retrieval_data])
        avg_mtm = statistics.mean([d['mtm_count'] for d in retrieval_data])
        avg_time = statistics.mean([d['time'] for d in retrieval_data])
        
        analysis = {
            'total_queries': len(retrieval_data),
            'avg_relevance_score': avg_relevance,
            'avg_stm_hits': avg_stm,
            'avg_mtm_hits': avg_mtm,
            'avg_retrieval_time': avg_time,
            'retrieval_details': retrieval_data
        }
        
        print(f"\n📈 Retrieval Quality Analysis:")
        print(f"   Total queries: {analysis['total_queries']}")
        print(f"   Avg relevance score: {avg_relevance:.1%}")
        print(f"   Avg STM hits: {avg_stm:.1f}")
        print(f"   Avg MTM hits: {avg_mtm:.1f}")
        print(f"   Avg retrieval time: {avg_time:.4f}s")
        
        if avg_relevance >= 0.70:
            print(f"   ✅ Retrieval quality is EXCELLENT")
        elif avg_relevance >= 0.50:
            print(f"   ✓ Retrieval quality is GOOD")
        else:
            print(f"   ⚠️  Retrieval quality needs improvement")
        
        self.results['memory_retrieval_analysis'].append(analysis)
        return analysis
    
    def generate_report(self, output_file: str = 'comprehensive_test_report.json'):
        """Generate comprehensive test report."""
        print("\n" + "=" * 80)
        print("📝 Generating Comprehensive Report")
        print("=" * 80)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'stm_tests': len(self.results['stm_tests']),
                'mtm_tests': len(self.results['mtm_tests']),
                'ltm_tests': len(self.results['ltm_tests']),
                'integration_tests': len(self.results['integration_tests']),
            },
            'detailed_results': self.results
        }
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Report saved to: {output_file}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 TEST SUMMARY")
        print("=" * 80)
        
        if self.results['stm_tests']:
            stm = self.results['stm_tests'][0]
            print(f"\n✅ Short-Term Memory (STM):")
            print(f"   ├─ Messages added: {stm['added_count']}")
            print(f"   ├─ Retrieval tests: {len(stm['retrieval_tests'])}")
            print(f"   └─ Avg add time: {statistics.mean(stm['performance']):.4f}s")
        
        if self.results['mtm_tests']:
            mtm = self.results['mtm_tests'][0]
            print(f"\n✅ Mid-Term Memory (MTM):")
            print(f"   ├─ Chunks created: {mtm['chunks_created']}")
            print(f"   ├─ Retrieval tests: {len(mtm['retrieval_tests'])}")
            print(f"   └─ Avg add time: {statistics.mean(mtm['performance']):.4f}s")
        
        if self.results['compression_analysis']:
            comp = self.results['compression_analysis'][0]
            print(f"\n✅ Compression Analysis:")
            print(f"   ├─ Avg compression ratio: {comp['avg_compression_ratio']:.1%}")
            print(f"   ├─ Avg original items: {comp['avg_original_items']:.1f}")
            print(f"   └─ Avg compressed items: {comp['avg_compressed_items']:.1f}")
        
        if self.results['memory_retrieval_analysis']:
            retr = self.results['memory_retrieval_analysis'][0]
            print(f"\n✅ Retrieval Quality:")
            print(f"   ├─ Avg relevance: {retr['avg_relevance_score']:.1%}")
            print(f"   ├─ Avg STM hits: {retr['avg_stm_hits']:.1f}")
            print(f"   ├─ Avg MTM hits: {retr['avg_mtm_hits']:.1f}")
            print(f"   └─ Avg time: {retr['avg_retrieval_time']:.4f}s")
        
        print("\n" + "=" * 80)
        print("🎉 COMPREHENSIVE TEST COMPLETE!")
        print("=" * 80)
        
        return report
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("\n" + "=" * 80)
        print("🚀 STARTING COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        # Load test data
        messages = self.load_test_data('short_term.json')
        if not messages:
            print("❌ No test data available. Exiting.")
            return
        
        # Run tests
        self.test_stm_layer(messages)
        self.test_mtm_layer(messages)
        self.test_ltm_layer()
        self.test_memory_orchestrator()
        self.test_end_to_end_queries()
        
        # Analysis
        self.analyze_compression_effectiveness()
        self.analyze_memory_retrieval_quality()
        
        # Generate report
        self.generate_report()
        
        total_time = time.time() - start_time
        print(f"\n⏱️  Total test duration: {total_time:.2f}s")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main entry point."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                     COMPREHENSIVE TEST SUITE                                ║
║                      Memory Layer Lab v1.0                                  ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    tester = ComprehensiveTest()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
