# ARGUS Architecture Documentation

## System Overview

ARGUS is a **reasoning system** that performs structured adversarial analysis of arguments. Unlike traditional chatbots, ARGUS doesn't just respond—it systematically decomposes, attacks, defends, and evaluates logical structures.

---

## Core Philosophy

**"Argue with the logic, not the person."**

ARGUS separates:
- **Empirical claims** (verifiable facts)
- **Normative claims** (value judgments)
- **Logical structure** (how claims connect)

This enables:
- Objective analysis of reasoning quality
- Separation of facts from values
- Traceable argument evolution

---

## Architecture Layers

```
┌─────────────────────────────────────────┐
│         Frontend (React)                │
│  - Input interface                      │
│  - Visualization                        │
│  - Results display                      │
└──────────────┬──────────────────────────┘
               │ REST API
┌──────────────▼──────────────────────────┐
│         FastAPI Backend                 │
│  - Request validation                   │
│  - Response formatting                  │
│  - Caching                              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         ARGUS Core Engine               │
│  - Claim decomposition                  │
│  - Attack generation                    │
│  - Defense construction                 │
│  - Fallacy detection                    │
│  - Robustness scoring                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         LLM Reasoning Layer             │
│  - Claude API integration               │
│  - Structured outputs (Pydantic)        │
│  - Prompt engineering                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Data Layer                      │
│  - NetworkX graphs                      │
│  - Redis cache (optional)               │
│  - PostgreSQL storage (optional)        │
└─────────────────────────────────────────┘
```

---

## Key Components

### 1. Claim Decomposer

**Purpose:** Break complex arguments into atomic propositions

**Input:** Raw argument text
**Output:** List of `AtomicClaim` objects

**Process:**
1. Identify discrete statements
2. Classify claim type (empirical/normative/causal/predictive/definitional)
3. Extract hidden assumptions
4. Determine verification requirements
5. Map claim relationships (supports/contradicts)

**Example:**
```python
Input: "AI will replace doctors"

Output:
- Claim 1: "Diagnosis can be automated" (empirical)
  - Assumptions: ["AI can match human accuracy"]
  - Evidence needed: "Clinical trial comparisons"

- Claim 2: "Patients accept AI doctors" (empirical)
  - Assumptions: ["Trust is achievable"]
  - Evidence needed: "Patient surveys"

- Claim 3: "AI doctors will be authorized" (normative)
  - Assumptions: ["Regulations will change"]
  - Evidence needed: "Legal analysis"
```

### 2. Argument Attacker

