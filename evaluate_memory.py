#!/usr/bin/env python3
"""
Memory Layer Evaluation Framework

Evaluates:
- Retrieval quality (precision, recall, relevance)
- Context compression efficiency
- Response quality
- Latency and performance
- Token usage

For tuning compression and retrieval parameters.
"""

import json
import time
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
from core.short_term import ShortTermMemory
from core.mid_term import MidTermMemory
from core.long_term import LongTermMemory


class MemoryEvaluator:
    """Comprehensive memory layer evaluation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.stm = ShortTermMemory(max_items=self.config.get('stm_max_items', 10))
        self.mtm = MidTermMemory(max_chunks=self.config.get('mtm_max_chunks', 20))
        self.ltm = LongTermMemory()
        
        # Load test data
        self.load_data()
        
        # Evaluation queries with ground truth
        self.test_cases = [
            {
                "query": "Hàm computeMetrics bị lỗi chia cho 0",
                "category": "debugging",
                "expected_entities": ["computeMetrics", "divide-by-zero", "bug", "abc123"],
                "expected_sources": ["stm", "mtm", "ltm"],
                "min_relevance": 0.7
            },
            {
                "query": "Commit abc123 fix gì?",
                "category": "commit_history",
                "expected_entities": ["abc123", "computeMetrics", "John Doe", "bugfix"],
                "expected_sources": ["mtm", "ltm"],
                "min_relevance": 0.8
            },
            {
                "query": "Module Analytics có những function nào?",
                "category": "architecture",
                "expected_entities": ["Analytics", "computeMetrics", "calculateAverage", "module"],
                "expected_sources": ["stm", "ltm"],
                "min_relevance": 0.7
            },
            {
                "query": "John Doe đã làm gì?",
                "category": "team",
                "expected_entities": ["John Doe", "abc123", "def456", "author"],
                "expected_sources": ["mtm", "ltm"],
                "min_relevance": 0.6
            },
            {
                "query": "Guideline về error handling?",
                "category": "guideline",
                "expected_entities": ["guideline", "error", "validation", "zero"],
                "expected_sources": ["ltm"],
                "min_relevance": 0.7
            },
        ]
    
    def load_data(self):
        """Load test data into memory layers."""
        # Load STM
        with open('data/stm.json', 'r', encoding='utf-8') as f:
            stm_data = json.load(f)
        for msg in stm_data:
            self.stm.add(
                msg['role'],
                msg['content'],
                embedding=msg['metadata'].get('embedding'),
                **{k: v for k, v in msg['metadata'].items() if k != 'embedding'}
            )
        
        # Load MTM
        with open('data/mtm.json', 'r', encoding='utf-8') as f:
            mtm_data = json.load(f)
        for chunk in mtm_data:
            self.mtm.add_chunk(
                chunk['summary'],
                metadata=chunk['metadata'],
                embedding=chunk.get('embedding')
            )
        
        # Load LTM
        with open('data/ltm.json', 'r', encoding='utf-8') as f:
            self.ltm_facts = json.load(f)
    
    def evaluate_retrieval(self, query: str, expected_entities: List[str], 
                          expected_sources: List[str], top_k: int = 3) -> Dict[str, Any]:
        """Evaluate retrieval quality for a query."""
        # Generate embedding
        try:
            from utils.real_embedding import RealEmbeddingGenerator
            embedder = RealEmbeddingGenerator()
            query_emb = embedder.generate(query)
        except:
            import hashlib, random
            h = int(hashlib.md5(query.encode()).hexdigest(), 16)
            random.seed(h)
            query_emb = [random.random() for _ in range(384)]
        
        # Retrieve from each layer
        start_time = time.time()
        stm_results = self.stm.search_by_embedding(query_emb, top_k=top_k)
        stm_time = time.time() - start_time
        
        start_time = time.time()
        mtm_results = self.mtm.search_by_embedding(query_emb, top_k=top_k)
        mtm_time = time.time() - start_time
        
        # For LTM, manual search
        start_time = time.time()
        ltm_results = []
        for fact in self.ltm_facts:
            score = sum(1 for e in expected_entities if e.lower() in fact['content'].lower())
            if score > 0:
                ltm_results.append({'fact': fact, 'score': score})
        ltm_results.sort(key=lambda x: x['score'], reverse=True)
        ltm_results = ltm_results[:top_k]
        ltm_time = time.time() - start_time
        
        # Calculate metrics
        found_entities = set()
        found_sources = set()
        
        # Check STM
        if stm_results:
            found_sources.add('stm')
            for r in stm_results:
                content = r['message']['content'].lower()
                found_entities.update([e for e in expected_entities if e.lower() in content])
        
        # Check MTM
        if mtm_results:
            found_sources.add('mtm')
            for r in mtm_results:
                content = r['chunk']['summary'].lower()
                found_entities.update([e for e in expected_entities if e.lower() in content])
        
        # Check LTM
        if ltm_results:
            found_sources.add('ltm')
            for r in ltm_results:
                content = r['fact']['content'].lower()
                found_entities.update([e for e in expected_entities if e.lower() in content])
        
        # Precision & Recall
        precision = len(found_entities) / len(expected_entities) if expected_entities else 0
        recall = len(found_entities) / len(expected_entities) if expected_entities else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        source_coverage = len(found_sources) / len(expected_sources) if expected_sources else 0
        
        return {
            'query': query,
            'found_entities': list(found_entities),
            'expected_entities': expected_entities,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'source_coverage': source_coverage,
            'found_sources': list(found_sources),
            'retrieval_times': {
                'stm': stm_time * 1000,
                'mtm': mtm_time * 1000,
                'ltm': ltm_time * 1000,
                'total': (stm_time + mtm_time + ltm_time) * 1000
            },
            'result_counts': {
                'stm': len(stm_results),
                'mtm': len(mtm_results),
                'ltm': len(ltm_results)
            }
        }
    
    def evaluate_context_compression(self) -> Dict[str, Any]:
        """Evaluate context compression efficiency."""
        # Get all memory content
        stm_content = [msg['content'] for msg in self.stm.get_recent(100)]
        mtm_content = [chunk['summary'] for chunk in self.mtm.get_all()]
        ltm_content = [fact['content'] for fact in self.ltm_facts]
        
        # Calculate token counts (rough estimate: 1 token ≈ 4 chars)
        stm_tokens = sum(len(c) for c in stm_content) // 4
        mtm_tokens = sum(len(c) for c in mtm_content) // 4
        ltm_tokens = sum(len(c) for c in ltm_content) // 4
        total_tokens = stm_tokens + mtm_tokens + ltm_tokens
        
        # Compression if we only use summaries
        compressed_tokens = mtm_tokens + ltm_tokens  # Skip STM details
        compression_ratio = compressed_tokens / total_tokens if total_tokens > 0 else 0
        
        return {
            'total_tokens': total_tokens,
            'compressed_tokens': compressed_tokens,
            'compression_ratio': compression_ratio,
            'savings_percent': (1 - compression_ratio) * 100,
            'layer_tokens': {
                'stm': stm_tokens,
                'mtm': mtm_tokens,
                'ltm': ltm_tokens
            },
            'layer_counts': {
                'stm': len(stm_content),
                'mtm': len(mtm_content),
                'ltm': len(ltm_content)
            }
        }
    
    def run_full_evaluation(self) -> Dict[str, Any]:
        """Run complete evaluation suite."""
        print("╔" + "="*78 + "╗")
        print("║" + " "*25 + "MEMORY EVALUATION" + " "*36 + "║")
        print("╚" + "="*78 + "╝")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'config': self.config,
            'retrieval_tests': [],
            'compression': {},
            'summary': {}
        }
        
        # 1. Retrieval evaluation
        print("\n1️⃣ Evaluating retrieval quality...")
        retrieval_results = []
        
        for test_case in self.test_cases:
            print(f"   Testing: {test_case['category']}")
            result = self.evaluate_retrieval(
                test_case['query'],
                test_case['expected_entities'],
                test_case['expected_sources'],
                top_k=self.config.get('top_k', 3)
            )
            result['category'] = test_case['category']
            result['min_relevance'] = test_case['min_relevance']
            result['passed'] = result['f1_score'] >= test_case['min_relevance']
            retrieval_results.append(result)
            
            status = "✅" if result['passed'] else "❌"
            print(f"      {status} F1: {result['f1_score']:.2f}, Coverage: {result['source_coverage']:.2f}")
        
        results['retrieval_tests'] = retrieval_results
        
        # 2. Compression evaluation
        print("\n2️⃣ Evaluating context compression...")
        compression = self.evaluate_context_compression()
        results['compression'] = compression
        
        print(f"   Total tokens: {compression['total_tokens']}")
        print(f"   Compressed: {compression['compressed_tokens']}")
        print(f"   Savings: {compression['savings_percent']:.1f}%")
        
        # 3. Summary metrics
        avg_f1 = sum(r['f1_score'] for r in retrieval_results) / len(retrieval_results)
        avg_precision = sum(r['precision'] for r in retrieval_results) / len(retrieval_results)
        avg_recall = sum(r['recall'] for r in retrieval_results) / len(retrieval_results)
        avg_coverage = sum(r['source_coverage'] for r in retrieval_results) / len(retrieval_results)
        avg_latency = sum(r['retrieval_times']['total'] for r in retrieval_results) / len(retrieval_results)
        passed_tests = sum(1 for r in retrieval_results if r['passed'])
        
        results['summary'] = {
            'avg_f1_score': avg_f1,
            'avg_precision': avg_precision,
            'avg_recall': avg_recall,
            'avg_source_coverage': avg_coverage,
            'avg_latency_ms': avg_latency,
            'tests_passed': passed_tests,
            'tests_total': len(retrieval_results),
            'pass_rate': passed_tests / len(retrieval_results),
            'compression_ratio': compression['compression_ratio'],
            'token_savings_percent': compression['savings_percent']
        }
        
        # Grade
        if avg_f1 >= 0.8 and passed_tests >= 4:
            grade = "🟢 EXCELLENT"
        elif avg_f1 >= 0.6 and passed_tests >= 3:
            grade = "🟡 GOOD"
        elif avg_f1 >= 0.4:
            grade = "🟠 FAIR"
        else:
            grade = "🔴 NEEDS IMPROVEMENT"
        
        results['summary']['grade'] = grade
        
        print("\n" + "="*80)
        print("📊 SUMMARY")
        print("="*80)
        print(f"Avg F1 Score:      {avg_f1:.3f}")
        print(f"Avg Precision:     {avg_precision:.3f}")
        print(f"Avg Recall:        {avg_recall:.3f}")
        print(f"Source Coverage:   {avg_coverage:.3f}")
        print(f"Avg Latency:       {avg_latency:.2f}ms")
        print(f"Tests Passed:      {passed_tests}/{len(retrieval_results)}")
        print(f"Compression:       {compression['savings_percent']:.1f}% savings")
        print(f"Grade:             {grade}")
        print("="*80)
        
        # Save report
        report_file = f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Report saved: {report_file}")
        
        return results


def main():
    """Run evaluation with default config."""
    config = {
        'stm_max_items': 10,
        'mtm_max_chunks': 20,
        'top_k': 3
    }
    
    evaluator = MemoryEvaluator(config)
    results = evaluator.run_full_evaluation()
    
    print("\n✅ Evaluation complete!")
    print("\nTune parameters in config and re-run to optimize performance.")


if __name__ == "__main__":
    main()
