"""
Metrics collection and monitoring for Memory Layer Lab.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import numpy as np


@dataclass
class QueryMetrics:
    """Metrics for a single query."""
    timestamp: str
    query: str
    intent: str
    
    # Memory metrics
    stm_hits: int
    mtm_hits: int
    ltm_hits: int
    total_retrieved: int
    
    # Compression metrics
    original_items: int
    compressed_items: int
    compression_ratio: float
    
    # Performance metrics
    preprocessing_time: float
    retrieval_time: float
    generation_time: float
    total_time: float
    
    # Quality metrics
    response_length: int
    context_utilization: float
    
    def to_dict(self) -> Dict:
        """Convert to dict."""
        return asdict(self)


class MetricsCollector:
    """Collect and analyze metrics."""
    
    def __init__(self):
        """Initialize collector."""
        self.query_metrics: List[QueryMetrics] = []
        self.session_start = datetime.now()
    
    def record_query(self, metrics: QueryMetrics):
        """Record metrics for a query."""
        self.query_metrics.append(metrics)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.query_metrics:
            return {}
        
        return {
            'session_duration': (datetime.now() - self.session_start).total_seconds(),
            'total_queries': len(self.query_metrics),
            
            # Memory stats
            'avg_stm_hits': np.mean([m.stm_hits for m in self.query_metrics]),
            'avg_mtm_hits': np.mean([m.mtm_hits for m in self.query_metrics]),
            'avg_total_retrieved': np.mean([m.total_retrieved for m in self.query_metrics]),
            
            # Compression stats
            'avg_compression_ratio': np.mean([m.compression_ratio for m in self.query_metrics]),
            'min_compression_ratio': np.min([m.compression_ratio for m in self.query_metrics]),
            'max_compression_ratio': np.max([m.compression_ratio for m in self.query_metrics]),
            
            # Performance stats
            'avg_total_time': np.mean([m.total_time for m in self.query_metrics]),
            'avg_retrieval_time': np.mean([m.retrieval_time for m in self.query_metrics]),
            'avg_generation_time': np.mean([m.generation_time for m in self.query_metrics]),
            
            # Quality stats
            'avg_response_length': np.mean([m.response_length for m in self.query_metrics]),
            'avg_context_utilization': np.mean([m.context_utilization for m in self.query_metrics]),
        }
    
    def get_intent_breakdown(self) -> Dict[str, int]:
        """Get breakdown by intent."""
        intents = {}
        for m in self.query_metrics:
            intents[m.intent] = intents.get(m.intent, 0) + 1
        return intents
    
    def get_performance_trends(self) -> Dict[str, List[float]]:
        """Get performance trends over time."""
        return {
            'timestamps': [m.timestamp for m in self.query_metrics],
            'response_times': [m.total_time for m in self.query_metrics],
            'compression_ratios': [m.compression_ratio for m in self.query_metrics],
            'context_utilization': [m.context_utilization for m in self.query_metrics],
        }
    
    def generate_report(self) -> str:
        """Generate comprehensive metrics report."""
        stats = self.get_summary_stats()
        intents = self.get_intent_breakdown()
        
        report = []
        report.append("=" * 70)
        report.append("METRICS REPORT")
        report.append("=" * 70)
        report.append(f"Session Duration: {stats.get('session_duration', 0):.2f}s")
        report.append(f"Total Queries: {stats.get('total_queries', 0)}")
        report.append("")
        
        report.append("MEMORY PERFORMANCE")
        report.append("-" * 70)
        report.append(f"  Avg STM Hits: {stats.get('avg_stm_hits', 0):.2f}")
        report.append(f"  Avg MTM Hits: {stats.get('avg_mtm_hits', 0):.2f}")
        report.append(f"  Avg Total Retrieved: {stats.get('avg_total_retrieved', 0):.2f}")
        report.append("")
        
        report.append("COMPRESSION EFFECTIVENESS")
        report.append("-" * 70)
        report.append(f"  Avg Compression Ratio: {stats.get('avg_compression_ratio', 0):.2%}")
        report.append(f"  Min: {stats.get('min_compression_ratio', 0):.2%}")
        report.append(f"  Max: {stats.get('max_compression_ratio', 0):.2%}")
        report.append("")
        
        report.append("RESPONSE TIME")
        report.append("-" * 70)
        report.append(f"  Avg Total Time: {stats.get('avg_total_time', 0):.3f}s")
        report.append(f"  Avg Retrieval: {stats.get('avg_retrieval_time', 0):.3f}s")
        report.append(f"  Avg Generation: {stats.get('avg_generation_time', 0):.3f}s")
        report.append("")
        
        report.append("QUALITY METRICS")
        report.append("-" * 70)
        report.append(f"  Avg Response Length: {stats.get('avg_response_length', 0):.0f} chars")
        report.append(f"  Avg Context Utilization: {stats.get('avg_context_utilization', 0):.2%}")
        report.append("")
        
        report.append("INTENT BREAKDOWN")
        report.append("-" * 70)
        for intent, count in sorted(intents.items(), key=lambda x: x[1], reverse=True):
            percentage = count / stats.get('total_queries', 1) * 100
            report.append(f"  {intent}: {count} ({percentage:.1f}%)")
        
        report.append("=" * 70)
        return "\n".join(report)
    
    def save(self, filepath: str):
        """Save metrics to file."""
        data = {
            'session_start': self.session_start.isoformat(),
            'metrics': [m.to_dict() for m in self.query_metrics],
            'summary': self.get_summary_stats(),
            'intents': self.get_intent_breakdown()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load(self, filepath: str):
        """Load metrics from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.session_start = datetime.fromisoformat(data['session_start'])
        self.query_metrics = [
            QueryMetrics(**m) for m in data['metrics']
        ]


# Example usage
if __name__ == '__main__':
    collector = MetricsCollector()
    
    # Record some example metrics
    for i in range(5):
        metrics = QueryMetrics(
            timestamp=datetime.now().isoformat(),
            query=f"test query {i}",
            intent="general",
            stm_hits=3,
            mtm_hits=2,
            ltm_hits=0,
            total_retrieved=5,
            original_items=10,
            compressed_items=5,
            compression_ratio=0.5,
            preprocessing_time=0.1,
            retrieval_time=0.2,
            generation_time=1.0,
            total_time=1.3,
            response_length=150,
            context_utilization=0.7
        )
        collector.record_query(metrics)
    
    print(collector.generate_report())
