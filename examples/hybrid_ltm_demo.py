#!/usr/bin/env python3
"""
Hybrid LTM Demo

Demonstrates VectorDB + Knowledge Graph integration.
"""

from ltm.hybrid_ltm import HybridLTM, QueryStrategy, HybridResult


def demo_add_to_ltm(ltm: HybridLTM):
    """Demo: Adding data to both databases."""
    print("\n" + "="*80)
    print("📥 DEMO 1: Adding Data to Hybrid LTM")
    print("="*80)
    
    # Example 1: Add a function
    print("\n1️⃣ Adding function to LTM...")
    result1 = ltm.add(
        content="computeMetrics(data): Calculates mean, median, std. Raises ValueError on empty input.",
        metadata={
            'category': 'function',
            'function_name': 'computeMetrics',
            'file_path': 'analytics/stats.py',
            'line_start': 42,
            'line_end': 58,
            'tags': ['analytics', 'statistics'],
            'graph_links': [
                {'type': 'BELONGS_TO', 'target': 'module_analytics'},
                {'type': 'CALLS', 'target': 'func_calculateAverage'}
            ]
        }
    )
    print(f"   ✅ Vector ID: {result1['vector_id']}")
    print(f"   ✅ Graph Entity ID: {result1['graph_entity_id']}")
    
    # Example 2: Add a commit
    print("\n2️⃣ Adding commit to LTM...")
    result2 = ltm.add(
        content="Fixed division by zero error in computeMetrics. Added validation check before division operation.",
        metadata={
            'category': 'commit_log',
            'git_commit': 'abc123',
            'author': 'John Doe',
            'date': '2023-09-10',
            'file_path': 'analytics/stats.py',
            'graph_links': [
                {'type': 'FIXES', 'target': 'bug_242'},
                {'type': 'MODIFIES', 'target': 'func_computeMetrics'}
            ]
        }
    )
    print(f"   ✅ Vector ID: {result2['vector_id']}")
    print(f"   ✅ Graph Entity ID: {result2['graph_entity_id']}")
    
    # Example 3: Add a bug
    print("\n3️⃣ Adding bug report to LTM...")
    result3 = ltm.add(
        content="Bug #242: Division by zero in computeMetrics when processing empty datasets. Critical severity.",
        metadata={
            'category': 'guideline',  # Using existing schema category
            'issue_id': '#242',
            'severity': 'critical',
            'status': 'fixed',
            'tags': ['bug', 'divide-by-zero'],
            'graph_links': [
                {'type': 'AFFECTS', 'target': 'func_computeMetrics'}
            ]
        }
    )
    print(f"   ✅ Vector ID: {result3['vector_id']}")
    print(f"   ✅ Graph Entity ID: {result3['graph_entity_id']}")
    
    print("\n✅ All data added to both VectorDB and Knowledge Graph!")


def demo_vector_first_query(ltm: HybridLTM):
    """Demo: Vector-first query strategy."""
    print("\n" + "="*80)
    print("🔍 DEMO 2: Vector-First Query (Semantic → Structural)")
    print("="*80)
    
    query = "functions related to error handling"
    print(f"\n📝 Query: '{query}'")
    print("\nStrategy: Find semantically similar content, then expand with graph relationships")
    
    result = ltm.query(
        query=query,
        strategy=QueryStrategy.VECTOR_FIRST,
        top_k=3,
        expand_graph=True
    )
    
    print("\n📊 Results:")
    print(f"\n   Semantic Matches: {len(result.semantic_matches)}")
    for i, match in enumerate(result.semantic_matches[:3], 1):
        print(f"   {i}. {match.get('content', 'N/A')[:60]}...")
    
    print(f"\n   Graph Relations: {len(result.graph_relations)}")
    for i, rel in enumerate(result.graph_relations[:3], 1):
        print(f"   {i}. {rel}")
    
    print(f"\n   Combined Score: {result.combined_score:.3f}")
    print(f"   Strategy Used: {result.strategy_used.value}")


def demo_graph_first_query(ltm: HybridLTM):
    """Demo: Graph-first query strategy."""
    print("\n" + "="*80)
    print("🔍 DEMO 3: Graph-First Query (Structural → Semantic)")
    print("="*80)
    
    query = "commits by John Doe"
    print(f"\n📝 Query: '{query}'")
    print("\nStrategy: Query graph for precise match, then enrich with vector content")
    
    result = ltm.query(
        query=query,
        strategy=QueryStrategy.GRAPH_FIRST,
        top_k=5
    )
    
    print("\n📊 Results:")
    print(f"\n   Graph Relations: {len(result.graph_relations)}")
    for i, rel in enumerate(result.graph_relations[:3], 1):
        print(f"   {i}. {rel}")
    
    print(f"\n   Semantic Content: {len(result.semantic_matches)}")
    for i, match in enumerate(result.semantic_matches[:3], 1):
        print(f"   {i}. {match.get('content', 'N/A')[:60]}...")
    
    print(f"\n   Strategy Used: {result.strategy_used.value}")


