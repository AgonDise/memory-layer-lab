# ✅ LTM & Neo4j Setup Checklist

**Your Custom Setup Guide**  
**Target:** Connect Memory Layer Lab to your remote Neo4j server and load your data

---

## 📋 PHASE 1: Provide Information (You)

### ✅ Neo4j Server Details

**Provide these details to complete setup:**

```yaml
# Fill this in and share:
neo4j_server:
  host: "___.___.___.___ or hostname"  # Your Neo4j server IP/hostname
  port: 7687                           # Default Bolt port (change if different)
  username: "neo4j"                    # Your Neo4j username
  password: "____________"             # Your Neo4j password
  database: "neo4j"                    # Database name (or custom)
  
# Network info:
network:
  is_local: false                      # true if same machine, false if remote
  vpn_required: false                  # true if needs VPN to access
  ssl_enabled: false                   # true if using SSL/TLS
```

**Example:**
```yaml
neo4j_server:
  host: "192.168.1.100"
  port: 7687
  username: "neo4j"
  password: "my-secret-password"
  database: "memory-layer-lab"
```

---

### ✅ Data Files Location

**Where are your data files?**

```yaml
data_files:
  mid_term:
    path: "path/to/your/mid_term_data.json"
    format: "json"  # json, csv, etc.
    estimated_items: ~100  # Approximate number of chunks
    
  long_term:
    path: "path/to/your/long_term_data.json"
    format: "json"
    estimated_items: ~500  # Approximate number of facts
```

**Data format confirmation:**
- [ ] Mid-term data follows format in `ROADMAP_LTM_INTEGRATION.md` (Section 2.2)
- [ ] Long-term data follows format in `ROADMAP_LTM_INTEGRATION.md` (Section 2.2)
- [ ] Embeddings are included (or will be generated)

---

## 🔧 PHASE 2: Server Setup (You or Server Admin)

### On Neo4j Server:

- [ ] **2.1** Neo4j 5.x installed
  ```bash
  sudo systemctl status neo4j  # Check if running
  neo4j version  # Check version
  ```

- [ ] **2.2** Neo4j configured for remote access
  ```bash
  # Edit /etc/neo4j/neo4j.conf
  server.default_listen_address=0.0.0.0
  server.bolt.enabled=true
  server.bolt.listen_address=0.0.0.0:7687
  ```

- [ ] **2.3** Firewall configured
  ```bash
  sudo ufw allow 7687/tcp  # Allow Bolt
  sudo ufw allow 7474/tcp  # Allow HTTP (optional)
  sudo ufw status
  ```

- [ ] **2.4** Neo4j user credentials set
  ```bash
  sudo neo4j-admin dbms set-initial-password YOUR_PASSWORD
  sudo systemctl restart neo4j
  ```

- [ ] **2.5** Network accessible from dev machine
  ```bash
  # From your dev machine:
  telnet YOUR_SERVER_IP 7687  # Should connect
  ```

**Reference:** See [NEO4J_SETUP_GUIDE.md](NEO4J_SETUP_GUIDE.md) for detailed instructions

---

## 💻 PHASE 3: Development Machine Setup (Me/Automated)

### On Your Development Machine:

- [ ] **3.1** Install Python dependencies
  ```bash
  pip install neo4j pyyaml
  ```

- [ ] **3.2** Create config file
  ```bash
  cp config/neo4j_config.yaml.example config/neo4j_config.yaml
  # Will be auto-filled with your details
  ```

- [ ] **3.3** Test connection
  ```bash
  python3 test_neo4j_connection.py
  # Should show: ✅ ALL TESTS PASSED!
  ```

- [ ] **3.4** Verify data files accessible
  ```bash
  ls -lh YOUR_MTM_FILE.json
  ls -lh YOUR_LTM_FILE.json
  ```

---

## 📊 PHASE 4: Data Loading (Automated)

### Load Your Data:

- [ ] **4.1** Validate data format
  ```bash
  python3 validate_ltm_data.py --file YOUR_MTM_FILE.json
  python3 validate_ltm_data.py --file YOUR_LTM_FILE.json
  ```

- [ ] **4.2** Load mid-term data
  ```bash
  python3 load_ltm_data.py \
    --type mtm \
    --file YOUR_MTM_FILE.json \
    --batch-size 100
  ```

