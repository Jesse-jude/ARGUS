# ARGUS – Adversarial Reasoning System

ARGUS is a **reasoning system** designed to perform structured adversarial analysis of arguments. Unlike traditional chatbots, ARGUS **doesn’t just respond**—it systematically decomposes, attacks, defends, and evaluates logical structures.

> **Philosophy:** *"Argue with the logic, not the person."*

---

## Features

- Decompose complex arguments into atomic claims
- Generate adversarial counterarguments (Devil’s Advocate)
- Steelman arguments to their strongest form
- Detect logical fallacies automatically
- Evaluate argument robustness (0–100 scale)
- Visualize argument structure as directed graphs
- Multi-round dialectic simulations
- REST API for integration

---

## Architecture Overview

Frontend (React)
└─ Input interface, visualizations, results display
│
▼
FastAPI Backend
└─ Request validation, response formatting, caching
│
▼
ARGUS Core Engine
└─ Claim decomposition, attack generation, defense construction,
fallacy detection, robustness scoring
│
▼
LLM Reasoning Layer
└─ Claude API integration, structured outputs, prompt engineering
│
▼
Data Layer
└─ NetworkX graphs, Redis cache (optional), PostgreSQL (optional)


---

## Core Components

### 1. Claim Decomposer
Breaks arguments into atomic propositions.

```python
Input: "AI will replace doctors"

Output:
- Claim 1: "Diagnosis can be automated" (empirical)
  - Assumptions: ["AI can match human accuracy"]
  - Evidence needed: "Clinical trial comparisons"
```


2. Argument Attacker

Generates adversarial counterarguments with persona adaptation (academic, engineer, economist, social media styles, etc.).

Claim: "AI can replace radiologists"

Academic Attack:
- "Systematic review by Smith et al. (2023) showed AI sensitivity drops 15% on out-of-distribution scans"
- Strength: 0.8


3. Argument Defender

Steelmans arguments by removing strawman interpretations, adding qualifications, and providing evidence.

Original: "AI will replace doctors"

Defended:
"AI will augment diagnostic capabilities in radiology and pathology over next 15-20 years..."

4. Fallacy Detector

Detects common logical errors like:

Strawman, Ad Hominem, False Dichotomy

Circular Reasoning, Appeal to Authority

Slippery Slope, Hasty Generalization, Post Hoc, Tu Quoque, Appeal to Emotion

{
  "fallacy_type": "false_dichotomy",
  "location": "claim_3",
  "explanation": "Presents only 'full automation' or 'no automation' without middle ground",
  "severity": "moderate"
}

5. Belief Scorer

Calculates argument robustness (0–100):

score = (
    (survived_claims / total_claims) * 60 +
    (empirical_claims / total_claims) * 20 -
    (fallacy_penalty) * 20
)

Interpretation:

70–100 → Strong

40–69 → Moderate

0–39 → Weak

API Endpoints
POST /analyze

Analyze argument fully.

Request:

{
  "input_text": "AI will replace doctors",
  "stance": "dialectic",
  "persona": "academic",
  "detect_fallacies": true
}


Response:

{
  "analysis_id": "uuid",
  "timestamp": "2026-...",
  "graph": { /* ArgumentGraph */ },
  "execution_time_ms": 2500.0
}

POST /dialectic

Simulate multi-round debates.

POST /quick-score

Fast robustness check for arguments.

LLM Integration

Claude API with structured outputs (validated with Pydantic)

Different temperatures per task:

Decomposition: 0.3

Attacks: 0.7

Defenses: 0.5

Fallacies: 0.2

response = claude.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": prompt}]
)

Graph Representation

Arguments stored as directed graphs:

G = nx.DiGraph()
G.add_node("claim_1", text="...", type="empirical")
G.add_edge("claim_1", "claim_2", relation="supports")

Deployment
Docker
docker build -t argus .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-ant-... argus

Gunicorn
gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120

Testing

Unit, integration, and performance tests included

Performance target: <5s per analysis

Security

Input validation, content filtering

API key protection with environment variables

Rate limiting

Future Enhancements

Real-time collaboration

Domain-specific templates

Research database integration

Mobile & browser clients

Multi-language support

Tech Stack

Backend: Python, FastAPI

Frontend: React, D3.js

LLM: Claude API

Database & Caching: PostgreSQL (optional), Redis (optional)

Graph Analysis: NetworkX
