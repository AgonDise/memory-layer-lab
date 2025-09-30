# Neo4j Setup Guide

## 🚀 Quick Start with Docker

### 1. Start Neo4j

```bash
# Start Neo4j container
docker-compose up -d neo4j

# Check if running
docker ps | grep neo4j
```

### 2. Access Neo4j Browser

Open: http://localhost:7474

**Login credentials:**
- Username: `neo4j`
- Password: `test123`

### 3. Create Databases

Neo4j supports multiple databases. Create two for our use:

```cypher
// In Neo4j Browser, run:
CREATE DATABASE temporal_kg;
CREATE DATABASE longterm_kg;
```

### 4. Verify Setup

```cypher
// Switch to temporal_kg
:use temporal_kg

// Create a test node
CREATE (n:Test {name: 'Hello'}) RETURN n;

// Delete test node
MATCH (n:Test) DELETE n;
```

---

## 📊 Database Schema

### Temporal Graph (temporal_kg) - MTM

**Nodes:**
- `Commit`: Git commits
  - Properties: `id`, `message`, `timestamp`, `author`
- `Checkpoint`: Code checkpoints
  - Properties: `id`, `description`, `timestamp`
- `File`: Source code files
  - Properties: `name`, `path`

**Relationships:**
- `(Commit)-[:NEXT]->(Commit)` - Sequential commits
- `(Commit)-[:AFFECTS]->(File)` - Which files changed
- `(Checkpoint)-[:LINKED_TO]->(Commit)` - Checkpoint associations

**Example Queries:**

```cypher
// Find commits affecting a file
MATCH (c:Commit)-[:AFFECTS]->(f:File {name: 'checkpoints.rs'})
RETURN c.id, c.message, c.timestamp
ORDER BY c.timestamp DESC
LIMIT 10;

// Get commit timeline
MATCH (c:Commit)
RETURN c
ORDER BY c.timestamp DESC
LIMIT 20;
```

### Knowledge Graph (temporal_kg & longterm_kg) - MTM & LTM

**Nodes:**
- `Function`: Code functions
  - Properties: `name`, `module`, `file_path`, `signature`, `doc`
- `Class`: Code classes
  - Properties: `name`, `module`, `file_path`, `doc`
- `Module`: Code modules
  - Properties: `name`, `path`
- `Concept`: Domain concepts (LTM only)
  - Properties: `id`, `name`, `description`, `category`
- `DesignDoc`: Design documents (LTM only)
  - Properties: `id`, `title`, `content`, `version`

**Relationships:**
- `(Function)-[:CALLS]->(Function)` - Function calls
- `(Function)-[:BELONGS_TO]->(Module)` - Module membership
- `(Class)-[:BELONGS_TO]->(Module)` - Module membership
- `(Concept)-[:RELATED_TO]->(Concept)` - Concept relationships
- `(DesignDoc)-[:DESCRIBES]->(Module)` - Documentation

**Example Queries:**

```cypher
// Find what a function calls
MATCH (f:Function {name: 'apply_patch'})-[:CALLS*1..2]->(called:Function)
RETURN f.name, called.name, called.module;

// Get module structure
MATCH (m:Module)<-[:BELONGS_TO]-(item)
WHERE m.name = 'checkpoints'
RETURN m, item;

// Find related concepts
MATCH (c:Concept {name: 'AST'})-[:RELATED_TO*1..2]-(related:Concept)
RETURN c.name, related.name, related.category;
```

---

## 🔧 Configuration in Code

### Enable Neo4j in config.py

```python
NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7687',
    'user': 'neo4j',
    'password': 'test123',
    'databases': {
        'temporal': 'temporal_kg',
        'knowledge': 'longterm_kg',
    },
    'enabled': True,  # Set to True to enable
}
```

### Initialize in main.py