def demo_parallel_query(ltm: HybridLTM):
    """Demo: Parallel query strategy."""
    print("\n" + "="*80)
    print("🔍 DEMO 4: Parallel Query (Both Simultaneously)")
    print("="*80)
    
    query = "how was the divide-by-zero bug fixed"
    print(f"\n📝 Query: '{query}'")
    print("\nStrategy: Query both databases in parallel for complex queries")
    
    result = ltm.query(
        query=query,
        strategy=QueryStrategy.PARALLEL,
        top_k=5
    )
    
    print("\n📊 Results:")
    print(f"\n   Semantic Matches: {len(result.semantic_matches)}")
    print(f"   Graph Relations: {len(result.graph_relations)}")
    print(f"   Combined Score: {result.combined_score:.3f}")
    print(f"   Parallel Execution: {result.metadata.get('parallel', False)}")


def demo_get_related(ltm: HybridLTM):
    """Demo: Get related entities."""
    print("\n" + "="*80)
    print("🔗 DEMO 5: Get Related Entities (Graph Traversal)")
    print("="*80)
    
    entity_id = "func_computeMetrics"
    print(f"\n📍 Starting from: {entity_id}")
    print("\nTraversing graph to find related entities...")
    
    related = ltm.get_related(
        entity_id=entity_id,
        relationship_types=['CALLS', 'BELONGS_TO', 'MODIFIES'],
        max_depth=2
    )
    
    print("\n📊 Related Entities:")
    print(f"   Count: {related['count']}")
    for i, item in enumerate(related['related'][:5], 1):
        node = item.get('node', {})
        content = item.get('content', 'No content')[:50]
        print(f"   {i}. {node.get('id', 'unknown')}: {content}...")


def demo_find_path(ltm: HybridLTM):
    """Demo: Find path between entities."""
    print("\n" + "="*80)
    print("🛤️  DEMO 6: Find Path Between Entities")
    print("="*80)
    
    start = "func_computeMetrics"
    end = "bug_242"
    print(f"\n📍 From: {start}")
    print(f"📍 To: {end}")
    print("\nFinding shortest path...")
    
    paths = ltm.find_path(start_id=start, end_id=end, max_length=5)
    
    print(f"\n📊 Paths Found: {len(paths)}")
    for i, path in enumerate(paths[:3], 1):
        print(f"   {i}. Length: {path.get('length', 'unknown')}")
        print(f"      Path: {path}")


def demo_comparison(ltm: HybridLTM):
    """Demo: Compare different strategies."""
    print("\n" + "="*80)
    print("⚖️  DEMO 7: Strategy Comparison")
    print("="*80)
    
    query = "analytics module functions"
    print(f"\n📝 Query: '{query}'")
    print("\nComparing all strategies...\n")
    
    strategies = [
        QueryStrategy.VECTOR_FIRST,
        QueryStrategy.GRAPH_FIRST,
        QueryStrategy.PARALLEL,
        QueryStrategy.VECTOR_ONLY,
        QueryStrategy.GRAPH_ONLY
    ]
    
    results = []
    for strategy in strategies:
        result = ltm.query(query=query, strategy=strategy, top_k=3)
        results.append({
            'strategy': strategy.value,
            'vector_count': len(result.semantic_matches),
            'graph_count': len(result.graph_relations),
            'score': result.combined_score
        })
    
    print("┌────────────────────┬────────┬───────┬───────┐")
    print("│ Strategy           │ Vector │ Graph │ Score │")
    print("├────────────────────┼────────┼───────┼───────┤")
    for r in results:
        print(f"│ {r['strategy']:<18} │ {r['vector_count']:>6} │ {r['graph_count']:>5} │ {r['score']:>5.2f} │")
    print("└────────────────────┴────────┴───────┴───────┘")


def main():
    """Run all demos."""
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "HYBRID LTM DEMO" + " "*38 + "║")
    print("╚" + "="*78 + "╝")
    
    print("\nInitializing Hybrid LTM...")
    print("   Note: Using mock databases for demo")
    
    # Initialize with mock DBs (for demo)
    ltm = HybridLTM(vector_db=None, graph_db=None)
    print(f"   Status: {ltm}")
    
    # Run demos
    try:
        demo_add_to_ltm(ltm)
        demo_vector_first_query(ltm)
        demo_graph_first_query(ltm)
        demo_parallel_query(ltm)
        demo_get_related(ltm)
        demo_find_path(ltm)
        demo_comparison(ltm)
        
        print("\n" + "="*80)
        print("✅ All demos completed successfully!")
        print("="*80)
        
        print("\n💡 Key Takeaways:")
        print("   • VectorDB = Semantic search (fuzzy, broad)")
        print("   • Graph = Structured queries (precise, relational)")
        print("   • Hybrid = Best of both worlds!")
        print("\n   Choose strategy based on query type:")
        print("   • Fuzzy search → Vector First")
        print("   • Precise query → Graph First")
        print("   • Complex query → Parallel")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
