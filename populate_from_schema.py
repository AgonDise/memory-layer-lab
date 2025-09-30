#!/usr/bin/env python3
"""
Populate memory layers from schema.yaml

This script:
1. Reads schema.yaml data
2. Generates embeddings for text
3. Populates STM, MTM, LTM with sample data
4. Demonstrates queries
"""

import yaml
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import hashlib

from config import get_config
from core import (
    ShortTermMemory, MidTermMemory, LongTermMemory,
    InputPreprocessor, MemoryOrchestrator, Summarizer
)
from mtm import TemporalGraph, KnowledgeGraph, MTMQuery
from ltm import LTMKnowledgeGraph, VectorDatabase, LTMQuery


class EmbeddingGenerator:
    """Generate consistent fake embeddings for testing."""
    
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
    
    def generate(self, text: str) -> List[float]:
        """
        Generate deterministic embedding from text.
        Uses hash of text to seed random generator for reproducibility.
        """
        # Use text hash as seed for reproducibility
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        np.random.seed(seed)
        
        # Generate random vector
        embedding = np.random.randn(self.embedding_dim)
        
        # Normalize to unit length
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.tolist()


def load_schema(file_path: str = 'schema.yaml') -> Dict[str, Any]:
    """Load data from schema.yaml."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data


def populate_short_term(stm: ShortTermMemory, 
                        data: List[Dict[str, Any]],
                        embedder: EmbeddingGenerator) -> None:
    """Populate short-term memory."""
    print("=" * 60)
    print("Populating Short-term Memory")
    print("=" * 60)
    
    for item in data:
        # Generate embedding for content
        embedding = embedder.generate(item['content'])
        
        # Add to STM
        stm.add(
            role=item['role'],
            content=item['content'],
            embedding=embedding,
            message_id=item.get('id'),
            token_count=item.get('token_count', 0),
            timestamp=item.get('timestamp')
        )
        
        print(f"✓ Added [{item['role']}]: {item['content'][:50]}...")
    
    print(f"\nTotal messages in STM: {len(stm.messages)}")


def populate_mid_term(mtm: MidTermMemory,
                     data: List[Dict[str, Any]],
                     embedder: EmbeddingGenerator,
                     temporal_graph: TemporalGraph = None,
                     knowledge_graph: KnowledgeGraph = None) -> None:
    """Populate mid-term memory."""
    print("\n" + "=" * 60)
    print("Populating Mid-term Memory")
    print("=" * 60)
    
    for item in data:
        # Generate or use existing embedding
        if 'embedding' in item and item['embedding']:
            emb_data = item['embedding']
            # Check if it's a valid list (not containing '...')
            if isinstance(emb_data, list) and len(emb_data) > 0 and emb_data[-1] != '...':
                # Truncate to match dimension if needed
                embedding = emb_data[:embedder.embedding_dim]
                # Pad if too short
                while len(embedding) < embedder.embedding_dim:
                    embedding.append(0.0)
            else:
                # Invalid or placeholder embedding, generate new one
                embedding = embedder.generate(item['text'])
        else:
            embedding = embedder.generate(item['text'])
        
        # Add to MTM chunks
        mtm.add_chunk(
            summary=item['text'],
            metadata={
                'chunk_id': item.get('id'),
                'embedding': embedding,
                **item.get('metadata', {})
            }
        )
        
        print(f"✓ Added chunk: {item['text'][:50]}...")
        
        # If temporal graph exists and has commit info
        if temporal_graph and item.get('metadata', {}).get('commit'):
            commit_id = item['metadata']['commit']
            file_name = item['metadata'].get('file', 'unknown.py')
            
            temporal_graph.add_commit(
                commit_id=commit_id,
                message=item['text'],
                timestamp=item['metadata'].get('timestamp', datetime.utcnow().isoformat()),
                affected_files=[file_name],
                author='developer'
            )
            print(f"  → Added to temporal graph: {commit_id}")
        
        # If knowledge graph exists and has function info
        if knowledge_graph and item.get('metadata', {}).get('function'):
            func_name = item['metadata']['function']
            module = item['metadata'].get('file', 'unknown').replace('.py', '')
            file_path = item['metadata'].get('file', 'unknown.py')
            
            knowledge_graph.add_function(
                name=func_name,
                module=module,
                file_path=file_path,
                doc=item['text']
            )
            print(f"  → Added to knowledge graph: {module}.{func_name}")
    
    print(f"\nTotal chunks in MTM: {len(mtm.chunks)}")


def populate_long_term_graph(ltm_kg: LTMKnowledgeGraph,
                             graph_data: Dict[str, Any]) -> None:
    """Populate long-term knowledge graph."""
    print("\n" + "=" * 60)
    print("Populating Long-term Knowledge Graph")
    print("=" * 60)
    
    nodes = graph_data.get('nodes', [])
    edges = graph_data.get('edges', [])
    
    # Add nodes
    print("\n--- Adding Nodes ---")
    for node in nodes:
        node_type = node.get('label')
        node_id = node.get('id')
        
        if node_type == 'Function':
            print(f"✓ Function: {node.get('name')}")
        elif node_type == 'Class':
            print(f"✓ Class: {node.get('name')}")
        elif node_type == 'Commit':
            print(f"✓ Commit: {node.get('hash')} - {node.get('message', '')[:40]}")
        elif node_type == 'Doc':
            ltm_kg.add_design_doc(
                doc_id=node_id,
                title=node.get('name', 'Untitled'),
                content=node.get('content', ''),
                version='1.0',
                related_modules=[]
            )
            print(f"✓ Design Doc: {node.get('name')}")
        else:
            print(f"✓ {node_type}: {node_id}")
    
    # Add edges
    print("\n--- Adding Relationships ---")
    for edge in edges:
        print(f"  {edge['from']} --[{edge['type']}]--> {edge['to']}")
    
    print(f"\nTotal nodes: {len(nodes)}, Total edges: {len(edges)}")


def populate_long_term_vector(vecdb: VectorDatabase,
                              vector_data: List[Dict[str, Any]],
                              embedder: EmbeddingGenerator) -> None:
    """Populate long-term vector database."""
    print("\n" + "=" * 60)
    print("Populating Long-term Vector Database")
    print("=" * 60)
    
    for item in vector_data:
        # Generate or use existing embedding
        if 'embedding' in item and item['embedding']:
            emb_data = item['embedding']
            # Check if it's a valid list (not containing '...')
            if isinstance(emb_data, list) and len(emb_data) > 0 and emb_data[-1] != '...':
                embedding = emb_data[:embedder.embedding_dim]
                while len(embedding) < embedder.embedding_dim:
                    embedding.append(0.0)
            else:
                # Invalid or placeholder embedding, generate new one
                embedding = embedder.generate(item['text'])
        else:
            embedding = embedder.generate(item['text'])
        
        # Add to vector DB
        vecdb.add_document(
            doc_id=item['id'],
            content=item['text'],
            embedding=embedding,
            metadata=item.get('metadata', {})
        )
        
        print(f"✓ Added document: {item['id']} - {item['text'][:50]}...")
    
    stats = vecdb.get_stats()
    print(f"\nVector DB: {stats['total_documents']} documents")


def demo_queries(stm: ShortTermMemory,
                mtm: MidTermMemory,
                ltm: LongTermMemory,
                embedder: EmbeddingGenerator):
    """Demonstrate queries on populated data."""
    print("\n" + "=" * 60)
    print("DEMO: Querying Memory Layers")
    print("=" * 60)
    
    queries = [
        "login_user function",
        "auth_service.py",
        "commit abc123",
        "OAuth2 authentication"
    ]
    
    for query in queries:
        print(f"\n--- Query: '{query}' ---")
        query_embedding = embedder.generate(query)
        
        # Query STM
        stm_results = stm.search_by_embedding(query_embedding, top_k=2)
        print(f"\n  STM Results ({len(stm_results)}):")
        for i, msg in enumerate(stm_results, 1):
            print(f"    {i}. [{msg['role']}] {msg['content'][:60]}...")
            if 'relevance_score' in msg:
                print(f"       Score: {msg['relevance_score']:.3f}")
        
        # Query MTM
        mtm_results = mtm.search_by_embedding(query_embedding, top_k=2)
        print(f"\n  MTM Results ({len(mtm_results)}):")
        for i, chunk in enumerate(mtm_results, 1):
            print(f"    {i}. {chunk['summary'][:60]}...")
            print(f"       Score: {chunk.get('relevance_score', 0):.3f}")
        
        # Query LTM (if vector DB enabled)
        if ltm.vecdb_enabled and ltm.vector_db:
            ltm_results = ltm.vector_db.search(query_embedding, top_k=2)
            print(f"\n  LTM Vector Results ({len(ltm_results)}):")
            for i, doc in enumerate(ltm_results, 1):
                print(f"    {i}. [{doc['id']}] {doc['content'][:60]}...")
                print(f"       Score: {doc.get('score', 0):.3f}")


def main():
    """Main function."""
    print("=" * 60)
    print("Memory Layer Population from schema.yaml")
    print("=" * 60)
    
    # Load schema
    print("\n📂 Loading schema.yaml...")
    try:
        schema = load_schema('schema.yaml')
    except FileNotFoundError:
        print("❌ Error: schema.yaml not found!")
        return
    
    # Initialize embedding generator
    embedding_dim = 384
    embedder = EmbeddingGenerator(embedding_dim=embedding_dim)
    print(f"✓ Embedding generator initialized (dim={embedding_dim})")
    
    # Initialize memory layers
    print("\n🔧 Initializing memory layers...")
    
    # STM
    stm = ShortTermMemory(max_size=20, ttl_seconds=3600)
    
    # MTM with optional Neo4j
    temporal_graph = TemporalGraph()  # Mock mode
    knowledge_graph = KnowledgeGraph()  # Mock mode
    mtm_query = MTMQuery(temporal_graph, knowledge_graph)
    mtm = MidTermMemory(
        max_size=100,
        temporal_graph=temporal_graph,
        knowledge_graph=knowledge_graph,
        mtm_query=mtm_query
    )
    
    # LTM with Vector DB
    ltm_kg = LTMKnowledgeGraph()  # Mock mode
    vecdb = VectorDatabase(embedding_dim=embedding_dim, backend='simple')
    ltm_query = LTMQuery(ltm_kg, vecdb)
    ltm = LongTermMemory(
        enabled=True,
        knowledge_graph=ltm_kg,
        vector_db=vecdb,
        ltm_query=ltm_query
    )
    
    print("✓ All memory layers initialized")
    
    # Populate data
    print("\n" + "=" * 60)
    print("POPULATING DATA")
    print("=" * 60)
    
    # Populate STM
    if 'short_term' in schema and schema['short_term']:
        populate_short_term(stm, schema['short_term'], embedder)
    
    # Populate MTM
    if 'mid_term' in schema and schema['mid_term']:
        populate_mid_term(mtm, schema['mid_term'], embedder, 
                         temporal_graph, knowledge_graph)
    
    # Populate LTM
    if 'long_term' in schema and schema['long_term']:
        lt_data = schema['long_term']
        
        # Graph data
        if 'graph' in lt_data and lt_data['graph']:
            populate_long_term_graph(ltm_kg, lt_data['graph'])
        
        # Vector data
        if 'vector' in lt_data and lt_data['vector']:
            populate_long_term_vector(vecdb, lt_data['vector'], embedder)
    
    # Demo queries
    demo_queries(stm, mtm, ltm, embedder)
    
    # Final stats
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✓ STM: {len(stm.messages)} messages")
    print(f"✓ MTM: {len(mtm.chunks)} chunks")
    if mtm.temporal_graph:
        print(f"  └─ Temporal: {len(temporal_graph.commits)} commits")
    if mtm.knowledge_graph:
        print(f"  └─ Knowledge: {len(knowledge_graph.nodes)} nodes")
    print(f"✓ LTM Vector: {vecdb.get_stats()['total_documents']} documents")
    
    print("\n✅ Population complete!")
    print("\nNext steps:")
    print("  • Modify schema.yaml to add more data")
    print("  • Run: python populate_from_schema.py")
    print("  • Try different queries in demo_queries()")


if __name__ == '__main__':
    main()
