# 🗄️ Neo4j Remote Setup Guide

**Goal:** Connect Memory Layer Lab to your remote Neo4j server

---

## 📋 Prerequisites

### On Your Neo4j Server:
- [ ] Neo4j 5.x installed and running
- [ ] Port 7687 open (Bolt protocol)
- [ ] Port 7474 open (HTTP - optional, for browser)
- [ ] Neo4j user credentials

### On Your Development Machine:
- [ ] Python 3.8+
- [ ] neo4j Python driver installed

---

## 🚀 STEP 1: Neo4j Server Setup

### 1.1 Install Neo4j (if not already installed)

#### On Ubuntu/Debian:
```bash
# Add Neo4j repository
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list

# Install Neo4j
sudo apt-get update
sudo apt-get install neo4j

# Start Neo4j
sudo systemctl start neo4j
sudo systemctl enable neo4j  # Start on boot
```

#### On macOS:
```bash
# Using Homebrew
brew install neo4j

# Start Neo4j
neo4j start
```

#### Using Docker:
```bash
docker run -d \
    --name neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/your-password \
    neo4j:5.14
```

---

### 1.2 Configure Neo4j for Remote Access

Edit Neo4j config file:
- **Location:** `/etc/neo4j/neo4j.conf` (Linux) or `~/Library/Application Support/Neo4j Desktop/Application/relate-data/dbmss/*/conf/neo4j.conf` (macOS)

**Required Changes:**

```properties
# Allow connections from any IP (be careful in production!)
server.default_listen_address=0.0.0.0

# Or specify your network interface
# server.default_listen_address=192.168.1.100

# Bolt connector (default port 7687)
server.bolt.enabled=true
server.bolt.listen_address=0.0.0.0:7687

# HTTP connector (optional, for browser access)
server.http.enabled=true
server.http.listen_address=0.0.0.0:7474

# HTTPS (optional, recommended for production)
# server.https.enabled=true
# server.https.listen_address=0.0.0.0:7473

# Memory settings (adjust based on your server)
server.memory.heap.initial_size=512m
server.memory.heap.max_size=2G
server.memory.pagecache.size=1G
```

**After editing, restart Neo4j:**
```bash
sudo systemctl restart neo4j  # Linux
# or
neo4j restart  # macOS
```

---

### 1.3 Set Up Firewall Rules

#### Using UFW (Ubuntu):
```bash
# Allow Bolt (7687)
sudo ufw allow 7687/tcp

# Allow HTTP (7474) - optional
sudo ufw allow 7474/tcp

# Check status
sudo ufw status
```

#### Using firewalld (CentOS/RHEL):
```bash
# Allow Bolt
sudo firewall-cmd --permanent --add-port=7687/tcp

# Allow HTTP - optional
sudo firewall-cmd --permanent --add-port=7474/tcp

# Reload
sudo firewall-cmd --reload
```

#### Cloud providers:
- **AWS:** Add inbound rules in Security Group for ports 7687, 7474
- **Google Cloud:** Create firewall rules for ports 7687, 7474
- **Azure:** Add inbound port rules in Network Security Group

---

### 1.4 Set Up Neo4j User

```bash
# Access Neo4j browser
# Open: http://YOUR_SERVER_IP:7474

# Default credentials:
# Username: neo4j
# Password: neo4j

# You'll be prompted to change password on first login
```

**Or via command line:**
```bash
sudo neo4j-admin dbms set-initial-password YOUR_NEW_PASSWORD
```

---

## 🔧 STEP 2: Development Machine Setup

### 2.1 Install Python Dependencies

```bash
cd /Users/innotech/memory-layer-lab

# Install Neo4j driver
pip install neo4j pyyaml
```

---

### 2.2 Configure Connection

Copy the example config:
```bash
cp config/neo4j_config.yaml.example config/neo4j_config.yaml
```