```python
from neo4j import GraphDatabase
from mtm import TemporalGraph, KnowledgeGraph, MTMQuery
from ltm import LTMKnowledgeGraph, VectorDatabase, LTMQuery

# Create Neo4j driver
neo4j_driver = GraphDatabase.driver(
    neo4j_config['uri'],
    auth=(neo4j_config['user'], neo4j_config['password'])
)

# Initialize MTM with Neo4j
temporal_graph = TemporalGraph(neo4j_driver, 'temporal_kg')
knowledge_graph = KnowledgeGraph(neo4j_driver, 'temporal_kg')
mtm_query = MTMQuery(temporal_graph, knowledge_graph)

# Initialize LTM with Neo4j and Vector DB
ltm_kg = LTMKnowledgeGraph(neo4j_driver, 'longterm_kg')
vector_db = VectorDatabase(embedding_dim=384, backend='faiss')
ltm_query = LTMQuery(ltm_kg, vector_db)

# Create memory layers
mid_term = MidTermMemory(
    max_size=100,
    temporal_graph=temporal_graph,
    knowledge_graph=knowledge_graph,
    mtm_query=mtm_query
)

long_term = LongTermMemory(
    enabled=True,
    knowledge_graph=ltm_kg,
    vector_db=vector_db,
    ltm_query=ltm_query
)
```

---

## 📝 Example Usage

### Add Commit to Temporal Graph

```python
temporal_graph.add_commit(
    commit_id='abc123',
    message='Fix bug in checkpoints',
    timestamp='2025-09-30T10:00:00',
    affected_files=['checkpoints.rs', 'git.rs'],
    author='developer'
)
```

### Add Function to Knowledge Graph

```python
knowledge_graph.add_function(
    name='apply_patch',
    module='checkpoints',
    file_path='src/checkpoints.rs',
    signature='fn apply_patch(status: &Status) -> Result<()>',
    doc='Apply a patch to the current status'
)

knowledge_graph.add_call_relationship('apply_patch', 'validate_status')
```

### Add Design Doc to LTM

```python
ltm_kg.add_design_doc(
    doc_id='design_v0.3',
    title='AST Parser Design',
    content='The AST parser uses a recursive descent approach...',
    version='0.3',
    related_modules=['parser', 'ast']
)
```

### Query MTM Context

```python
mtm_context = mtm_query.get_mtm_context('find bug in checkpoints', top_k=5)
print(mtm_context['temporal_graph'])  # Recent commits
print(mtm_context['knowledge_graph'])  # Related functions
```

---

## 🛠️ Management Commands

### Stop Neo4j

```bash
docker-compose stop neo4j
```

### Restart Neo4j

```bash
docker-compose restart neo4j
```

### View Logs

```bash
docker-compose logs -f neo4j
```

### Backup Data

```bash
# Neo4j data is stored in Docker volume
docker run --rm -v memory-layer-lab_neo4j_data:/data -v $(pwd):/backup ubuntu tar czf /backup/neo4j_backup.tar.gz /data
```

### Clear All Data

```bash
docker-compose down -v  # Warning: Deletes all data!
```

---

## 🔍 Debugging

### Check Connection

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'bolt://localhost:7687',
    auth=('neo4j', 'test123')
)

try:
    driver.verify_connectivity()
    print("✅ Connected to Neo4j!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
finally:
    driver.close()
```

### Common Issues

**Port already in use:**
```bash
# Check what's using port 7687
lsof -i :7687

# Change port in docker-compose.yml
ports:
  - "7688:7687"  # Use different host port
```

**Memory issues:**
```bash
# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory → 4GB+
```

**Database not found:**
```cypher
// List all databases
SHOW DATABASES;

// Create if missing
CREATE DATABASE temporal_kg;
CREATE DATABASE longterm_kg;
```

---

## 📚 Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Cypher Query Language](https://neo4j.com/developer/cypher/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Graph Data Science](https://neo4j.com/docs/graph-data-science/current/)

---

## ✅ Verification Checklist

- [ ] Neo4j container is running
- [ ] Can access http://localhost:7474
- [ ] Both databases created (temporal_kg, longterm_kg)
- [ ] Python driver installed: `pip install neo4j>=5.14.0`
- [ ] Connection test passes
- [ ] Config.py updated with `enabled: True`
