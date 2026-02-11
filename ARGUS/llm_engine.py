"""
ARGUS LLM Integration — Reasoning Engine
Connects to Claude API for structured argument analysis
"""

import os
import json
from typing import List, Optional
from anthropic import Anthropic

from argus_core import (
    AtomicClaim,
    ClaimType,
    CounterArgument,
    DefenseArgument,
    LogicalFallacy,
    Persona,
    ArgumentStance
)


class ClaudeArgumentEngine:
    """
    Wrapper for Claude API with specialized prompting for ARGUS
    Handles all LLM reasoning with structured outputs
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client
        
        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"  # Latest Sonnet
    
    async def decompose_into_claims(self, input_text: str) -> List[AtomicClaim]:
        """
        Phase 1: Decompose argument into atomic claims
        
        This is the foundation of ARGUS — breaking complex arguments
        into independently verifiable propositions
        """
        
        prompt = f"""You are ARGUS, a reasoning system that decomposes arguments into atomic claims.

Input argument:
"{input_text}"

Your task:
1. Break this into ATOMIC CLAIMS — single, independently verifiable propositions
2. For each claim, identify:
   - The claim type (empirical, normative, causal, definitional, predictive)
   - Hidden assumptions the claim relies on
   - What evidence would verify or falsify it
   - Which other claims it supports or contradicts

Rules:
- Each claim should be ONE testable statement
- Extract implicit assumptions that aren't stated
- Don't add claims that aren't in the original argument
- Identify logical dependencies between claims

