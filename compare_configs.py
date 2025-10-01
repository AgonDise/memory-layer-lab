#!/usr/bin/env python3
"""
Config Comparison Tool

Compare multiple configurations side-by-side.
Useful for A/B testing compression parameters.
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Any
from evaluate_memory import MemoryEvaluator


class ConfigComparator:
    """Compare multiple configurations."""
    
    def __init__(self, configs: List[Dict[str, Any]]):
        self.configs = configs
    
    def compare(self) -> Dict[str, Any]:
        """Run comparison across all configs."""
        print("╔" + "="*78 + "╗")
        print("║" + " "*25 + "CONFIG COMPARISON" + " "*35 + "║")
        print("╚" + "="*78 + "╝")
        
        results = []
        
        for idx, config in enumerate(self.configs, 1):
            print(f"\n{'='*80}")
            print(f"Config {idx}: {config}")
            print('='*80)
            
            evaluator = MemoryEvaluator(config)
            result = evaluator.run_full_evaluation()
            
            results.append({
                'config_id': idx,
                'config': config,
                'summary': result['summary'],
                'compression': result['compression']
            })
        
        # Comparison table
        print("\n" + "="*80)
        print("📊 COMPARISON TABLE")
        print("="*80)
        
        print(f"\n{'Metric':<25} ", end='')
        for i in range(len(self.configs)):
            print(f"Config {i+1:<10}", end=' ')
        print()
        print("-" * 80)
        
        metrics = [
            ('F1 Score', 'avg_f1_score', '.3f'),
            ('Precision', 'avg_precision', '.3f'),
            ('Recall', 'avg_recall', '.3f'),
            ('Source Coverage', 'avg_source_coverage', '.3f'),
            ('Pass Rate', 'pass_rate', '.2%'),
            ('Avg Latency (ms)', 'avg_latency_ms', '.2f'),
            ('Compression Ratio', 'compression_ratio', '.3f'),
            ('Token Savings %', 'token_savings_percent', '.1f'),
        ]
        
        for metric_name, metric_key, fmt in metrics:
            print(f"{metric_name:<25} ", end='')
            for result in results:
                if metric_key in result['summary']:
                    value = result['summary'][metric_key]
                elif metric_key in result['compression']:
                    value = result['compression'][metric_key]
                else:
                    value = 0
                
                print(f"{value:{fmt}:<12}", end=' ')
            print()
        
        print("-" * 80)
        
        # Recommendation
        print("\n💡 RECOMMENDATION")
        print("="*80)
        
        best_f1_idx = max(range(len(results)), key=lambda i: results[i]['summary']['avg_f1_score'])
        best_latency_idx = min(range(len(results)), key=lambda i: results[i]['summary']['avg_latency_ms'])
        best_compression_idx = max(range(len(results)), key=lambda i: results[i]['compression']['savings_percent'])
        
        print(f"🏆 Best F1 Score: Config {best_f1_idx + 1}")
        print(f"⚡ Fastest: Config {best_latency_idx + 1}")
        print(f"💾 Best Compression: Config {best_compression_idx + 1}")
        
        # Overall winner (balanced)
        for i, result in enumerate(results):
            s = result['summary']
            # Score = F1 * 0.5 + (1 - latency_norm) * 0.3 + compression * 0.2
            f1_norm = s['avg_f1_score']
            latency_norm = s['avg_latency_ms'] / max(r['summary']['avg_latency_ms'] for r in results)
            comp_norm = result['compression']['compression_ratio']
            
            result['balanced_score'] = f1_norm * 0.5 + (1 - latency_norm) * 0.3 + comp_norm * 0.2
        
        best_overall_idx = max(range(len(results)), key=lambda i: results[i]['balanced_score'])
        
        print(f"\n🎯 Best Overall (balanced): Config {best_overall_idx + 1}")
        print(f"   Config: {results[best_overall_idx]['config']}")
        print(f"   F1: {results[best_overall_idx]['summary']['avg_f1_score']:.3f}")
        print(f"   Latency: {results[best_overall_idx]['summary']['avg_latency_ms']:.2f}ms")
        print(f"   Compression: {results[best_overall_idx]['compression']['savings_percent']:.1f}%")
        print("="*80)
        
        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'configs': self.configs,
            'results': results,
            'recommendations': {
                'best_f1': best_f1_idx + 1,
                'best_latency': best_latency_idx + 1,
                'best_compression': best_compression_idx + 1,
                'best_overall': best_overall_idx + 1,
                'best_config': results[best_overall_idx]['config']
            }
        }
        
        report_file = f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Report saved: {report_file}")
        
        return report


# Preset configurations for common scenarios
PRESET_CONFIGS = {
    'minimal': {
        'name': 'Minimal (Low Memory)',
        'config': {'stm_max_items': 5, 'mtm_max_chunks': 10, 'top_k': 2}
    },
    'balanced': {
        'name': 'Balanced',
        'config': {'stm_max_items': 10, 'mtm_max_chunks': 20, 'top_k': 3}
    },
    'quality': {
        'name': 'Quality (High Recall)',
        'config': {'stm_max_items': 15, 'mtm_max_chunks': 30, 'top_k': 5}
    },
    'performance': {
        'name': 'Performance (Low Latency)',
        'config': {'stm_max_items': 5, 'mtm_max_chunks': 15, 'top_k': 2}
    },
}


def main():
    """Compare configurations."""
    if len(sys.argv) > 1 and sys.argv[1] == 'preset':
        # Compare preset configs
        configs = [PRESET_CONFIGS[k]['config'] for k in ['minimal', 'balanced', 'quality', 'performance']]
        print("\n🔧 Comparing preset configurations:")
        for k, v in PRESET_CONFIGS.items():
            print(f"  • {k}: {v['name']}")
    else:
        # Default comparison
        configs = [
            {'stm_max_items': 5, 'mtm_max_chunks': 15, 'top_k': 2},   # Low memory
            {'stm_max_items': 10, 'mtm_max_chunks': 20, 'top_k': 3},  # Balanced
            {'stm_max_items': 15, 'mtm_max_chunks': 30, 'top_k': 5},  # High quality
        ]
    
    comparator = ConfigComparator(configs)
    result = comparator.compare()
    
    print("\n✅ Comparison complete!")
    print("   Review results above to choose best config for your use case.")


if __name__ == "__main__":
    main()
