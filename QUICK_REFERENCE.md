# ESPER Email Swarm v2.0 - Quick Reference

## 📦 Installation

```bash
git clone https://github.com/PaniclandUSA/Esper-Email-Swarm.git
cd Esper-Email-Swarm
pip install -e .
```

## 🚀 Common Commands

### Basic Usage
```bash
# Process single email
esper-email --email sample.eml

# With verbose output (show agent packets)
esper-email --email sample.eml --verbose

# With routing explanation
esper-email --email sample.eml --explain

# Export to JSON
esper-email --email sample.eml --json output.json
```

### IMAP Usage
```bash
# Gmail (easiest)
export IMAP_PASSWORD="your_app_password"
esper-email --provider gmail --user you@gmail.com

# Other providers
esper-email --provider outlook --user you@outlook.com
esper-email --provider icloud --user you@icloud.com
esper-email --provider yahoo --user you@yahoo.com

# Custom IMAP
esper-email --imap --host imap.example.com --user you@example.com

# With search criteria
esper-email --provider gmail --user you@gmail.com --search 'UNSEEN'
esper-email --provider gmail --user you@gmail.com --search 'FROM "boss@company.com"'

# Limit results
esper-email --provider gmail --user you@gmail.com --limit 20
```

### Output Formats
```bash
# Pretty (default)
esper-email --email sample.eml

# JSON to stdout
esper-email --email sample.eml --format json

# Minimal (one-line)
esper-email --email sample.eml --format minimal

# Quiet (errors only)
esper-email --email sample.eml --quiet --json output.json
```

### Backward Compatibility
```bash
# Original v1.0 entry point still works
python esper_email_swarm.py --email sample.eml
python esper_email_swarm.py --imap --host imap.gmail.com --user you@gmail.com
```

## 📚 Library Usage

### Basic Processing
```python
from esper_email_swarm import process_email_file

# Process email file
analysis = process_email_file('important.eml')
print(analysis.routing_folder)  # "1-URGENT-NOW"
print(analysis.pretty())  # Terminal output
```

### Process Raw Email
```python
from esper_email_swarm import process_email

with open('email.eml', 'r') as f:
    raw_email = f.read()

analysis = process_email(raw_email)
print(f"Route to: {analysis.routing_folder}")
print(f"Action: {analysis.action}")
```

### Access Analysis Details
```python
from esper_email_swarm import process_email_file

analysis = process_email_file('sample.eml')

# Routing decision
print(analysis.routing_folder)   # "2-Important"
print(analysis.routing_priority) # "high"
print(analysis.routing_color)    # "#FF9500"

# Semantic scores
print(analysis.urgency)      # 0.45
print(analysis.importance)   # 0.72
print(analysis.warmth)       # 0.61
print(analysis.tension)      # 0.12

# Recommendations
print(analysis.icon)   # "⚡⊻≃" (3-glyph signature)
print(analysis.gloss)  # "A warm and important message about research"
print(analysis.topic)  # "Primary topic: research"
print(analysis.action) # "Schedule a meeting or call"

# Metadata
print(analysis.metadata.sender)  # "colleague@university.edu"
print(analysis.metadata.subject) # "Research Collaboration"
```

### Inspect Agent Packets (Auditability)
```python
from esper_email_swarm import process_email_file

analysis = process_email_file('sample.eml')

# All 5 agent packets preserved
for role, packet in analysis.packets.items():
    print(f"{role.upper()} Agent:")
    print(f"  Gloss: {packet.gloss}")
    print(f"  Confidence: {packet.confidence:.2f}")
    print(f"  Urgency: {packet.intent_spine.urgency:.2f}")
```

### Export to JSON
```python
import json
from esper_email_swarm import process_email_file

analysis = process_email_file('sample.eml')

# Full analysis as JSON
data = analysis.to_json_dict()
print(json.dumps(data, indent=2))

# Save to file
with open('analysis.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### Custom Agent Development
```python
from esper_email_swarm.agents import analyze_email_agents
from esper_email_swarm.model import VSEPacket, IntentSpine, AffectLattice, semantic_hash

# Get standard agent packets
packets = analyze_email_agents(email_text, metadata)

# Add custom agent
def my_custom_agent(text: str) -> VSEPacket:
    # Your analysis logic here
    score = calculate_custom_score(text)
    
    return VSEPacket(
        agent_role="custom",
        intent_spine=IntentSpine(urgency=score, confidence=0.8),
        affect_lattice=AffectLattice(),
        semantic_motif=semantic_hash(f"custom:{score}"),
        gloss=f"Custom analysis: {score:.2f}",
        confidence=0.8,
    )

