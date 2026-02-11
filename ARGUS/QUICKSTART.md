# ARGUS Quick Start Guide

## 2-Minute Local Setup

### Option A: Using Script (Easiest)

**Linux/Mac:**
```bash
./run-local.sh
# Script handles everything automatically!
```

**Windows:**
```cmd
run-local.bat
# Script handles everything automatically!
```

### Option B: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install packages
pip install -r requirements.txt

# 3. Set API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"  # Linux/Mac
# or
set ANTHROPIC_API_KEY=sk-ant-your-key-here  # Windows

# 4. Run server
python api.py
# Server starts at http://localhost:8000
```

---

## 2-Minute Cloud Deployment (Railway)

### Easiest Option - Railway.app

**Using Script:**
```bash
./deploy-railway.sh
# Follow on-screen instructions
```

**Manual Steps:**
1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub"
4. Select your repo
5. Add environment variable: `ANTHROPIC_API_KEY`
6. Railway auto-deploys! ✨

**Other Options:** See `DEPLOYMENT.md` for Render, Vercel, Heroku, VPS

### 4. Test It

```bash
# Quick test
curl http://localhost:8000/

# Analyze an argument
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "AI will replace doctors",
    "stance": "dialectic",
    "persona": "academic"
  }'
```

---

## Example Usage

### Python Script

```python
import asyncio
from argus_core import ARGUS, ArgumentStance, Persona

async def main():
    argus = ARGUS()
    
    # Analyze an argument
    result = await argus.analyze_argument(
        input_text="Free will doesn't exist because everything is predetermined",
        stance=ArgumentStance.DIALECTIC,
        persona=Persona.ACADEMIC
    )
    
    # Print results
    print(f"\n🎯 Robustness Score: {result.robustness_score}/100\n")
    
    print(f"📋 Claims Found: {len(result.claims)}")
    for claim in result.claims:
        print(f"  - {claim.text}")
    
    print(f"\n⚔️  Attacks Generated: {len(result.attacks)}")
    for attack in result.attacks[:3]:  # Show first 3
        print(f"  - {attack.counterpoint}")
    
    print(f"\n❌ Fallacies Detected: {len(result.fallacies)}")
    for fallacy in result.fallacies:
        print(f"  - {fallacy.fallacy_type}: {fallacy.explanation}")
    
    print(f"\n✅ Survived: {len(result.survived_claims)}")
    print(f"❌ Collapsed: {len(result.collapsed_claims)}")
    print(f"🟡 Value-dependent: {len(result.value_dependent_claims)}")

asyncio.run(main())
```

### Expected Output

```
🎯 Robustness Score: 42/100

📋 Claims Found: 3
  - Everything is predetermined
  - Predetermined events eliminate choice
  - Free will requires ability to choose otherwise

⚔️  Attacks Generated: 5
  - This assumes hard determinism without proving it
  - Compatibilist definitions of free will allow for both
  - Quantum indeterminacy challenges strict determinism

❌ Fallacies Detected: 1
  - circular_reasoning: Assumes determinism to prove determinism

✅ Survived: 1
❌ Collapsed: 1
🟡 Value-dependent: 1
```

---

## Try Different Modes

### Attack Mode (Devil's Advocate)

```python
result = await argus.analyze_argument(
    "Cryptocurrency is the future of money",
    stance=ArgumentStance.ATTACK,  # Only attacks
    persona=Persona.ECONOMIST
)
```

### Defense Mode (Steelman)

```python
result = await argus.analyze_argument(
    "Working from home is better for everyone",
    stance=ArgumentStance.DEFENSE,  # Only strengthen
    persona=Persona.CORPORATE
)
```

### Dialectic Mode (Full Debate)

```python
result = await argus.analyze_argument(
    "Social media causes depression in teenagers",
    stance=ArgumentStance.DIALECTIC,  # Attack + Defense
    persona=Persona.ACADEMIC
)
```

---

## Try Different Personas

```python
# Academic: Rigorous, evidence-based
persona=Persona.ACADEMIC

# Engineer: Systems thinking, edge cases
persona=Persona.ENGINEER

# Economist: Incentives, trade-offs
persona=Persona.ECONOMIST

# Twitter: Punchy, provocative
persona=Persona.TWITTER

# Reddit Atheist: Skeptical, logical
persona=Persona.REDDIT_ATHEIST
```

---

## Multi-Round Dialectic

Watch arguments evolve over multiple rounds:

```python
history = await argus.dialectic_loop(
    input_text="AI will replace doctors",
    rounds=3,
    persona=Persona.ACADEMIC
)

for i, round_result in enumerate(history, 1):
    print(f"Round {i}: Score = {round_result.robustness_score}")
```

---

## API Usage (Curl)

### Quick Score

```bash
curl -X POST http://localhost:8000/quick-score \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Cryptocurrency will replace banks"}'
```

### Full Analysis

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Climate change is primarily caused by human CO2 emissions",
    "stance": "dialectic",
    "persona": "academic",
    "detect_fallacies": true
  }' | jq
```

### Dialectic

```bash
curl -X POST http://localhost:8000/dialectic \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Universal basic income will solve poverty",
    "rounds": 3,
    "persona": "economist"
  }' | jq
```

---

## Common Issues

### "Module not found"
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### "API key not found"
```bash
# Check environment variable
echo $ANTHROPIC_API_KEY

# Or use .env file
pip install python-dotenv
# Add to code: from dotenv import load_dotenv; load_dotenv()
```

### "Port 8000 already in use"
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn api:app --port 8001
```

---

## Next Steps

1. **Try the examples** in `examples.py`
2. **Read** `ARCHITECTURE.md` for deep dive
3. **Run tests**: `pytest test_argus.py -v`
4. **Deploy** with Docker: `docker-compose up`

---

## Example Arguments to Try

```python
# Philosophy
"Free will doesn't exist"
"Consciousness is an illusion"
"Morality is objective"

# Technology
"AI will replace programmers"
"Blockchain solves trust"
"Social media harms democracy"

# Policy
"Universal healthcare is a right"
"Minimum wage should be $25/hour"
"Nuclear energy is our only option"

# Science
"Evolution is just a theory"
"Vaccines cause autism"  # (Will score very low)
"Climate change is natural"

# Economics
"Trickle-down economics works"
"Cryptocurrency will replace banks"
"Automation will cause mass unemployment"
```

---

## Get Help

- **Documentation:** `README.md`, `ARCHITECTURE.md`
- **Examples:** `examples.py`
- **Tests:** `test_argus.py`
- **Issues:** GitHub Issues

---

**Remember:** ARGUS analyzes **logical structure**, not factual truth. A well-structured argument can still be factually wrong!
