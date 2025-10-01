#!/usr/bin/env python3
"""
Test semantic search with real embeddings.

This script tests the semantic search capabilities with pre-generated
embedded data for MT and LT memory layers.
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List

from core.preprocessor import InputPreprocessor
from core.short_term import ShortTermMemory
from core.mid_term import MidTermMemory
from core.long_term import LongTermMemory
from core.orchestrator import MemoryOrchestrator
from core.summarizer import Summarizer
from core.aggregator import MemoryAggregator
from core.compressor import ContextCompressor

# Try to use real embeddings
try:
    from utils.real_embedding import RealEmbeddingGenerator
    embedder = RealEmbeddingGenerator()
    use_real_embeddings = True
    print(f"✅ Using RealEmbeddingGenerator (dim={embedder.embedding_dim})")
except Exception as e:
    from utils import FakeEmbeddingGenerator
    embedder = FakeEmbeddingGenerator()
    use_real_embeddings = False
    print(f"⚠️  Using FakeEmbeddingGenerator: {e}")


class SemanticSearchTest:
    """Test semantic search capabilities."""
    
    def __init__(self):
        """Initialize test components."""
        print("\n🔧 Initializing components...")
        
        # Create components with real embeddings
        self.preprocessor = InputPreprocessor(
            use_mock_embeddings=False,
            embedding_model=embedder
        )
        
        self.stm = ShortTermMemory(max_size=20)
        self.mtm = MidTermMemory(max_size=100)
        self.ltm = LongTermMemory()  # Add LTM
        self.summarizer = Summarizer()
        self.aggregator = MemoryAggregator()
        self.compressor = ContextCompressor(max_tokens=2000)
        
        self.orchestrator = MemoryOrchestrator(
            short_term=self.stm,
            mid_term=self.mtm,
            long_term=self.ltm,  # Add LTM
            summarizer=self.summarizer,
            aggregator=self.aggregator,
            compressor=self.compressor,
            preprocessor=self.preprocessor
        )
        
        print("✅ Components initialized")
    
    def load_test_data(self):
        """Load pre-generated test data with embeddings."""
        print("\n📂 Loading test data...")
        
        # Load STM data
        stm_file = "data/short_term.json"
        try:
            with open(stm_file, 'r', encoding='utf-8') as f:
                stm_data = json.load(f)
            
            # Add messages with embeddings
            messages_added = 0
            for msg in stm_data:
                if msg.get('role') in ['user', 'assistant']:
                    content = msg.get('content', '')
                    if content:
                        # Generate embedding
                        embedding = embedder.generate(content)
                        self.stm.add(
                            role=msg['role'],
                            content=content,
                            embedding=embedding
                        )
                        messages_added += 1
            
            print(f"   ✅ Loaded {messages_added} STM messages")
        except FileNotFoundError:
            print(f"   ⚠️  STM data not found: {stm_file}")
        
        # Load MTM data
        mtm_file = "data/mid_term_chunks.json"
        try:
            with open(mtm_file, 'r', encoding='utf-8') as f:
                mtm_data = json.load(f)
            
            # Add chunks
            chunks = mtm_data.get('chunks', [])
            for chunk in chunks:
                self.mtm.add_chunk(
                    summary=chunk['summary'],
                    embedding=chunk.get('embedding'),
                    metadata=chunk.get('metadata', {})
                )
            
            print(f"   ✅ Loaded {len(chunks)} MTM chunks")
        except FileNotFoundError:
            print(f"   ⚠️  MTM data not found: {mtm_file}")
        
        # Load LTM data
        ltm_file = "data/long_term_facts.json"
        try:
            with open(ltm_file, 'r', encoding='utf-8') as f:
                ltm_data = json.load(f)
            
            facts = ltm_data.get('facts', [])
            print(f"   ✅ Loaded {len(facts)} LTM facts (not integrated yet)")
        except FileNotFoundError:
            print(f"   ⚠️  LTM data not found: {ltm_file}")
    
    def test_semantic_queries(self):
        """Test semantic search with various queries."""
        print("\n" + "="*80)
        print("🔍 SEMANTIC SEARCH TESTS")
        print("="*80)
        
        # Test queries with expected topics
        test_queries = [
            {
                "query": "Tôi làm nghề gì?",
                "expected_topics": ["AI Engineer", "đầu bếp", "Sasukekeke"],
                "description": "Identity query - should retrieve personal info"
            },
            {
                "query": "Hướng dẫn nấu gà chiên Nhật Bản",
                "expected_topics": ["gà chiên", "Karaage", "ướp", "chiên"],
                "description": "Cooking query - should retrieve cooking knowledge"
            },
            {
                "query": "Valorant tips and tricks",
                "expected_topics": ["Valorant", "Jett", "Reyna", "aim"],
                "description": "Gaming query - should retrieve gaming knowledge"
            },
            {
                "query": "OpenAI API pricing and usage",
                "expected_topics": ["OpenAI", "API", "token", "pricing"],
                "description": "Tech query - should retrieve tech knowledge"
            },
            {
                "query": "Du lịch Tokyo mùa hoa anh đào",
                "expected_topics": ["Tokyo", "sakura", "hoa anh đào", "Ueno"],
                "description": "Travel query - should retrieve travel knowledge"
            },
            {
                "query": "Transformer architecture in deep learning",
                "expected_topics": ["Transformer", "attention", "encoder", "decoder"],
                "description": "Education query - should retrieve ML knowledge"
            },
        ]
        
        results = []
        
        for i, test in enumerate(test_queries, 1):
            query = test['query']
            expected = test['expected_topics']
            desc = test['description']
            
            print(f"\n{'='*80}")
            print(f"📝 Query {i}/{len(test_queries)}: {query}")
            print(f"💡 Expected: {desc}")
            print(f"{'='*80}")
            
            # Test with semantic search
            start_time = time.time()
            context = self.orchestrator.get_context(
                query=query,
                n_recent=5,
                n_chunks=3,
                use_embedding_search=True  # Enable semantic search
            )
            elapsed = time.time() - start_time
            
            # Analyze results
            aggregated = context['aggregated']
            compressed = context['compressed']
            
            # Calculate relevance
            context_text = json.dumps(aggregated, ensure_ascii=False).lower()
            found_topics = sum(1 for topic in expected if topic.lower() in context_text)
            relevance_score = (found_topics / len(expected)) * 100 if expected else 0
            
            # Display results
            print(f"\n📊 Results:")
            print(f"   STM hits: {aggregated.get('stm_count', 0)}")
            print(f"   MTM hits: {aggregated.get('mtm_count', 0)}")
            print(f"   Compressed: {len(compressed.get('compressed_items', []))} items")
            print(f"   Relevance: {relevance_score:.1f}%")
            print(f"   Time: {elapsed*1000:.2f}ms")
            
            # Show top items
            items = aggregated.get('items', [])
            if items:
                print(f"\n   🔝 Top Results:")
                for idx, item in enumerate(items[:3], 1):
                    content = item.get('content', '') or item.get('summary', '')
                    score = item.get('final_score', 0)
                    source = item.get('source', 'unknown')
                    print(f"      {idx}. [{source}] {content[:80]}... (score: {score:.3f})")
            
            # Store result
            result = {
                'query': query,
                'description': desc,
                'stm_count': aggregated.get('stm_count', 0),
                'mtm_count': aggregated.get('mtm_count', 0),
                'relevance_score': relevance_score,
                'time_ms': elapsed * 1000,
                'found_topics': found_topics,
                'total_topics': len(expected),
            }
            results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]):
        """Generate test report."""
        print("\n" + "="*80)
        print("📊 SEMANTIC SEARCH TEST REPORT")
        print("="*80)
        
        # Calculate averages
        avg_relevance = sum(r['relevance_score'] for r in results) / len(results)
        avg_stm = sum(r['stm_count'] for r in results) / len(results)
        avg_mtm = sum(r['mtm_count'] for r in results) / len(results)
        avg_time = sum(r['time_ms'] for r in results) / len(results)
        
        print(f"\n✨ Overall Performance:")
        print(f"   Average Relevance: {avg_relevance:.1f}%")
        print(f"   Average STM hits: {avg_stm:.1f}")
        print(f"   Average MTM hits: {avg_mtm:.1f}")
        print(f"   Average time: {avg_time:.2f}ms")
        
        # Grade
        if avg_relevance >= 80:
            grade = "🟢 EXCELLENT"
        elif avg_relevance >= 60:
            grade = "🟡 GOOD"
        elif avg_relevance >= 40:
            grade = "🟠 FAIR"
        else:
            grade = "🔴 NEEDS IMPROVEMENT"
        
        print(f"\n🎖️  Grade: {grade}")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        for i, r in enumerate(results, 1):
            print(f"\n   {i}. {r['query']}")
            print(f"      Relevance: {r['relevance_score']:.1f}% ({r['found_topics']}/{r['total_topics']} topics)")
            print(f"      Context: {r['stm_count']} STM + {r['mtm_count']} MTM")
            print(f"      Time: {r['time_ms']:.2f}ms")
        
        # Save report
        report = {
            'test_date': datetime.now().isoformat(),
            'embedding_model': 'real' if use_real_embeddings else 'mock',
            'summary': {
                'avg_relevance': avg_relevance,
                'avg_stm_hits': avg_stm,
                'avg_mtm_hits': avg_mtm,
                'avg_time_ms': avg_time,
                'grade': grade,
            },
            'results': results
        }
        
        with open('semantic_search_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Report saved to: semantic_search_report.json")
        
        return report


def main():
    """Run semantic search tests."""
    print("="*80)
    print("🚀 SEMANTIC SEARCH TEST SUITE")
    print("="*80)
    
    # Initialize
    test = SemanticSearchTest()
    
    # Load data
    test.load_test_data()
    
    # Run tests
    results = test.test_semantic_queries()
    
    # Generate report
    test.generate_report(results)
    
    print("\n" + "="*80)
    print("🎉 SEMANTIC SEARCH TESTS COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()
