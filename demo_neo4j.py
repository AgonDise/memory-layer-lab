#!/usr/bin/env python3
"""
Demo for Neo4j integration with MTM and LTM.

This demonstrates:
1. Temporal Graph (commit timeline)
2. Knowledge Graph (code relationships)
3. LTM Knowledge Graph (design docs, concepts)
4. Vector Database (semantic search)
"""

import sys
from config import get_config

def demo_temporal_graph():
    """Demo: Temporal Graph for commit timeline."""
    print("=" * 60)
    print("DEMO 1: Temporal Graph (Commit Timeline)")
    print("=" * 60)
    
    from mtm import TemporalGraph
    
    # Initialize (works without Neo4j, uses mock storage)
    temporal = TemporalGraph(neo4j_driver=None)
    
    # Add commits
    commits = [
        {
            'id': 'abc123',
            'message': 'Fix bug in checkpoints.rs',
            'timestamp': '2025-09-30T10:00:00',
            'affected_files': ['checkpoints.rs', 'git.rs'],
            'author': 'developer1'
        },
        {
            'id': 'def456',
            'message': 'Refactor AST parser',
            'timestamp': '2025-09-30T11:00:00',
            'affected_files': ['parser.rs', 'ast.rs'],
            'author': 'developer2'
        },
        {
            'id': 'ghi789',
            'message': 'Update checkpoints logic',
            'timestamp': '2025-09-30T12:00:00',
            'affected_files': ['checkpoints.rs'],
            'author': 'developer1'
        }
    ]
    
    for commit in commits:
        success = temporal.add_commit(**commit)
        print(f"✓ Added commit: {commit['id']} - {commit['message']}")
    
    # Query commits affecting a file
    print(f"\n--- Commits affecting 'checkpoints.rs' ---")
    results = temporal.get_commits_affecting_file('checkpoints.rs', limit=10)
    for i, commit in enumerate(results, 1):
        print(f"{i}. [{commit['id']}] {commit.get('message', 'N/A')}")
    
    # Get timeline
    print(f"\n--- Recent Timeline ---")
    timeline = temporal.get_timeline(limit=5)
    for item in timeline:
        print(f"  {item['timestamp']}: {item.get('message', item.get('description', 'N/A'))}")

def demo_knowledge_graph():
    """Demo: Knowledge Graph for code relationships."""
    print("\n" + "=" * 60)
    print("DEMO 2: Knowledge Graph (Code Relationships)")
    print("=" * 60)
    
    from mtm import KnowledgeGraph
    
    kg = KnowledgeGraph(neo4j_driver=None)
    
    # Add functions
    functions = [
        {
            'name': 'apply_patch',
            'module': 'checkpoints',
            'file_path': 'src/checkpoints.rs',
            'signature': 'fn apply_patch(status: &Status) -> Result<()>',
            'doc': 'Apply a patch to the current status'
        },
        {
            'name': 'validate_status',
            'module': 'checkpoints',
            'file_path': 'src/checkpoints.rs',
            'signature': 'fn validate_status(status: &Status) -> bool',
            'doc': 'Validate status before applying patch'
        },
        {
            'name': 'parse_ast',
            'module': 'parser',
            'file_path': 'src/parser.rs',
            'signature': 'fn parse_ast(code: &str) -> AST',
            'doc': 'Parse code into AST'
        }
    ]
    
    for func in functions:
        kg.add_function(**func)
        print(f"✓ Added function: {func['module']}.{func['name']}")
    
    # Add call relationships
    print(f"\n--- Adding Call Relationships ---")
    kg.add_call_relationship('apply_patch', 'validate_status')
    print(f"  apply_patch → validate_status")
    
    # Query function calls
    print(f"\n--- Functions called by 'apply_patch' ---")
    calls = kg.get_function_calls('apply_patch')
    for call in calls:
        print(f"  → {call.get('to', 'N/A')}")

def demo_ltm_knowledge_graph():
    """Demo: LTM Knowledge Graph."""
    print("\n" + "=" * 60)
    print("DEMO 3: LTM Knowledge Graph (Design Docs & Concepts)")
    print("=" * 60)
    
    from ltm import LTMKnowledgeGraph
    
    ltm_kg = LTMKnowledgeGraph(neo4j_driver=None)
    
    # Add design docs
    print("--- Adding Design Documents ---")
    ltm_kg.add_design_doc(
        doc_id='design_v0.3',
        title='AST Parser Design',
        content='The AST parser uses a recursive descent approach with error recovery...',
        version='0.3',
        related_modules=['parser', 'ast', 'lexer']
    )
    print("✓ Added: AST Parser Design v0.3")
    
    ltm_kg.add_design_doc(
        doc_id='design_v0.4',
        title='Checkpoint System Architecture',
        content='The checkpoint system maintains state across operations...',
        version='0.4',
        related_modules=['checkpoints', 'git']
    )
    print("✓ Added: Checkpoint System Architecture v0.4")
    
    # Add domain concepts
    print(f"\n--- Adding Domain Concepts ---")
    concepts = [
        {
            'concept_id': 'ast_001',
            'name': 'Abstract Syntax Tree',
            'description': 'Tree representation of code structure',
            'category': 'architecture',
            'related_concepts': []
        },
        {
            'concept_id': 'checkpoint_001',
            'name': 'State Checkpoint',
            'description': 'Snapshot of system state at a point in time',
            'category': 'pattern',
            'related_concepts': ['ast_001']
        }
    ]
    
    for concept in concepts:
        ltm_kg.add_domain_concept(**concept)
        print(f"✓ Added concept: {concept['name']}")
    
    # Query design docs
    print(f"\n--- Design Docs for 'parser' module ---")
    docs = ltm_kg.query_design_docs('parser')
    for doc in docs:
        print(f"  [{doc.get('version', 'N/A')}] {doc.get('title', 'N/A')}")