packets['custom'] = my_custom_agent(email_text)
```

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# With coverage
pytest --cov=esper_email_swarm

# Specific test file
pytest tests/test_router.py -v

# Specific test
pytest tests/test_router.py::TestBenevolentFusion::test_benevolence_clamp_activates
```

## 📊 Routing Categories

| Folder | Color | Priority | Criteria |
|--------|-------|----------|----------|
| 1-URGENT-NOW | 🔴 #FF3B30 | critical | urgency > 0.7 |
| 2-Important | 🟠 #FF9500 | high | importance > 0.6 |
| 3-Action-Required | 🟡 #FFCC00 | medium | urgency > 0.4 OR importance > 0.3 |
| 4-Read-Later | 🟢 #34C759 | low | newsletters, bulk mail |
| 5-Reference | ⚪ #8E8E93 | low | archive-worthy |

**Benevolence Clamp**: Personal emails (warmth > 0.6) never go to 5-Reference

## 🔧 Module Reference

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `model.py` | Data structures | VSEPacket, EmailAnalysis, glyph_from_hash() |
| `agents.py` | 5-agent swarm | analyze_email_agents() |
| `router.py` | Routing logic | route_email(), benevolence_clamp() |
| `processor.py` | Email parsing | process_email(), process_email_file() |
| `imap_client.py` | IMAP fetching | IMAPClient, fetch_imap_messages() |
| `cli.py` | CLI interface | main() |

## 📁 File Structure

```
Esper-Email-Swarm/
├── esper_email_swarm/        # Main package
│   ├── __init__.py
│   ├── model.py
│   ├── agents.py
│   ├── router.py
│   ├── processor.py
│   ├── imap_client.py
│   └── cli.py
├── tests/
│   ├── test_router.py
│   └── test_agents.py
├── examples/                 # Sample .eml files
├── esper_email_swarm.py      # Backward-compatible entry
├── pyproject.toml            # Package config
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## 🎯 Agent Roles

| Agent | Analyzes | Returns |
|-------|----------|---------|
| **Urgency** | Deadlines, time pressure | urgency score, gloss |
| **Importance** | Long-term impact domains | importance score, domain, gloss |
| **Topic** | Dominant subject | topic string, gloss |
| **Tone** | Emotional qualities | warmth, tension, formality, gloss |
| **Action** | Required next steps | action recommendation, gloss |

## 💡 Tips & Tricks

### Gmail App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Generate password for "Mail"
3. Use that instead of regular password

### Environment Variables
```bash
export IMAP_PASSWORD="your_password"
# Now you don't need --password flag
esper-email --provider gmail --user you@gmail.com
```

### Multiple Formats at Once
```bash
# Pretty to screen + JSON to file
esper-email --email sample.eml --json output.json
```

### Batch Processing
```bash
# Process all emails in a directory
for file in emails/*.eml; do
    esper-email --email "$file" --quiet --json "results/$(basename "$file" .eml).json"
done
```

### Quick Check Routing
```bash
# Just see where it routes (minimal format)
esper-email --email sample.eml --format minimal
# Output: ⚡⊻≃ [1-URGENT-NOW] Tax documents due Friday
```

## 🐛 Troubleshooting

### IMAP Connection Fails
```bash
# Check host
ping imap.gmail.com

# Check credentials
esper-email --provider gmail --user you@gmail.com --password your_password
# If fails, regenerate app password

# Check firewall
# Port 993 must be open for SSL/TLS
```

### Import Errors
```bash
# Reinstall in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH=/path/to/Esper-Email-Swarm:$PYTHONPATH
```

### Tests Fail
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Clear pytest cache
pytest --cache-clear

# Run with verbose output
pytest -vv
```

## 📞 Get Help

- **GitHub Issues**: https://github.com/PaniclandUSA/Esper-Email-Swarm/issues
- **Documentation**: [README.md](README.md)
- **Examples**: See `examples/` directory
- **Tests**: See `tests/` for usage examples

## 🎓 Learn More

- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md) (if available)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Contributing**: Open an issue or PR

---

**Quick Start in 3 Commands:**
```bash
git clone https://github.com/PaniclandUSA/Esper-Email-Swarm.git
cd Esper-Email-Swarm && pip install -e .
esper-email --email examples/urgent_personal.eml
```

**That's it!** 🚀
