---
title: Compliance Audit Environment
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Compliance Audit Environment

An AI training environment for learning regulatory compliance. Agents review company privacy policies and data processing agreements, identify GDPR violations, and suggest fixes.

## What is this?

This is a reinforcement learning environment where AI agents act as compliance officers. Given a company's privacy policy and a set of GDPR-style rules, the agent must:

1. Find which rules are violated
2. Explain why they're violated  
3. Suggest compliant rewrites (for advanced tasks)

Think of it as a gym for training AI to understand data protection regulations.

## Quick Start

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd compliance-audit-env

# Install dependencies
pip install -r server/requirements.txt
```

### Run the Server

```bash
python -m uvicorn server.app:app --host 0.0.0.0 --port 7860
```

The server will start on `http://localhost:7860`. You can check it's running by visiting `http://localhost:7860/health`.

### Use the Environment

```python
from client import EnvClient
from models import ComplianceAction

# Connect to the environment
client = EnvClient(url="ws://localhost:7860/ws")

# Start a new episode
obs = client.reset(task="easy")  # or "medium", "hard"

print(f"Company: {obs.company_name}")
print(f"Document:\n{obs.document_text}\n")

# Make your compliance assessment
action = ComplianceAction(
    violation_ids=["RULE_01", "RULE_03"],
    explanation="The policy doesn't specify data retention periods and lacks opt-out mechanisms.",
    suggested_rewrite=""
)

# Get feedback
obs, reward, done, info = client.step(action)
print(f"Score: {reward:.2f}")
print(f"Feedback: {obs.feedback}")

client.close()
```

## How It Works

### The Rules

The environment includes 8 GDPR-style rules:

- **RULE_01**: Data Retention - Must specify how long data is kept
- **RULE_02**: Third-Party Transparency - Must name all data recipients
- **RULE_03**: Opt-Out Rights - Must provide clear opt-out mechanisms
- **RULE_04**: Purpose Limitation - Can't use data for different purposes
- **RULE_05**: Breach Notification - Must notify users within 72 hours
- **RULE_06**: Cross-Border Transfers - Need safeguards for international transfers
- **RULE_07**: Consent Requirements - Must get explicit, informed consent
- **RULE_08**: Deletion Rights - Users can request data deletion

### The Documents

15 company documents with known violations:
- **5 easy** - Obvious violations (e.g., "we keep data forever")
- **5 medium** - Requires understanding rule categories
- **5 hard** - Violations hidden in legal language

### Difficulty Levels

**Easy**: Straightforward violation detection. Graded on precision and recall (F1 score).

**Medium**: Need to understand rule categories. Get partial credit for identifying the right domain even if you miss the exact rule.

**Hard**: Must both detect violations AND suggest compliant rewrites. Graded 60% on detection, 40% on rewrite quality.

### Scoring

Each episode gives you up to 3 attempts. The environment provides feedback after each attempt so you can improve. Episodes end when:
- You score ≥ 0.85 (excellent performance), or
- You've used all 3 attempts

## Project Structure

```
compliance-audit-env/
├── server/
│   ├── app.py                    # FastAPI server
│   ├── compliance_data.py        # Rules and documents
│   ├── compliance_environment.py # Core environment logic
│   └── requirements.txt          # Server dependencies
├── client.py                     # Client for connecting to the environment
├── models.py                     # Data models (Action, Observation)
├── baseline_inference.py         # Optional: GPT-4o-mini baseline
├── openenv.yaml                  # Environment metadata
├── Dockerfile                    # For containerized deployment
└── requirements.txt              # Client dependencies
```

## Docker Deployment

```bash
# Build the image
docker build -t compliance-audit-env .

# Run the container
docker run -p 7860:7860 compliance-audit-env
```

## Advanced Usage

### Async Client

```python
import asyncio
from client import EnvClient
from models import ComplianceAction

async def run_episode():
    async with EnvClient(url="ws://localhost:7860/ws") as client:
        obs = await client.async_reset(task="medium")
        
        action = ComplianceAction(
            violation_ids=["RULE_02"],
            explanation="Missing third-party disclosure",
            suggested_rewrite=""
        )
        
        obs, reward, done, info = await client.async_step(action)
        print(f"Score: {reward:.2f}")

asyncio.run(run_episode())
```

### Running Baseline (Optional)

If you want to test the environment with GPT-4o-mini:

```bash
export OPENAI_API_KEY="your-key-here"
python baseline_inference.py
```

This will run 3 episodes per difficulty level and output average scores. Expected results:
- Easy: ~0.70
- Medium: ~0.43  
- Hard: ~0.22

## Why This Exists

Training AI to understand regulations is hard. This environment provides:

1. **Structured learning** - Clear rules, graded feedback, multiple difficulty levels
2. **Real-world relevance** - Based on actual GDPR requirements
3. **Immediate feedback** - Agents learn from mistakes within the same episode
4. **Scalable difficulty** - From simple pattern matching to nuanced legal reasoning

## Technical Details

Built on [openenv-core](https://github.com/openenv-ai/openenv-core), a framework for creating RL environments. The server uses FastAPI and communicates via WebSocket. All grading is deterministic - no LLM judges, just rule-based scoring.

## License

MIT License - see LICENSE file for details.

## Contributing

Found a bug? Have an idea? Open an issue or submit a pull request. We're especially interested in:
- Additional compliance rules
- More document examples
- Alternative grading strategies
- Integration with other RL frameworks

## Questions?

Open an issue on GitHub or check the [documentation](link-to-docs).

