#!/usr/bin/env python3
"""
Test semantic search with CODE ANALYSIS domain data.

Tests queries relevant to code analysis:
- Debugging questions
- Commit history searches
- Architecture questions
- API documentation queries
"""

import json
import time
from typing import List, Dict, Any
from core.short_term import ShortTermMemory
from core.mid_term import MidTermMemory
from core.long_term import LongTermMemory


class CodeAnalysisTest:
    """Test suite for code analysis domain."""
    
    def __init__(self):
        self.stm = ShortTermMemory(max_items=10)
        self.mtm = MidTermMemory(max_chunks=20)
        self.ltm = LongTermMemory()
        
        self.test_queries = [
            {
                "query": "Hàm computeMetrics bị lỗi chia cho 0",
                "expected_topics": ["bug", "computeMetrics", "divide-by-zero", "fix"],
                "description": "Debugging query - should find bug info and fixes"
            },
            {
                "query": "Commit nào fix lỗi analytics",
                "expected_topics": ["commit", "abc123", "fix", "analytics"],
                "description": "Commit history - should find relevant commits"
            },
            {
                "query": "Module Analytics làm gì",
                "expected_topics": ["analytics", "module", "architecture", "functions"],
                "description": "Architecture - should find module documentation"
            },
            {
                "query": "API endpoint metrics hoạt động thế nào",
                "expected_topics": ["api", "metrics", "endpoint", "REST"],
                "description": "API docs - should find endpoint documentation"
            },
            {
                "query": "Hàm calculateAverage được dùng ở đâu",
                "expected_topics": ["calculateAverage", "function", "computeMetrics", "dependencies"],
                "description": "Code search - should find function usage"
            },
            {
                "query": "John Doe là ai",
                "expected_topics": ["John Doe", "contributor", "team", "analytics"],
                "description": "Team info - should find contributor information"
            },
        ]
    
    def load_test_data(self):
        """Load generated code analysis data."""
        print("\n📂 Loading test data...")
        
        # Load STM
        try:
            with open('data/stm.json', 'r', encoding='utf-8') as f:
                stm_data = json.load(f)
            for msg in stm_data:
                self.stm.add(
                    msg['role'],
                    msg['content'],
                    embedding=msg['metadata'].get('embedding'),
                    **{k: v for k, v in msg['metadata'].items() if k != 'embedding'}
                )
            print(f"   ✅ Loaded {len(stm_data)} STM messages")
        except FileNotFoundError:
            print("   ⚠️  STM data not found. Run generate_data.py first")
            return False
        
        # Load MTM
        try:
            with open('data/mtm.json', 'r', encoding='utf-8') as f:
                mtm_data = json.load(f)
            for chunk in mtm_data:
                self.mtm.add_chunk(
                    chunk['summary'],
                    metadata=chunk['metadata'],
                    embedding=chunk.get('embedding')
                )
            print(f"   ✅ Loaded {len(mtm_data)} MTM chunks")
        except FileNotFoundError:
            print("   ⚠️  MTM data not found")
            return False
        
        # Load LTM
        try:
            with open('data/ltm.json', 'r', encoding='utf-8') as f:
                ltm_data = json.load(f)
            # Add to LTM (if method exists)
            for fact in ltm_data:
                # LongTermMemory doesn't have add method yet, so we'll store for manual check
                pass
            print(f"   ✅ Loaded {len(ltm_data)} LTM facts")
            self.ltm_facts = ltm_data  # Store for later use
        except FileNotFoundError:
            print("   ⚠️  LTM data not found")
            self.ltm_facts = []
        
        return True
    
    def test_query(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single query."""
        query = query_info["query"]
        expected_topics = query_info["expected_topics"]
        
        # Generate embedding for query
        try:
            from utils.real_embedding import RealEmbeddingGenerator
            embedder = RealEmbeddingGenerator()
            query_embedding = embedder.generate(query)
        except:
            # Mock embedding
            import hashlib
            import random
            hash_val = int(hashlib.md5(query.encode()).hexdigest(), 16)
            random.seed(hash_val)
            query_embedding = [random.random() for _ in range(384)]
        
        # Search STM
        start_time = time.time()
        stm_results = self.stm.search_by_embedding(query_embedding, top_k=5)
        stm_time = time.time() - start_time
        
        # Search MTM
        start_time = time.time()
        mtm_results = self.mtm.search_by_embedding(query_embedding, top_k=3)
        mtm_time = time.time() - start_time
        
        # Calculate relevance
        found_topics = set()
        
        # Check STM results
        for result in stm_results:
            msg = result['message']
            content_lower = msg['content'].lower()
            for topic in expected_topics:
                if topic.lower() in content_lower:
                    found_topics.add(topic)
        
        # Check MTM results
        for result in mtm_results:
            chunk = result['chunk']
            summary_lower = chunk['summary'].lower()
            keywords = chunk.get('metadata', {}).get('keywords', [])
            keywords_lower = [k.lower() for k in keywords]
            
            for topic in expected_topics:
                topic_lower = topic.lower()
                if topic_lower in summary_lower or topic_lower in keywords_lower:
                    found_topics.add(topic)
        
        # Calculate score
        relevance_score = (len(found_topics) / len(expected_topics)) * 100 if expected_topics else 0
        
        return {
            "query": query,
            "description": query_info["description"],
            "stm_count": len(stm_results),
            "mtm_count": len(mtm_results),
            "stm_time_ms": stm_time * 1000,
            "mtm_time_ms": mtm_time * 1000,
            "expected_topics": len(expected_topics),
            "found_topics": len(found_topics),
            "matched_topics": list(found_topics),
            "relevance_score": relevance_score,
            "top_stm": [r['message']['content'][:100] + "..." for r in stm_results[:2]],
            "top_mtm": [r['chunk']['metadata'].get('topic', 'N/A') for r in mtm_results[:2]],
        }
    
    def run_tests(self):
        """Run all test queries."""
        print("\n🔍 Running semantic search tests...")
        print("="*80)
        
        results = []
        total_relevance = 0
        total_time = 0
        
        for idx, query_info in enumerate(self.test_queries, 1):
            print(f"\n[{idx}/{len(self.test_queries)}] {query_info['query']}")
            result = self.test_query(query_info)
            results.append(result)
            
            total_relevance += result['relevance_score']
            total_time += result['stm_time_ms'] + result['mtm_time_ms']
            
            # Print result
            print(f"   📊 Relevance: {result['relevance_score']:.1f}%")
            print(f"   ✅ Found topics: {result['matched_topics']}")
            print(f"   📈 STM: {result['stm_count']} results ({result['stm_time_ms']:.2f}ms)")
            print(f"   📈 MTM: {result['mtm_count']} results ({result['mtm_time_ms']:.2f}ms)")
            if result['top_mtm']:
                print(f"   🎯 Top MTM topics: {', '.join(result['top_mtm'])}")
        
        # Calculate averages
        avg_relevance = total_relevance / len(results)
        avg_time = total_time / len(results)
        
        # Grade
        if avg_relevance >= 70:
            grade = "🟢 EXCELLENT"
        elif avg_relevance >= 50:
            grade = "🟡 GOOD"
        elif avg_relevance >= 30:
            grade = "🟠 FAIR"
        else:
            grade = "🔴 NEEDS IMPROVEMENT"
        
        # Summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        print(f"Total Queries:      {len(results)}")
        print(f"Avg Relevance:      {avg_relevance:.1f}%")
        print(f"Avg Time:           {avg_time:.2f}ms")
        print(f"Grade:              {grade}")
        print("="*80)
        
        # Save report
        report = {
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "domain": "code_analysis",
            "summary": {
                "total_queries": len(results),
                "avg_relevance": avg_relevance,
                "avg_time_ms": avg_time,
                "grade": grade
            },
            "results": results
        }
        
        with open('code_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Report saved to: code_analysis_report.json")
        
        return report


def main():
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "CODE ANALYSIS SEMANTIC SEARCH TEST" + " "*24 + "║")
    print("╚" + "="*78 + "╝")
    
    test = CodeAnalysisTest()
    
    # Load data
    if not test.load_test_data():
        print("\n❌ Failed to load test data")
        print("💡 Run: python generate_code_analysis_data.py")
        return
    
    # Run tests
    test.run_tests()
    
    print("\n✅ Testing complete!")


if __name__ == "__main__":
    main()
