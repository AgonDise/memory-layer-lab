#!/usr/bin/env python3
"""
Parameter Tuning Tool for Memory Layer

Auto-tunes:
- STM size (max_items)
- MTM size (max_chunks)
- Retrieval top_k
- Compression thresholds

Finds optimal parameters for your use case.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from evaluate_memory import MemoryEvaluator


class ParameterTuner:
    """Automated parameter tuning."""
    
    def __init__(self):
        self.results = []
    
    def tune_stm_size(self, sizes: List[int] = [5, 10, 15, 20]) -> Dict[str, Any]:
        """Tune STM max_items parameter."""
        print("\n🔧 Tuning STM size...")
        
        best_config = None
        best_score = 0
        results = []
        
        for size in sizes:
            print(f"   Testing STM size: {size}")
            config = {'stm_max_items': size, 'mtm_max_chunks': 20, 'top_k': 3}
            
            evaluator = MemoryEvaluator(config)
            result = evaluator.run_full_evaluation()
            
            score = result['summary']['avg_f1_score']
            results.append({
                'stm_size': size,
                'score': score,
                'latency': result['summary']['avg_latency_ms'],
                'compression': result['summary']['compression_ratio']
            })
            
            if score > best_score:
                best_score = score
                best_config = config
            
            print(f"      F1: {score:.3f}, Latency: {result['summary']['avg_latency_ms']:.2f}ms")
        
        return {
            'parameter': 'stm_max_items',
            'best_value': best_config['stm_max_items'],
            'best_score': best_score,
            'results': results
        }
    
    def tune_mtm_size(self, sizes: List[int] = [10, 20, 30, 50]) -> Dict[str, Any]:
        """Tune MTM max_chunks parameter."""
        print("\n🔧 Tuning MTM size...")
        
        best_config = None
        best_score = 0
        results = []
        
        for size in sizes:
            print(f"   Testing MTM size: {size}")
            config = {'stm_max_items': 10, 'mtm_max_chunks': size, 'top_k': 3}
            
            evaluator = MemoryEvaluator(config)
            result = evaluator.run_full_evaluation()
            
            score = result['summary']['avg_f1_score']
            results.append({
                'mtm_size': size,
                'score': score,
                'latency': result['summary']['avg_latency_ms'],
                'compression': result['summary']['compression_ratio']
            })
            
            if score > best_score:
                best_score = score
                best_config = config
            
            print(f"      F1: {score:.3f}, Latency: {result['summary']['avg_latency_ms']:.2f}ms")
        
        return {
            'parameter': 'mtm_max_chunks',
            'best_value': best_config['mtm_max_chunks'],
            'best_score': best_score,
            'results': results
        }
    
    def tune_top_k(self, values: List[int] = [1, 3, 5, 7]) -> Dict[str, Any]:
        """Tune retrieval top_k parameter."""
        print("\n🔧 Tuning top_k...")
        
        best_config = None
        best_score = 0
        results = []
        
        for k in values:
            print(f"   Testing top_k: {k}")
            config = {'stm_max_items': 10, 'mtm_max_chunks': 20, 'top_k': k}
            
            evaluator = MemoryEvaluator(config)
            result = evaluator.run_full_evaluation()
            
            score = result['summary']['avg_f1_score']
            results.append({
                'top_k': k,
                'score': score,
                'latency': result['summary']['avg_latency_ms'],
                'compression': result['summary']['compression_ratio']
            })
            
            if score > best_score:
                best_score = score
                best_config = config
            
            print(f"      F1: {score:.3f}, Latency: {result['summary']['avg_latency_ms']:.2f}ms")
        
        return {
            'parameter': 'top_k',
            'best_value': best_config['top_k'],
            'best_score': best_score,
            'results': results
        }
    
    def run_grid_search(self) -> Dict[str, Any]:
        """Run grid search over parameter space."""
        print("╔" + "="*78 + "╗")
        print("║" + " "*25 + "PARAMETER TUNING" + " "*37 + "║")
        print("╚" + "="*78 + "╝")
        
        print("\n🔍 Running grid search...")
        
        stm_sizes = [5, 10, 15]
        mtm_sizes = [10, 20, 30]
        top_ks = [2, 3, 5]
        
        best_config = None
        best_score = 0
        all_results = []
        
        total = len(stm_sizes) * len(mtm_sizes) * len(top_ks)
        current = 0
        
        for stm_size in stm_sizes:
            for mtm_size in mtm_sizes:
                for top_k in top_ks:
                    current += 1
                    print(f"\n[{current}/{total}] Testing: STM={stm_size}, MTM={mtm_size}, top_k={top_k}")
                    
                    config = {
                        'stm_max_items': stm_size,
                        'mtm_max_chunks': mtm_size,
                        'top_k': top_k
                    }
                    
                    evaluator = MemoryEvaluator(config)
                    result = evaluator.run_full_evaluation()
                    
                    score = result['summary']['avg_f1_score']
                    
                    result_summary = {
                        'config': config,
                        'f1_score': score,
                        'precision': result['summary']['avg_precision'],
                        'recall': result['summary']['avg_recall'],
                        'latency_ms': result['summary']['avg_latency_ms'],
                        'compression_ratio': result['summary']['compression_ratio'],
                        'pass_rate': result['summary']['pass_rate']
                    }
                    all_results.append(result_summary)
                    
                    if score > best_score:
                        best_score = score
                        best_config = config
                    
                    print(f"   F1: {score:.3f}, Latency: {result['summary']['avg_latency_ms']:.2f}ms")
        
        # Sort by score
        all_results.sort(key=lambda x: x['f1_score'], reverse=True)
        
        print("\n" + "="*80)
        print("📊 TUNING RESULTS")
        print("="*80)
        print(f"Best Config:")
        print(f"  - STM size: {best_config['stm_max_items']}")
        print(f"  - MTM size: {best_config['mtm_max_chunks']}")
        print(f"  - top_k: {best_config['top_k']}")
        print(f"  - F1 Score: {best_score:.3f}")
        print("\nTop 5 configurations:")
        for i, r in enumerate(all_results[:5], 1):
            print(f"{i}. STM={r['config']['stm_max_items']}, MTM={r['config']['mtm_max_chunks']}, "
                  f"top_k={r['config']['top_k']} → F1={r['f1_score']:.3f}")
        print("="*80)
        
        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'method': 'grid_search',
            'best_config': best_config,
            'best_score': best_score,
            'all_results': all_results
        }
        
        report_file = f"tuning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Report saved: {report_file}")
        
        return report


def main():
    """Run parameter tuning."""
    import sys
    
    tuner = ParameterTuner()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == 'stm':
            result = tuner.tune_stm_size()
        elif mode == 'mtm':
            result = tuner.tune_mtm_size()
        elif mode == 'topk':
            result = tuner.tune_top_k()
        elif mode == 'grid':
            result = tuner.run_grid_search()
        else:
            print("Usage: python3 tune_parameters.py [stm|mtm|topk|grid]")
            sys.exit(1)
    else:
        # Default: run grid search
        result = tuner.run_grid_search()
    
    print("\n✅ Parameter tuning complete!")
    print("   Use best config in your application for optimal performance.")


if __name__ == "__main__":
    main()
