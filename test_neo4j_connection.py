#!/usr/bin/env python3
"""
Test Neo4j connection and setup.

Usage:
    python3 test_neo4j_connection.py
    python3 test_neo4j_connection.py --uri bolt://your-host:7687 --username neo4j --password yourpass
"""

import argparse
import yaml
import sys
from pathlib import Path
from utils.neo4j_manager import Neo4jManager


def load_config(config_file: str = "config/neo4j_config.yaml") -> dict:
    """Load Neo4j configuration from YAML file."""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('neo4j', {})
    except FileNotFoundError:
        print(f"⚠️  Config file not found: {config_file}")
        print(f"   Copy config/neo4j_config.yaml.example to config/neo4j_config.yaml")
        return {}
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return {}


def test_connection(manager: Neo4jManager) -> bool:
    """Test Neo4j connection."""
    print("\n" + "="*80)
    print("🔌 TESTING NEO4J CONNECTION")
    print("="*80)
    
    print(f"\n📡 Connecting to: {manager.uri}")
    print(f"👤 Username: {manager.username}")
    print(f"🗄️  Database: {manager.database}")
    
    # Test connection
    if manager.connect():
        print("✅ Connection successful!")
        return True
    else:
        print("❌ Connection failed!")
        return False


def test_health_check(manager: Neo4jManager):
    """Perform health check."""
    print("\n" + "="*80)
    print("🏥 HEALTH CHECK")
    print("="*80)
    
    health = manager.health_check()
    
    print(f"\n📊 Status:")
    print(f"   Connected: {'✅ Yes' if health['connected'] else '❌ No'}")
    print(f"   URI: {health['uri']}")
    print(f"   Database: {health['database']}")
    
    if health.get('version'):
        print(f"   Version: {health['version']}")
    if health.get('edition'):
        print(f"   Edition: {health['edition']}")
    if health.get('node_count') is not None:
        print(f"   Node count: {health['node_count']}")
    
    if health.get('error'):
        print(f"\n❌ Error: {health['error']}")
        return False
    
    return True


def test_simple_query(manager: Neo4jManager):
    """Test a simple query."""
    print("\n" + "="*80)
    print("📝 TESTING SIMPLE QUERY")
    print("="*80)
    
    query = "RETURN 'Hello from Neo4j!' AS message, datetime() AS timestamp"
    
    print(f"\nQuery: {query}")
    result = manager.execute_query(query)
    
    if result:
        print(f"✅ Query successful!")
        print(f"\nResult:")
        for record in result:
            for key, value in record.items():
                print(f"   {key}: {value}")
        return True
    else:
        print(f"❌ Query failed!")
        return False


def test_write_read(manager: Neo4jManager):
    """Test write and read operations."""
    print("\n" + "="*80)
    print("✍️  TESTING WRITE & READ")
    print("="*80)
    
    # Create a test node
    create_query = """
    CREATE (n:TestNode {
        id: 'test_' + toString(timestamp()),
        content: 'This is a test node',
        created_at: datetime()
    })
    RETURN n.id as id
    """
    
    print("\n1️⃣ Creating test node...")
    result = manager.execute_query(create_query)
    
    if not result:
        print("❌ Failed to create test node")
        return False
    
    test_id = result[0]['id']
    print(f"✅ Created node with ID: {test_id}")
    
    # Read the test node
    read_query = """
    MATCH (n:TestNode {id: $id})
    RETURN n.id as id, n.content as content, n.created_at as created_at
    """
    
    print("\n2️⃣ Reading test node...")
    result = manager.execute_query(read_query, {'id': test_id})
    
    if not result:
        print("❌ Failed to read test node")
        return False
    
    print(f"✅ Read node successfully:")
    for key, value in result[0].items():
        print(f"   {key}: {value}")
    
    # Delete the test node
    delete_query = """
    MATCH (n:TestNode {id: $id})
    DELETE n
    """
    
    print("\n3️⃣ Deleting test node...")
    if manager.execute_write(delete_query, {'id': test_id}):
        print(f"✅ Deleted test node")
        return True
    else:
        print(f"❌ Failed to delete test node")
        return False


def test_indexes(manager: Neo4jManager):
    """Test index creation."""
    print("\n" + "="*80)
    print("📑 TESTING INDEX CREATION")
    print("="*80)
    
    # Check existing indexes
    check_query = "SHOW INDEXES"
    
    print("\n1️⃣ Checking existing indexes...")
    result = manager.execute_query(check_query)
    
    if result:
        print(f"✅ Found {len(result)} existing indexes")
        for idx in result[:5]:  # Show first 5
            print(f"   - {idx.get('name', 'unnamed')}: {idx.get('labelsOrTypes', [])} on {idx.get('properties', [])}")
        if len(result) > 5:
            print(f"   ... and {len(result) - 5} more")
    else:
        print("⚠️  Could not retrieve indexes (may not have permissions)")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Test Neo4j connection')
    parser.add_argument('--uri', help='Neo4j URI (e.g., bolt://localhost:7687)')
    parser.add_argument('--username', help='Neo4j username')
    parser.add_argument('--password', help='Neo4j password')
    parser.add_argument('--database', default='neo4j', help='Database name')
    parser.add_argument('--config', default='config/neo4j_config.yaml', help='Config file path')
    
    args = parser.parse_args()
    
    print("="*80)
    print("🚀 NEO4J CONNECTION TEST SUITE")
    print("="*80)
    
    # Load config
    if args.uri:
        # Use command line arguments
        config = {
            'uri': args.uri,
            'username': args.username or 'neo4j',
            'password': args.password or '',
            'database': args.database
        }
    else:
        # Load from config file
        config = load_config(args.config)
        if not config:
            print("\n❌ No configuration provided!")
            print("\nOptions:")
            print("1. Copy config/neo4j_config.yaml.example to config/neo4j_config.yaml and edit")
            print("2. Use command line arguments: --uri --username --password")
            sys.exit(1)
    
    # Validate config
    required = ['uri', 'username', 'password']
    missing = [key for key in required if not config.get(key)]
    if missing:
        print(f"\n❌ Missing required configuration: {', '.join(missing)}")
        sys.exit(1)
    
    # Create manager
    manager = Neo4jManager(
        uri=config['uri'],
        username=config['username'],
        password=config['password'],
        database=config.get('database', 'neo4j'),
        max_connection_lifetime=config.get('max_connection_lifetime', 3600),
        max_connection_pool_size=config.get('max_connection_pool_size', 50),
        connection_acquisition_timeout=config.get('connection_acquisition_timeout', 60),
        encrypted=config.get('encrypted', False),
        max_retry_time=config.get('max_retry_time', 30),
        initial_retry_delay=config.get('initial_retry_delay', 1.0)
    )
    
    # Run tests
    tests = [
        ("Connection", lambda: test_connection(manager)),
        ("Health Check", lambda: test_health_check(manager)),
        ("Simple Query", lambda: test_simple_query(manager)),
        ("Write & Read", lambda: test_write_read(manager)),
        ("Indexes", lambda: test_indexes(manager)),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed\n")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    # Final status
    print("\n" + "="*80)
    if passed == total:
        print("🎉 ALL TESTS PASSED! Neo4j is ready to use!")
    elif passed > 0:
        print("⚠️  SOME TESTS FAILED - Check errors above")
    else:
        print("❌ ALL TESTS FAILED - Check your Neo4j configuration")
    print("="*80 + "\n")
    
    # Cleanup
    manager.disconnect()
    
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