Edit `config/neo4j_config.yaml`:
```yaml
neo4j:
  uri: "bolt://YOUR_NEO4J_SERVER_IP:7687"  # Replace with your server IP
  username: "neo4j"
  password: "YOUR_PASSWORD"                 # Replace with your password
  database: "neo4j"
  
  max_connection_lifetime: 3600
  max_connection_pool_size: 50
  connection_acquisition_timeout: 60
  encrypted: false  # Set true if using SSL
```

**Example configurations:**

#### Local development:
```yaml
uri: "bolt://localhost:7687"
username: "neo4j"
password: "password"
encrypted: false
```

#### Remote server on LAN:
```yaml
uri: "bolt://192.168.1.100:7687"
username: "neo4j"
password: "your-strong-password"
encrypted: false
```

#### Remote server with SSL:
```yaml
uri: "bolt://your-server.com:7687"
username: "neo4j"
password: "your-strong-password"
encrypted: true
```

---

### 2.3 Test Connection

```bash
python3 test_neo4j_connection.py
```

**Expected output:**
```
================================================================================
🚀 NEO4J CONNECTION TEST SUITE
================================================================================

================================================================================
🔌 TESTING NEO4J CONNECTION
================================================================================

📡 Connecting to: bolt://192.168.1.100:7687
👤 Username: neo4j
🗄️  Database: neo4j
✅ Connection successful!

================================================================================
🏥 HEALTH CHECK
================================================================================

📊 Status:
   Connected: ✅ Yes
   URI: bolt://192.168.1.100:7687
   Database: neo4j
   Version: 5.14.0
   Edition: community
   Node count: 0

... (more tests)

================================================================================
📊 TEST SUMMARY
================================================================================

Results: 5/5 tests passed

   ✅ PASS - Connection
   ✅ PASS - Health Check
   ✅ PASS - Simple Query
   ✅ PASS - Write & Read
   ✅ PASS - Indexes

================================================================================
🎉 ALL TESTS PASSED! Neo4j is ready to use!
================================================================================
```

---

## 🔍 STEP 3: Troubleshooting

### Issue 1: Connection Refused

**Error:** `ServiceUnavailable: Connection refused`

**Solutions:**
1. Check Neo4j is running:
   ```bash
   sudo systemctl status neo4j  # Linux
   neo4j status  # macOS
   ```

2. Check firewall allows port 7687:
   ```bash
   sudo ufw status  # Ubuntu
   telnet YOUR_SERVER_IP 7687  # From dev machine
   ```

3. Check Neo4j is listening on correct interface:
   ```bash
   sudo netstat -tlnp | grep 7687
   ```

---

### Issue 2: Authentication Failed

**Error:** `AuthError: The client is unauthorized`

**Solutions:**
1. Verify credentials in `config/neo4j_config.yaml`
2. Reset Neo4j password:
   ```bash
   sudo neo4j-admin dbms set-initial-password NEW_PASSWORD
   sudo systemctl restart neo4j
   ```

---

### Issue 3: Cannot Access from Remote Machine

**Solutions:**
1. Check `server.default_listen_address` in neo4j.conf:
   ```properties
   server.default_listen_address=0.0.0.0
   ```

2. Check firewall on Neo4j server:
   ```bash
   sudo ufw allow from YOUR_DEV_MACHINE_IP to any port 7687
   ```

3. For cloud providers, check Security Groups/Firewall Rules

---

### Issue 4: Slow Connection

**Solutions:**
1. Check network latency:
   ```bash
   ping YOUR_SERVER_IP
   ```

2. Increase timeouts in config:
   ```yaml
   connection_acquisition_timeout: 120
   max_retry_time: 60
   ```

3. Optimize Neo4j memory settings in neo4j.conf

---

## 📊 STEP 4: Load Your Data

Once connection is working, load your data:

```bash
# Load mid-term data
python3 load_ltm_data.py --type mtm --file YOUR_MTM_FILE.json

# Load long-term data
python3 load_ltm_data.py --type ltm --file YOUR_LTM_FILE.json

# Or load both
python3 load_ltm_data.py --all --create-indexes
```