- [ ] **4.3** Load long-term data
  ```bash
  python3 load_ltm_data.py \
    --type ltm \
    --file YOUR_LTM_FILE.json \
    --batch-size 100
  ```

- [ ] **4.4** Create indexes
  ```bash
  python3 load_ltm_data.py --all --create-indexes
  ```

- [ ] **4.5** Verify data loaded
  ```bash
  python3 verify_ltm_data.py
  # Should show count of chunks and facts
  ```

---

## 🧪 PHASE 5: Testing & Integration

### Test LTM Functionality:

- [ ] **5.1** Test LTM queries
  ```bash
  python3 test_ltm_integration.py
  ```

- [ ] **5.2** Test semantic search
  ```bash
  python3 test_ltm_semantic_search.py
  ```

- [ ] **5.3** Test full pipeline (STM + MTM + LTM)
  ```bash
  python3 test_full_pipeline.py
  ```

- [ ] **5.4** Benchmark performance
  ```bash
  python3 benchmark_ltm.py
  # Target: <50ms per query
  ```

- [ ] **5.5** Verify relevance scores
  ```bash
  python3 test_semantic_search.py
  # Target: >70% relevance with all layers
  ```

---

## 📚 PHASE 6: Documentation & Handoff

### Documentation Complete:

- [ ] **6.1** Connection details documented
- [ ] **6.2** Data schema documented
- [ ] **6.3** Query examples created
- [ ] **6.4** Troubleshooting guide updated
- [ ] **6.5** Usage guide finalized

---

## 🎯 SUCCESS CRITERIA

### All Must Pass:

- [ ] ✅ Neo4j connection successful
- [ ] ✅ All data loaded (0 errors)
- [ ] ✅ Indexes created
- [ ] ✅ Queries working (<50ms)
- [ ] ✅ Semantic search functional
- [ ] ✅ Relevance >70%
- [ ] ✅ Full pipeline tested
- [ ] ✅ Documentation complete

---

## 📞 NEXT ACTIONS

### For You to Do Right Now:

1. **Fill in Neo4j server details** (Phase 1)
2. **Confirm Neo4j is running** on server
3. **Share data file locations** (Phase 1)
4. **Confirm network access** (can you ping the server?)

### Provide This Information:

```bash
# Run on your Neo4j server and share output:
sudo systemctl status neo4j
neo4j version
hostname -I  # Get server IP

# Run on your dev machine and share output:
ping YOUR_NEO4J_SERVER_IP  # Test connectivity
```

### Once You Provide Details, I Will:

1. ✅ Create customized `neo4j_config.yaml` with your details
2. ✅ Test connection to your Neo4j server
3. ✅ Validate your data files
4. ✅ Load data to Neo4j
5. ✅ Create indexes for performance
6. ✅ Run full test suite
7. ✅ Generate performance report
8. ✅ Create usage documentation
9. ✅ Provide ready-to-use system

---

## 📋 Quick Command Reference

### After Setup Complete:

```bash
# Check connection
python3 test_neo4j_connection.py

# Load data
python3 load_ltm_data.py --all

# Test LTM
python3 test_ltm_integration.py

# Test full system
python3 test_full_pipeline.py

# Query LTM
python3 -c "from core.long_term import LongTermMemory; ltm = LongTermMemory(); print(ltm.search('AI'))"
```

---

## 🚀 Ready to Start?

**Provide your Neo4j details and I'll set everything up!**

### Template to Fill:

```yaml
# Your Neo4j Server
host: "___.___.___.___ "
port: 7687
username: "neo4j"
password: "____________"
database: "neo4j"

# Your Data Files  
mtm_file: "path/to/mid_term_data.json"
ltm_file: "path/to/long_term_data.json"

# Network
can_ping_server: yes/no
firewall_configured: yes/no
```

**Send this information and I'll complete the setup! 🎉**

---

## 📖 Documentation Index

- **Setup Guide:** [NEO4J_SETUP_GUIDE.md](NEO4J_SETUP_GUIDE.md)
- **Roadmap:** [ROADMAP_LTM_INTEGRATION.md](ROADMAP_LTM_INTEGRATION.md)
- **Quick Start:** [QUICK_START.md](QUICK_START.md)
- **This Checklist:** [LTM_SETUP_CHECKLIST.md](LTM_SETUP_CHECKLIST.md)

---

**Status:** ⏳ Waiting for your Neo4j details  
**Next:** Provide server info → Automated setup begins  
**ETA:** 30 minutes after info provided