def demo_vector_database():
    """Demo: Vector Database for semantic search."""
    print("\n" + "=" * 60)
    print("DEMO 4: Vector Database (Semantic Search)")
    print("=" * 60)
    
    from ltm import VectorDatabase
    from core import InputPreprocessor
    
    # Initialize
    vecdb = VectorDatabase(embedding_dim=384, backend='simple')
    preprocessor = InputPreprocessor(embedding_dim=384)
    
    # Add documents
    print("--- Adding Documents to Vector DB ---")
    documents = [
        {
            'id': 'doc_001',
            'content': 'The AST parser handles syntax errors gracefully by implementing error recovery mechanisms.',
        },
        {
            'id': 'doc_002',
            'content': 'Checkpoint system maintains state consistency across git operations and rollbacks.',
        },
        {
            'id': 'doc_003',
            'content': 'Bug report: drop(status) causes undefined variable error in checkpoints.rs line 433',
        }
    ]
    
    for doc in documents:
        # Generate embedding
        embedding = preprocessor._generate_embedding(doc['content'])
        
        # Add to vector DB
        vecdb.add_document(
            doc_id=doc['id'],
            content=doc['content'],
            embedding=embedding,
            metadata={'type': 'documentation'}
        )
        print(f"✓ Added: {doc['id']}")
    
    # Perform semantic search
    print(f"\n--- Semantic Search ---")
    queries = [
        'bug in checkpoints',
        'error handling in parser',
        'state management'
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        query_embedding = preprocessor._generate_embedding(query)
        results = vecdb.search(query_embedding, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. [Score: {result['score']:.3f}] {result['id']}")
            print(f"     {result['content'][:80]}...")
    
    # Show stats
    print(f"\n--- Vector DB Stats ---")
    stats = vecdb.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

def demo_integrated_query():
    """Demo: Integrated MTM + LTM query."""
    print("\n" + "=" * 60)
    print("DEMO 5: Integrated MTM + LTM Query")
    print("=" * 60)
    
    from mtm import TemporalGraph, KnowledgeGraph, MTMQuery
    from ltm import LTMKnowledgeGraph, VectorDatabase, LTMQuery
    from core import InputPreprocessor
    
    # Initialize all components
    temporal = TemporalGraph()
    kg = KnowledgeGraph()
    mtm_query = MTMQuery(temporal, kg)
    
    ltm_kg = LTMKnowledgeGraph()
    vecdb = VectorDatabase(embedding_dim=384, backend='simple')
    ltm_query = LTMQuery(ltm_kg, vecdb)
    preprocessor = InputPreprocessor(embedding_dim=384)
    
    # Populate with sample data (from previous demos)
    # ... (code omitted for brevity)
    
    # Query MTM context
    print("--- MTM Context ---")
    query = "checkpoints bug"
    mtm_context = mtm_query.get_mtm_context(query, top_k=3)
    print(f"Temporal items: {len(mtm_context['temporal_graph'])}")
    print(f"Knowledge items: {len(mtm_context['knowledge_graph'])}")
    
    # Query LTM context
    print(f"\n--- LTM Context ---")
    query_embedding = preprocessor._generate_embedding(query)
    ltm_context = ltm_query.get_ltm_context(query, query_embedding, top_k=3)
    print(f"Semantic matches: {len(ltm_context['semantic_search'])}")
    print(f"Knowledge graph: {len(ltm_context['knowledge_graph'])}")

def main():
    """Run all Neo4j demos."""
    print("\n" + "=" * 60)
    print("Neo4j Integration Demo")
    print("=" * 60)
    print("\nNote: Running in mock mode (Neo4j not required)")
    print("To use real Neo4j:")
    print("  1. Start Neo4j: docker-compose up -d neo4j")
    print("  2. Set NEO4J_CONFIG['enabled'] = True in config.py")
    print("  3. Pass neo4j_driver to modules")
    print("=" * 60)
    
    try:
        demo_temporal_graph()
        demo_knowledge_graph()
        demo_ltm_knowledge_graph()
        demo_vector_database()
        demo_integrated_query()
        
        print("\n" + "=" * 60)
        print("✅ All Neo4j demos completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("  • Start Neo4j: docker-compose up -d neo4j")
        print("  • Access UI: http://localhost:7474")
        print("  • Read setup guide: NEO4J_SETUP.md")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