**Purpose:** Generate adversarial counterarguments (Devil's Advocate)

**Attack Vectors:**
1. **Weak Assumptions** — Identify questionable premises
2. **Counterexamples** — Find cases that contradict claims
3. **Alternative Explanations** — Suggest other causes
4. **Missing Evidence** — Point out unsupported leaps
5. **Scope Limitations** — Show where claims break down

**Persona Adaptation:**
- **Academic:** Rigorous methodology, research citations
- **Engineer:** Edge cases, failure modes, systems thinking
- **Economist:** Incentives, opportunity costs, data
- **Twitter:** Punchy, provocative, memorable
- **Reddit Atheist:** Demand evidence, formal logic

**Example:**
```python
Claim: "AI can replace radiologists"

Academic Attack:
- "Systematic review by Smith et al. (2023) showed AI 
   sensitivity drops 15% on out-of-distribution scans"
- Strength: 0.8

Engineer Attack:
- "What happens when the model encounters edge cases 
   outside training distribution?"
- Strength: 0.7
```

### 3. Argument Defender

**Purpose:** Steelman the argument (strongest possible version)

**Strategies:**
1. Remove strawman interpretations
2. Add necessary qualifications
3. Incorporate valid criticism
4. Provide supporting evidence
5. Clarify ambiguous terms

**Example:**
```python
Original: "AI will replace doctors"

Defended:
"AI will augment diagnostic capabilities in radiology 
and pathology over next 15-20 years, potentially reducing 
need for some specialist roles while creating new 
human-AI collaborative positions. Full replacement 
unlikely due to liability, patient preference, and 
need for complex judgment."

Added support:
- Specifies timeline
- Identifies specific domains
- Acknowledges limitations
- Clarifies "replace" = "augment"
```

### 4. Fallacy Detector

**Purpose:** Identify logical errors

**Detected Fallacies:**
- Strawman
- Ad Hominem
- False Dichotomy
- Circular Reasoning
- Appeal to Authority
- Slippery Slope
- Hasty Generalization
- Post Hoc
- Appeal to Emotion
- Tu Quoque

**Output:**
```python
{
  "fallacy_type": "false_dichotomy",
  "location": "claim_3",
  "explanation": "Presents only 'full automation' or 
                  'no automation' without middle ground",
  "severity": "moderate"
}
```

### 5. Belief Scorer

**Purpose:** Calculate robustness (0-100)

**Formula:**
```python
score = (
    (survived_claims / total_claims) * 60 +     # 60% weight
    (empirical_claims / total_claims) * 20 -    # 20% bonus
    (fallacy_penalty) * 20                       # 20% penalty
)
```

**Interpretation:**
- **70-100**: Strong — withstands critical analysis
- **40-69**: Moderate — has vulnerabilities
- **0-39**: Weak — significant logical issues

**Claim Categorization:**
- **Survived:** Withstood attacks
- **Collapsed:** Defeated by strong counterarguments
- **Value-dependent:** Can't be fact-checked (normative)

---

## Data Models

### AtomicClaim
```python
class AtomicClaim:
    id: str                    # Unique identifier
    text: str                  # Claim statement
    claim_type: ClaimType      # empirical/normative/causal/etc
    assumptions: List[str]     # Hidden assumptions
    evidence_required: str     # What would verify this
    confidence: float          # 0.0 - 1.0
    supports: List[str]        # IDs of supported claims
    contradicts: List[str]     # IDs of contradicted claims
```

### CounterArgument
```python
class CounterArgument:
    target_claim_id: str       # Which claim to attack
    attack_vector: str         # How we're attacking
    counterpoint: str          # The actual counterargument
    supporting_evidence: str   # Evidence for counter
    strength: float            # 0.0 - 1.0
```

### ArgumentGraph
```python
class ArgumentGraph:
    original_input: str
    claims: List[AtomicClaim]
    attacks: List[CounterArgument]
    defenses: List[DefenseArgument]
    fallacies: List[LogicalFallacy]
    robustness_score: float
    survived_claims: List[str]
    collapsed_claims: List[str]
    value_dependent_claims: List[str]
    
    def to_networkx() -> nx.DiGraph
```

---

## API Endpoints

### POST /analyze
Analyze an argument with full decomposition

**Request:**
```json
{
  "input_text": "AI will replace doctors",
  "stance": "dialectic",
  "persona": "academic",
  "detect_fallacies": true
}
```

**Response:**
```json
{
  "analysis_id": "uuid",
  "timestamp": "2024-...",
  "graph": { /* ArgumentGraph */ },
  "execution_time_ms": 2500.0
}
```

### POST /dialectic
Multi-round debate simulation

**Request:**
```json
{
  "input_text": "Free will doesn't exist",
  "rounds": 3,
  "persona": "academic"
}
```

**Response:**
```json
{
  "analysis_id": "uuid",
  "rounds": [
    { /* Round 1 ArgumentGraph */ },
    { /* Round 2 ArgumentGraph */ },
    { /* Round 3 ArgumentGraph */ }
  ]
}
```

### POST /quick-score
Fast robustness check

**Request:**
```json
{
  "input_text": "Crypto is the future"
}
```

**Response:**
```json
{
  "robustness_score": 45.0,
  "summary": "Moderate argument — has vulnerabilities"
}
```

---

## LLM Integration

### Structured Outputs

ARGUS uses **Pydantic models** for structured LLM outputs:

```python
prompt = f"""
Analyze this argument and return ONLY valid JSON:
{{
  "claims": [
    {{
      "id": "claim_1",
      "text": "...",
      "claim_type": "empirical",
      "assumptions": ["..."]
    }}
  ]
}}
"""

response = claude.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": prompt}]
)

# Parse and validate
data = json.loads(response.content[0].text)
claims = [AtomicClaim(**c) for c in data["claims"]]
```

### Temperature Settings

Different temperatures for different tasks:

- **Decomposition:** `temperature=0.3` (structured, consistent)
- **Attacks:** `temperature=0.7` (creative, diverse)
- **Defenses:** `temperature=0.5` (balanced)
- **Fallacies:** `temperature=0.2` (precise identification)

---

## Graph Representation

Arguments are stored as **directed graphs**:

```python
G = nx.DiGraph()

# Nodes = Claims
G.add_node("claim_1", text="...", type="empirical")
G.add_node("claim_2", text="...", type="normative")

# Edges = Relationships
G.add_edge("claim_1", "claim_2", relation="supports")
```

**Analysis Capabilities:**
- Find central claims (betweenness centrality)
- Identify disconnected claims
- Visualize argument structure
- Detect circular reasoning (cycles)

---

## Performance Optimization

### Caching Strategy

```python
# Redis cache for identical inputs
cache_key = hashlib.sha256(input_text.encode()).hexdigest()

if cached := redis.get(cache_key):
    return json.loads(cached)

# Run analysis
result = await argus.analyze(input_text)

# Cache for 1 hour
redis.setex(cache_key, 3600, json.dumps(result))
```

### Batch Processing

For multiple arguments:

```python
# Parallel processing
results = await asyncio.gather(*[
    argus.analyze(arg) for arg in arguments
])
```

---

## Security Considerations

1. **Input Validation**
   - Max length: 10,000 characters
   - Sanitize malicious inputs
   - Rate limiting: 10 requests/minute

2. **API Key Protection**
   - Never expose in client
   - Use environment variables
   - Rotate regularly

3. **Content Filtering**
   - Block harmful content
   - Detect prompt injection attempts

---

## Testing Strategy

### Unit Tests
```python
def test_claim_decomposition():
    claims = decomposer.decompose("AI will replace doctors")
    assert len(claims) >= 2
    assert any(c.claim_type == ClaimType.PREDICTIVE for c in claims)
```

### Integration Tests
```python
async def test_full_pipeline():
    result = await argus.analyze(
        "Free will doesn't exist",
        stance=ArgumentStance.DIALECTIC
    )
    assert 0 <= result.robustness_score <= 100
```

### Performance Tests
```python
def test_response_time():
    start = time.time()
    result = await argus.analyze(long_argument)
    duration = time.time() - start
    assert duration < 5.0  # Under 5 seconds
```

---

## Deployment

### Docker

```bash
docker build -t argus .
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  argus
```

### Production (Gunicorn)

```bash
gunicorn api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Scaling

- **Horizontal:** Multiple API instances behind load balancer
- **Vertical:** Increase workers per instance
- **Caching:** Redis for frequent arguments
- **Queue:** Celery for async processing

---

## Future Enhancements

### Phase 2
- [ ] Real-time collaboration (multiple users)
- [ ] Argument templates by domain
- [ ] Integration with research databases
- [ ] Voice input/output

### Phase 3
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Browser extension
- [ ] Slack/Discord bots

---

## References

- Toulmin's Argument Model
- Informal Logic (Walton et al.)
- Computational Argumentation (Bench-Capon)
- LLM Reasoning (Chain-of-Thought, Tree-of-Thought)

---

**Built with:** Python, FastAPI, Claude, NetworkX, React, D3.js