---

## 🔐 STEP 5: Security Best Practices

### For Production:

1. **Use SSL/TLS:**
   ```yaml
   encrypted: true
   uri: "neo4j+s://your-server.com:7687"
   ```

2. **Strong password:**
   - Minimum 12 characters
   - Mix of letters, numbers, symbols

3. **Restrict IP access:**
   ```bash
   # Only allow specific IPs
   sudo ufw allow from 192.168.1.0/24 to any port 7687
   ```

4. **Create separate user for app:**
   ```cypher
   // In Neo4j browser
   CREATE USER memory_layer_app
   SET PASSWORD 'strong-password'
   GRANT ROLE reader TO memory_layer_app;
   GRANT ROLE writer TO memory_layer_app;
   ```

5. **Regular backups:**
   ```bash
   sudo neo4j-admin database dump neo4j --to=/backups/neo4j-$(date +%Y%m%d).dump
   ```

---

## 📈 STEP 6: Monitoring & Maintenance

### Check Neo4j Logs:
```bash
# Linux
sudo tail -f /var/log/neo4j/neo4j.log

# macOS
tail -f ~/Library/Application\ Support/Neo4j\ Desktop/Application/relate-data/dbmss/*/logs/neo4j.log
```

### Monitor Performance:
```cypher
// Query slow queries
CALL dbms.listQueries()
YIELD query, elapsedTimeMillis, status
WHERE elapsedTimeMillis > 1000
RETURN query, elapsedTimeMillis, status;

// Check memory usage
CALL dbms.memory.listPools();
```

### Clean Up:
```cypher
// Delete test data
MATCH (n:TestNode) DELETE n;

// Clear all data (careful!)
MATCH (n) DETACH DELETE n;
```

---

## 🎯 Quick Reference

### Common Commands:

```bash
# Start/Stop Neo4j
sudo systemctl start neo4j
sudo systemctl stop neo4j
sudo systemctl restart neo4j

# Check status
sudo systemctl status neo4j

# View logs
sudo journalctl -u neo4j -f

# Test connection
python3 test_neo4j_connection.py

# Load data
python3 load_ltm_data.py --all
```

### Configuration Files:
- **Neo4j config:** `/etc/neo4j/neo4j.conf`
- **App config:** `config/neo4j_config.yaml`
- **Logs:** `/var/log/neo4j/neo4j.log`

### Default Ports:
- **7687** - Bolt protocol (required)
- **7474** - HTTP (browser access)
- **7473** - HTTPS (if enabled)

---

## 📝 Checklist

- [ ] Neo4j installed and running
- [ ] Port 7687 open in firewall
- [ ] Neo4j configured for remote access
- [ ] User credentials set up
- [ ] Python dependencies installed
- [ ] `config/neo4j_config.yaml` configured
- [ ] Connection test passed
- [ ] Data loaded successfully
- [ ] Security measures in place (for production)
- [ ] Monitoring set up
- [ ] Backups configured (for production)

---

## 🆘 Getting Help

### If you get stuck:

1. **Check logs:**
   ```bash
   sudo tail -100 /var/log/neo4j/neo4j.log
   ```

2. **Test with Neo4j browser:**
   Open `http://YOUR_SERVER_IP:7474`

3. **Verify network:**
   ```bash
   telnet YOUR_SERVER_IP 7687
   ```

4. **Review this guide:** Go through each step carefully

5. **Neo4j documentation:** https://neo4j.com/docs/

---

## ✅ You're Ready!

Once all tests pass, you're ready to use LTM with Neo4j!

**Next steps:**
1. Review [ROADMAP_LTM_INTEGRATION.md](ROADMAP_LTM_INTEGRATION.md)
2. Prepare your data files (MTM and LTM)
3. Run `load_ltm_data.py` to load your data
4. Test with `test_ltm_integration.py`

**Happy coding! 🚀**
