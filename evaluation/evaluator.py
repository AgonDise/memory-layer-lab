"""
Evaluation framework for Memory Layer Lab.

Evaluates:
- Context retrieval quality
- Compression effectiveness
- Memory recall accuracy
- Response quality
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from datetime import datetime
import json


class MemoryEvaluator:
    """Evaluate memory layer performance."""
    
    def __init__(self):
        """Initialize evaluator."""
        self.evaluation_results = []
    
    def evaluate_context_retrieval(self,
                                   query: str,
                                   retrieved_items: List[Dict],
                                   ground_truth_items: List[Dict]) -> Dict[str, float]:
        """
        Evaluate context retrieval quality.
        
        Metrics:
        - Precision: Relevant retrieved / Total retrieved
        - Recall: Relevant retrieved / Total relevant
        - F1 Score: Harmonic mean of precision and recall
        
        Args:
            query: User query
            retrieved_items: Items retrieved by system
            ground_truth_items: Known relevant items
            
        Returns:
            Metrics dict
        """
        if not retrieved_items:
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
        
        # Calculate overlap
        retrieved_ids = {item.get('id', str(i)) for i, item in enumerate(retrieved_items)}
        ground_truth_ids = {item.get('id', str(i)) for i, item in enumerate(ground_truth_items)}
        
        relevant_retrieved = retrieved_ids.intersection(ground_truth_ids)
        
        precision = len(relevant_retrieved) / len(retrieved_ids) if retrieved_ids else 0
        recall = len(relevant_retrieved) / len(ground_truth_ids) if ground_truth_ids else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'retrieved_count': len(retrieved_ids),
            'relevant_count': len(ground_truth_ids),
            'overlap_count': len(relevant_retrieved)
        }
    
    def evaluate_compression(self,
                            original_items: List[Dict],
                            compressed_items: List[Dict],
                            token_budget: int) -> Dict[str, Any]:
        """
        Evaluate context compression quality.
        
        Metrics:
        - Compression ratio
        - Information retention (estimated)
        - Token efficiency
        
        Args:
            original_items: Original context items
            compressed_items: Compressed items
            token_budget: Target token budget
            
        Returns:
            Metrics dict
        """
        original_count = len(original_items)
        compressed_count = len(compressed_items)
        
        # Estimate tokens (rough: 1 word ≈ 1.3 tokens)
        original_text = " ".join([str(item.get('content', item.get('summary', ''))) 
                                 for item in original_items])
        compressed_text = " ".join([str(item.get('content', item.get('summary', ''))) 
                                   for item in compressed_items])
        
        original_tokens = len(original_text.split()) * 1.3
        compressed_tokens = len(compressed_text.split()) * 1.3
        
        compression_ratio = compressed_count / original_count if original_count > 0 else 0
        token_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 0
        within_budget = compressed_tokens <= token_budget
        
        # Estimate information retention (overlap of important words)
        original_words = set(original_text.lower().split())
        compressed_words = set(compressed_text.lower().split())
        word_retention = len(compressed_words.intersection(original_words)) / len(original_words) if original_words else 0
        
        return {
            'compression_ratio': compression_ratio,
            'token_reduction': token_ratio,
            'original_tokens': int(original_tokens),
            'compressed_tokens': int(compressed_tokens),
            'within_budget': within_budget,
            'word_retention': word_retention,
            'efficiency_score': (1 - token_ratio) * word_retention  # Lower tokens, higher retention = better
        }
    
    def evaluate_memory_recall(self,
                               conversation_history: List[Dict],
                               test_queries: List[Dict]) -> Dict[str, float]:
        """
        Evaluate how well memory recalls past information.
        
        Args:
            conversation_history: Past conversations
            test_queries: Queries to test recall (with expected answers)
            
        Returns:
            Recall metrics
        """
        results = []
        
        for test in test_queries:
            query = test['query']
            expected_keywords = set(test.get('expected_keywords', []))
            
            # Simple keyword matching in history
            found_keywords = set()
            for conv in conversation_history:
                content = conv.get('content', '').lower()
                for keyword in expected_keywords:
                    if keyword.lower() in content:
                        found_keywords.add(keyword)
            
            recall = len(found_keywords) / len(expected_keywords) if expected_keywords else 0
            results.append(recall)
        
        return {
            'avg_recall': np.mean(results) if results else 0,
            'min_recall': np.min(results) if results else 0,
            'max_recall': np.max(results) if results else 0,
            'test_count': len(results)
        }
    
    def evaluate_response_quality(self,
                                  query: str,
                                  response: str,
                                  context: str,
                                  ground_truth: str = None) -> Dict[str, Any]:
        """
        Evaluate response quality.
        
        Metrics:
        - Context utilization
        - Response length
        - Keyword coverage
        - (Optional) Similarity to ground truth
        
        Args:
            query: User query
            response: Generated response
            context: Context used
            ground_truth: Expected response (optional)
            
        Returns:
            Quality metrics
        """
        # Context utilization: how many context words appear in response
        context_words = set(context.lower().split())
        response_words = set(response.lower().split())
        
        if context_words:
            context_utilization = len(context_words.intersection(response_words)) / len(context_words)
        else:
            context_utilization = 0
        
        # Query relevance: query keywords in response
        query_words = set(query.lower().split())
        query_coverage = len(query_words.intersection(response_words)) / len(query_words) if query_words else 0
        
        metrics = {
            'response_length': len(response),
            'word_count': len(response.split()),
            'context_utilization': context_utilization,
            'query_coverage': query_coverage,
        }
        
        # Optional: similarity to ground truth
        if ground_truth:
            gt_words = set(ground_truth.lower().split())
            overlap = response_words.intersection(gt_words)
            similarity = len(overlap) / len(gt_words.union(response_words)) if gt_words.union(response_words) else 0
            metrics['ground_truth_similarity'] = similarity
        
        return metrics
    
    def run_evaluation_suite(self,
                            test_cases: List[Dict]) -> Dict[str, Any]:
        """
        Run complete evaluation suite.
        
        Args:
            test_cases: List of test cases with queries and expected results
            
        Returns:
            Comprehensive evaluation results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(test_cases),
            'context_retrieval': [],
            'compression': [],
            'response_quality': [],
            'summary': {}
        }
        
        for test_case in test_cases:
            # Evaluate each aspect if data available
            if 'retrieved_items' in test_case and 'ground_truth_items' in test_case:
                retrieval_metrics = self.evaluate_context_retrieval(
                    test_case['query'],
                    test_case['retrieved_items'],
                    test_case['ground_truth_items']
                )
                results['context_retrieval'].append(retrieval_metrics)
            
            if 'original_items' in test_case and 'compressed_items' in test_case:
                compression_metrics = self.evaluate_compression(
                    test_case['original_items'],
                    test_case['compressed_items'],
                    test_case.get('token_budget', 2000)
                )
                results['compression'].append(compression_metrics)
            
            if 'response' in test_case:
                quality_metrics = self.evaluate_response_quality(
                    test_case['query'],
                    test_case['response'],
                    test_case.get('context', ''),
                    test_case.get('ground_truth_response')
                )
                results['response_quality'].append(quality_metrics)
        
        # Calculate summary statistics
        if results['context_retrieval']:
            results['summary']['avg_precision'] = np.mean([r['precision'] for r in results['context_retrieval']])
            results['summary']['avg_recall'] = np.mean([r['recall'] for r in results['context_retrieval']])
            results['summary']['avg_f1'] = np.mean([r['f1'] for r in results['context_retrieval']])
        
        if results['compression']:
            results['summary']['avg_compression_ratio'] = np.mean([r['compression_ratio'] for r in results['compression']])
            results['summary']['avg_efficiency'] = np.mean([r['efficiency_score'] for r in results['compression']])
        
        if results['response_quality']:
            results['summary']['avg_context_utilization'] = np.mean([r['context_utilization'] for r in results['response_quality']])
            results['summary']['avg_query_coverage'] = np.mean([r['query_coverage'] for r in results['response_quality']])
        
        self.evaluation_results.append(results)
        return results
    
    def save_results(self, filepath: str):
        """Save evaluation results to file."""
        with open(filepath, 'w') as f:
            json.dump(self.evaluation_results, f, indent=2)
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable evaluation report."""
        report = []
        report.append("=" * 70)
        report.append("EVALUATION REPORT")
        report.append("=" * 70)
        report.append(f"Timestamp: {results['timestamp']}")
        report.append(f"Total Tests: {results['total_tests']}")
        report.append("")
        
        if results['summary']:
            report.append("SUMMARY METRICS")
            report.append("-" * 70)
            for key, value in results['summary'].items():
                report.append(f"  {key}: {value:.4f}")
            report.append("")
        
        if results['context_retrieval']:
            report.append("CONTEXT RETRIEVAL")
            report.append("-" * 70)
            for i, metrics in enumerate(results['context_retrieval'], 1):
                report.append(f"  Test {i}:")
                report.append(f"    Precision: {metrics['precision']:.4f}")
                report.append(f"    Recall: {metrics['recall']:.4f}")
                report.append(f"    F1: {metrics['f1']:.4f}")
            report.append("")
        
        if results['compression']:
            report.append("COMPRESSION QUALITY")
            report.append("-" * 70)
            for i, metrics in enumerate(results['compression'], 1):
                report.append(f"  Test {i}:")
                report.append(f"    Compression Ratio: {metrics['compression_ratio']:.2%}")
                report.append(f"    Token Reduction: {metrics['token_reduction']:.2%}")
                report.append(f"    Efficiency Score: {metrics['efficiency_score']:.4f}")
            report.append("")
        
        report.append("=" * 70)
        return "\n".join(report)


# Example usage
if __name__ == '__main__':
    evaluator = MemoryEvaluator()
    
    # Example test case
    test_cases = [
        {
            'query': 'Tell me about login function',
            'retrieved_items': [
                {'id': '1', 'content': 'login_user handles auth'},
                {'id': '2', 'content': 'creates JWT token'},
            ],
            'ground_truth_items': [
                {'id': '1', 'content': 'login_user handles auth'},
                {'id': '3', 'content': 'validates credentials'},
            ],
            'original_items': [
                {'content': 'Long text about login...'},
                {'content': 'Another long text...'},
                {'content': 'More context...'},
            ],
            'compressed_items': [
                {'content': 'login_user handles auth'},
                {'content': 'creates JWT token'},
            ],
            'token_budget': 2000,
            'context': 'login_user handles authentication',
            'response': 'The login_user function handles user authentication and creates JWT tokens',
        }
    ]
    
    results = evaluator.run_evaluation_suite(test_cases)
    print(evaluator.generate_report(results))
