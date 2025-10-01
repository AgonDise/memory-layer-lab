#!/usr/bin/env python3
"""
Load data into Long-Term Memory (Neo4j).

Usage:
    # Load mid-term data
    python3 load_ltm_data.py --type mtm --file data/mid_term_chunks.json
    
    # Load long-term data
    python3 load_ltm_data.py --type ltm --file data/long_term_facts.json
    
    # Load both (auto-detect from data/ folder)
    python3 load_ltm_data.py --all
    
    # With custom config
    python3 load_ltm_data.py --type ltm --file your_data.json --config config/neo4j_config.yaml
"""

import argparse
import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from utils.neo4j_manager import Neo4jManager


def load_neo4j_config(config_file: str = "config/neo4j_config.yaml") -> Dict[str, Any]:
    """Load Neo4j configuration."""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('neo4j', {})
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_file}")
        print(f"   Copy config/neo4j_config.yaml.example to config/neo4j_config.yaml")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        sys.exit(1)


def load_data_file(file_path: str) -> Dict[str, Any]:
    """Load data from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded data from {file_path}")
        return data
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {file_path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)


def validate_mtm_data(data: Dict[str, Any]) -> bool:
    """Validate mid-term memory data format."""
    if 'chunks' not in data:
        print("❌ Invalid MTM data: missing 'chunks' field")
        return False
    
    chunks = data['chunks']
    if not isinstance(chunks, list):
        print("❌ Invalid MTM data: 'chunks' must be a list")
        return False
    
    print(f"✅ Valid MTM data: {len(chunks)} chunks")
    return True


def validate_ltm_data(data: Dict[str, Any]) -> bool:
    """Validate long-term memory data format."""
    if 'facts' not in data:
        print("❌ Invalid LTM data: missing 'facts' field")
        return False
    
    facts = data['facts']
    if not isinstance(facts, list):
        print("❌ Invalid LTM data: 'facts' must be a list")
        return False
    
    print(f"✅ Valid LTM data: {len(facts)} facts")
    return True


def load_mtm_chunks(manager: Neo4jManager, chunks: List[Dict[str, Any]], batch_size: int = 100) -> int:
    """
    Load mid-term memory chunks into Neo4j.
    
    Args:
        manager: Neo4j manager
        chunks: List of chunk data
        batch_size: Number of items per batch
        
    Returns:
        Number of chunks loaded
    """
    print(f"\n📦 Loading {len(chunks)} MTM chunks...")
    
    loaded = 0
    failed = 0
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        
        print(f"   Batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
        
        for chunk in batch:
            try:
                # Extract data
                chunk_id = chunk.get('id', f"mtm_chunk_{loaded+1}")
                summary = chunk.get('summary', '')
                embedding = chunk.get('embedding', [])
                metadata = chunk.get('metadata', {})
                
                # Create Cypher query
                query = """
                MERGE (c:Chunk {id: $id})
                SET c.summary = $summary,
                    c.timestamp = $timestamp,
                    c.topic = $topic,
                    c.importance = $importance,
                    c.message_count = $message_count,
                    c.updated_at = datetime()
                """
                
                # Add embedding if available
                if embedding:
                    query += ", c.embedding = $embedding"
                
                query += " RETURN c.id as id"
                
                params = {
                    'id': chunk_id,
                    'summary': summary,
                    'timestamp': metadata.get('timestamp', datetime.now().isoformat()),
                    'topic': metadata.get('topic', 'general'),
                    'importance': metadata.get('importance', 0.5),
                    'message_count': metadata.get('message_count', 0),
                }
                
                if embedding:
                    params['embedding'] = embedding
                
                result = manager.execute_query(query, params)
                
                if result:
                    loaded += 1
                else:
                    failed += 1
                    print(f"      ⚠️  Failed to load chunk: {chunk_id}")
                    
            except Exception as e:
                failed += 1
                print(f"      ❌ Error loading chunk: {e}")
        
        print(f"      ✅ Loaded {loaded} chunks so far...")
    
    print(f"\n✅ MTM loading complete: {loaded} loaded, {failed} failed")
    return loaded


def load_ltm_facts(manager: Neo4jManager, facts: List[Dict[str, Any]], batch_size: int = 100) -> int:
    """
    Load long-term memory facts into Neo4j.
    
    Args:
        manager: Neo4j manager
        facts: List of fact data
        batch_size: Number of items per batch
        
    Returns:
        Number of facts loaded
    """
    print(f"\n📚 Loading {len(facts)} LTM facts...")
    
    loaded = 0
    failed = 0
    
    for i in range(0, len(facts), batch_size):
        batch = facts[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(facts) + batch_size - 1) // batch_size
        
        print(f"   Batch {batch_num}/{total_batches} ({len(batch)} facts)...")
        
        for fact in batch:
            try:
                # Extract data
                fact_id = fact.get('id', f"ltm_fact_{loaded+1}")
                content = fact.get('content', '')
                embedding = fact.get('embedding', [])
                metadata = fact.get('metadata', {})
                
                # Create Cypher query
                query = """
                MERGE (f:Fact {id: $id})
                SET f.content = $content,
                    f.category = $category,
                    f.importance = $importance,
                    f.access_count = $access_count,
                    f.last_accessed = $last_accessed,
                    f.created_at = $created_at,
                    f.updated_at = datetime()
                """
                
                # Add embedding if available
                if embedding:
                    query += ", f.embedding = $embedding"
                
                # Add tags
                tags = metadata.get('tags', [])
                if tags:
                    query += ", f.tags = $tags"
                
                query += " RETURN f.id as id"
                
                params = {
                    'id': fact_id,
                    'content': content,
                    'category': metadata.get('category', 'general'),
                    'importance': metadata.get('importance', 0.5),
                    'access_count': metadata.get('access_count', 0),
                    'last_accessed': metadata.get('last_accessed', datetime.now().isoformat()),
                    'created_at': metadata.get('created_at', datetime.now().isoformat()),
                }
                
                if embedding:
                    params['embedding'] = embedding
                if tags:
                    params['tags'] = tags
                
                result = manager.execute_query(query, params)
                
                if result:
                    loaded += 1
                else:
                    failed += 1
                    print(f"      ⚠️  Failed to load fact: {fact_id}")
                    
            except Exception as e:
                failed += 1
                print(f"      ❌ Error loading fact: {e}")
        
        print(f"      ✅ Loaded {loaded} facts so far...")
    
    print(f"\n✅ LTM loading complete: {loaded} loaded, {failed} failed")
    return loaded


def create_indexes(manager: Neo4jManager):
    """Create necessary indexes for performance."""
    print("\n📑 Creating indexes...")
    
    indexes = [
        {"label": "Chunk", "property": "id", "type": "btree"},
        {"label": "Chunk", "property": "timestamp", "type": "btree"},
        {"label": "Chunk", "property": "topic", "type": "btree"},
        {"label": "Fact", "property": "id", "type": "btree"},
        {"label": "Fact", "property": "category", "type": "btree"},
        {"label": "Fact", "property": "importance", "type": "btree"},
    ]
    
    # Note: Vector indexes require Neo4j 5.11+ and specific configuration
    # Uncomment if your Neo4j version supports it
    # indexes.extend([
    #     {"label": "Chunk", "property": "embedding", "type": "vector"},
    #     {"label": "Fact", "property": "embedding", "type": "vector"},
    # ])
    
    created = manager.create_indexes(indexes)
    print(f"✅ Created {created} indexes")


def show_statistics(manager: Neo4jManager):
    """Show database statistics after loading."""
    print("\n📊 Database Statistics:")
    
    # Count chunks
    result = manager.execute_query("MATCH (c:Chunk) RETURN count(c) as count")
    if result:
        print(f"   Chunks: {result[0]['count']}")
    
    # Count facts
    result = manager.execute_query("MATCH (f:Fact) RETURN count(f) as count")
    if result:
        print(f"   Facts: {result[0]['count']}")
    
    # Count by category
    result = manager.execute_query("""
        MATCH (f:Fact)
        RETURN f.category as category, count(f) as count
        ORDER BY count DESC
        LIMIT 10
    """)
    if result:
        print(f"\n   Top categories:")
        for record in result:
            print(f"      - {record['category']}: {record['count']}")


def main():
    parser = argparse.ArgumentParser(description='Load data into Long-Term Memory')
    parser.add_argument('--type', choices=['mtm', 'ltm'], help='Data type (mtm or ltm)')
    parser.add_argument('--file', help='Data file path')
    parser.add_argument('--all', action='store_true', help='Load all data from data/ folder')
    parser.add_argument('--config', default='config/neo4j_config.yaml', help='Neo4j config file')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for loading')
    parser.add_argument('--create-indexes', action='store_true', help='Create indexes after loading')
    
    args = parser.parse_args()
    
    print("="*80)
    print("📥 LONG-TERM MEMORY DATA LOADER")
    print("="*80)
    
    # Validate arguments
    if not args.all and (not args.type or not args.file):
        print("\n❌ Error: Either use --all or specify both --type and --file")
        parser.print_help()
        sys.exit(1)
    
    # Load Neo4j config
    print(f"\n🔧 Loading Neo4j configuration...")
    neo4j_config = load_neo4j_config(args.config)
    
    # Create manager
    manager = Neo4jManager(
        uri=neo4j_config['uri'],
        username=neo4j_config['username'],
        password=neo4j_config['password'],
        database=neo4j_config.get('database', 'neo4j'),
    )
    
    # Test connection
    print(f"\n🔌 Testing connection to Neo4j...")
    if not manager.connect():
        print("❌ Failed to connect to Neo4j")
        sys.exit(1)
    
    print(f"✅ Connected to Neo4j at {neo4j_config['uri']}")
    
    # Load data
    total_loaded = 0
    
    if args.all:
        # Load both MTM and LTM
        files = [
            ('mtm', 'data/mid_term_chunks.json'),
            ('ltm', 'data/long_term_facts.json'),
        ]
        
        for data_type, file_path in files:
            if Path(file_path).exists():
                print(f"\n{'='*80}")
                print(f"📂 Loading {data_type.upper()} from {file_path}")
                print("="*80)
                
                data = load_data_file(file_path)
                
                if data_type == 'mtm':
                    if validate_mtm_data(data):
                        count = load_mtm_chunks(manager, data['chunks'], args.batch_size)
                        total_loaded += count
                elif data_type == 'ltm':
                    if validate_ltm_data(data):
                        count = load_ltm_facts(manager, data['facts'], args.batch_size)
                        total_loaded += count
            else:
                print(f"⚠️  File not found: {file_path} (skipping)")
    else:
        # Load single file
        print(f"\n{'='*80}")
        print(f"📂 Loading {args.type.upper()} from {args.file}")
        print("="*80)
        
        data = load_data_file(args.file)
        
        if args.type == 'mtm':
            if validate_mtm_data(data):
                count = load_mtm_chunks(manager, data['chunks'], args.batch_size)
                total_loaded += count
        elif args.type == 'ltm':
            if validate_ltm_data(data):
                count = load_ltm_facts(manager, data['facts'], args.batch_size)
                total_loaded += count
    
    # Create indexes if requested
    if args.create_indexes:
        create_indexes(manager)
    
    # Show statistics
    show_statistics(manager)
    
    # Summary
    print("\n" + "="*80)
    print("🎉 DATA LOADING COMPLETE")
    print("="*80)
    print(f"\n✅ Total items loaded: {total_loaded}")
    print(f"🗄️  Database: {neo4j_config['uri']}/{neo4j_config.get('database', 'neo4j')}")
    print("\n💡 Next steps:")
    print("   1. Test LTM integration: python3 test_ltm_integration.py")
    print("   2. Run full pipeline test: python3 test_full_pipeline.py")
    print("="*80 + "\n")
    
    manager.disconnect()


if __name__ == "__main__":
    main()