Return valid JSON with this structure:
{{
  "claims": [
    {{
      "id": "claim_1",
      "text": "The exact claim statement",
      "claim_type": "empirical",
      "assumptions": ["Hidden assumption 1", "Hidden assumption 2"],
      "evidence_required": "What evidence would verify this",
      "supports": [],  // IDs of claims this supports
      "contradicts": []  // IDs of claims this contradicts
    }}
  ]
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.3,  # Lower temp for structured analysis
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parse structured output
        result_text = response.content[0].text
        
        # Extract JSON (handle markdown code blocks)
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        else:
            json_str = result_text
        
        data = json.loads(json_str)
        
        # Convert to AtomicClaim objects
        claims = []
        for claim_data in data["claims"]:
            claims.append(AtomicClaim(
                id=claim_data["id"],
                text=claim_data["text"],
                claim_type=ClaimType(claim_data["claim_type"]),
                assumptions=claim_data.get("assumptions", []),
                evidence_required=claim_data.get("evidence_required"),
                supports=claim_data.get("supports", []),
                contradicts=claim_data.get("contradicts", [])
            ))
        
        return claims
    
    async def generate_attacks(
        self,
        claim: AtomicClaim,
        persona: Persona = Persona.ACADEMIC
    ) -> List[CounterArgument]:
        """
        Phase 2: Generate adversarial arguments (Devil's Advocate mode)
        
        Attack vectors:
        - Weak assumptions
        - Counterexamples
        - Alternative explanations
        - Missing evidence
        - Scope limitations
        """
        
        persona_styles = {
            Persona.ACADEMIC: "Use rigorous logic, cite research methods, question operationalization",
            Persona.ENGINEER: "Think in systems, find edge cases, ask about failure modes",
            Persona.TWITTER: "Be punchy and provocative, use memorable examples",
            Persona.REDDIT_ATHEIST: "Demand evidence, challenge authority, use formal logic",
            Persona.POLITICIAN: "Appeal to constituencies, point out unintended consequences",
            Persona.ECONOMIST: "Focus on incentives, opportunity costs, and unintended effects",
            Persona.TEENAGER: "Use relatable examples, emotional appeals, 'what if' scenarios",
            Persona.RELIGIOUS: "Appeal to moral frameworks, tradition, and spiritual consequences",
            Persona.CORPORATE: "Focus on risks, stakeholders, and ROI impacts"
        }
        
        style_instruction = persona_styles.get(persona, persona_styles[Persona.ACADEMIC])
        
        prompt = f"""You are ARGUS in ATTACK mode, arguing as a {persona.value}.

Target claim: "{claim.text}"
Claim type: {claim.claim_type.value}
Hidden assumptions: {', '.join(claim.assumptions) if claim.assumptions else 'None identified'}

Your style: {style_instruction}

Generate 3-5 STRONG counterarguments using these attack vectors:

1. **Weak Assumptions**: Which assumptions are questionable?
2. **Counterexamples**: What real or hypothetical cases contradict this?
3. **Alternative Explanations**: What else could explain the same observations?
4. **Missing Evidence**: What evidence is claimed but not provided?
5. **Scope Limitations**: Where does this claim break down?

For each attack, rate its strength (0.0 to 1.0).

Return valid JSON:
{{
  "attacks": [
    {{
      "attack_vector": "weak_assumption",
      "counterpoint": "Your specific counterargument here",
      "supporting_evidence": "Optional: evidence for your counterpoint",
      "strength": 0.8
    }}
  ]
}}

Be ruthless but fair. Attack the logic, not the person."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            temperature=0.7,  # Higher temp for creative attacks
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        result_text = response.content[0].text
        
        # Parse JSON
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        else:
            json_str = result_text
        
        data = json.loads(json_str)
        
        # Convert to CounterArgument objects
        attacks = []
        for attack_data in data["attacks"]:
            attacks.append(CounterArgument(
                target_claim_id=claim.id,
                attack_vector=attack_data["attack_vector"],
                counterpoint=attack_data["counterpoint"],
                supporting_evidence=attack_data.get("supporting_evidence"),
                strength=attack_data["strength"]
            ))
        
        return attacks
    
    async def strengthen_claim(
        self,
        claim: AtomicClaim,
        attacks: List[CounterArgument]
    ) -> DefenseArgument:
        """
        Phase 3: Steelman the argument (Defense mode)
        
        Build the strongest possible version by:
        - Removing strawman interpretations
        - Adding necessary qualifications
        - Incorporating valid criticism
        - Providing supporting evidence
        """
        
        attacks_summary = "\n".join([
            f"- {a.attack_vector}: {a.counterpoint} (strength: {a.strength})"
            for a in attacks
        ])
        
        prompt = f"""You are ARGUS in DEFENSE mode.

Original claim: "{claim.text}"

Attacks received:
{attacks_summary}

Your task: Create the STRONGEST possible version of this claim.

Guidelines:
1. **Remove weaknesses**: Fix any valid criticisms from attacks
2. **Add qualifications**: Specify scope, limitations, conditions
3. **Provide evidence**: Add supporting data or reasoning
4. **Clarify terms**: Define ambiguous language
5. **Acknowledge limits**: Be honest about what the claim doesn't cover

Important: You're creating the best POSSIBLE case, even if you personally disagree.
This is about intellectual rigor, not personal belief.

Return valid JSON:
{{
  "strengthened_claim": "The improved claim statement",
  "additional_support": [
    "Supporting point 1",
    "Supporting point 2"
  ],
  "removed_weaknesses": [
    "How you addressed attack 1",
    "How you addressed attack 2"
  ]
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.5,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        result_text = response.content[0].text
        
        # Parse JSON
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        else:
            json_str = result_text
        
        data = json.loads(json_str)
        
        return DefenseArgument(
            original_claim_id=claim.id,
            strengthened_claim=data["strengthened_claim"],
            additional_support=data["additional_support"],
            removed_weaknesses=data["removed_weaknesses"]
        )
    
    async def detect_fallacies(
        self,
        claims: List[AtomicClaim],
        original_input: str
    ) -> List[LogicalFallacy]:
        """
        Phase 4: Detect logical fallacies
        
        Common fallacies:
        - Strawman, ad hominem, false dichotomy
        - Circular reasoning, appeal to authority
        - Slippery slope, hasty generalization
        - Post hoc, appeal to emotion
        """
        
        claims_text = "\n".join([f"{c.id}: {c.text}" for c in claims])
        
        prompt = f"""You are ARGUS's fallacy detection system.

Original argument:
"{original_input}"

Decomposed claims:
{claims_text}

Analyze for these logical fallacies:

1. **Strawman**: Misrepresenting opponent's position
2. **Ad Hominem**: Attacking person instead of argument
3. **False Dichotomy**: Only two options when more exist
4. **Circular Reasoning**: Conclusion assumed in premises
5. **Appeal to Authority**: Citing authority instead of evidence
6. **Slippery Slope**: Assuming chain reaction without justification
7. **Hasty Generalization**: Broad conclusion from limited data
8. **Post Hoc**: Assuming causation from correlation/sequence
9. **Appeal to Emotion**: Using emotions instead of logic
10. **Tu Quoque**: "You too" / hypocrisy attack

For each fallacy found:
- Identify the EXACT claim (by ID)
- Explain WHY it's a fallacy
- Rate severity: minor, moderate, or severe

Return valid JSON:
{{
  "fallacies": [
    {{
      "fallacy_type": "false_dichotomy",
      "location": "claim_3",
      "explanation": "Why this is a false dichotomy",
      "severity": "moderate"
    }}
  ]
}}

If no fallacies found, return empty array."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2500,
            temperature=0.2,  # Lower temp for precise identification
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        result_text = response.content[0].text
        
        # Parse JSON
        if "```json" in result_text:
            json_str = result_text.split("```json")[1].split("```")[0].strip()
        else:
            json_str = result_text
        
        data = json.loads(json_str)
        
        # Convert to LogicalFallacy objects
        fallacies = []
        for fallacy_data in data.get("fallacies", []):
            fallacies.append(LogicalFallacy(
                fallacy_type=fallacy_data["fallacy_type"],
                location=fallacy_data["location"],
                explanation=fallacy_data["explanation"],
                severity=fallacy_data["severity"]
            ))
        
        return fallacies


# Integration with ARGUS core
def integrate_claude_engine():
    """
    Replace stub methods in argus_core.py with actual Claude calls
    """
    
    engine = ClaudeArgumentEngine()
    
    # Monkey-patch the core methods
    from argus_core import ArgumentDecomposer, ArgumentAttacker, ArgumentDefender, FallacyDetector
    
    ArgumentDecomposer.decompose = staticmethod(engine.decompose_into_claims)
    ArgumentAttacker.generate_attacks = staticmethod(engine.generate_attacks)
    ArgumentDefender.strengthen_claim = staticmethod(engine.strengthen_claim)
    
    # Fallacy detector needs special handling
    async def detect_fallacies_wrapper(graph):
        return await engine.detect_fallacies(graph.claims, graph.original_input)
    
    FallacyDetector.detect_fallacies = staticmethod(detect_fallacies_wrapper)
    
    print("✓ Claude reasoning engine integrated with ARGUS core")


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_decomposition():
        engine = ClaudeArgumentEngine()
        
        claims = await engine.decompose_into_claims(
            "AI will replace doctors because diagnosis can be automated "
            "and patients will trust machines more than humans"
        )
        
        print(f"\nFound {len(claims)} atomic claims:")
        for claim in claims:
            print(f"\n{claim.id}: {claim.text}")
            print(f"  Type: {claim.claim_type.value}")
            print(f"  Assumptions: {claim.assumptions}")
    
    # asyncio.run(test_decomposition())
