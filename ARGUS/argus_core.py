"""
ARGUS Core — Claim Decomposition & Argument Analysis Engine
Handles the atomic breakdown of complex arguments into verifiable claims
"""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum
import networkx as nx
from dataclasses import dataclass


class ClaimType(str, Enum):
    """Types of claims in argument structure"""
    EMPIRICAL = "empirical"  # Testable, fact-based
    NORMATIVE = "normative"  # Value judgment, "should" statements
    CAUSAL = "causal"  # X causes Y
    DEFINITIONAL = "definitional"  # What something means
    PREDICTIVE = "predictive"  # Future-oriented


class ArgumentStance(str, Enum):
    """Reasoning modes for ARGUS"""
    ATTACK = "attack"  # Devil's advocate
    DEFENSE = "defense"  # Steelman
    DIALECTIC = "dialectic"  # Back-and-forth
    NEUTRAL = "neutral"  # Objective analysis


class Persona(str, Enum):
    """Argument delivery styles"""
    ACADEMIC = "academic"
    POLITICIAN = "politician"
    ENGINEER = "engineer"
    TEENAGER = "teenager"
    RELIGIOUS = "religious"
    ECONOMIST = "economist"
    TWITTER = "twitter"
    REDDIT_ATHEIST = "reddit_atheist"
    CORPORATE = "corporate"


class AtomicClaim(BaseModel):
    """Single decomposed claim from an argument"""
    id: str
    text: str
    claim_type: ClaimType
    assumptions: List[str] = Field(default_factory=list)
    evidence_required: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    
    # Graph relationships
    supports: List[str] = Field(default_factory=list)  # IDs of claims this supports
    contradicts: List[str] = Field(default_factory=list)


class LogicalFallacy(BaseModel):
    """Detected logical error"""
    fallacy_type: str
    location: str  # Which claim ID
    explanation: str
    severity: Literal["minor", "moderate", "severe"]


class CounterArgument(BaseModel):
    """Generated attack on a claim"""
    target_claim_id: str
    attack_vector: str  # How we're attacking
    counterpoint: str
    supporting_evidence: Optional[str] = None
    strength: float = Field(ge=0, le=1)


class DefenseArgument(BaseModel):
    """Strengthened version of original claim"""
    original_claim_id: str
    strengthened_claim: str
    additional_support: List[str]
    removed_weaknesses: List[str]


class ArgumentGraph(BaseModel):
    """Complete argument structure as a graph"""
    original_input: str
    claims: List[AtomicClaim]
    fallacies: List[LogicalFallacy] = Field(default_factory=list)
    attacks: List[CounterArgument] = Field(default_factory=list)
    defenses: List[DefenseArgument] = Field(default_factory=list)
    
    # Scoring
    robustness_score: Optional[float] = Field(None, ge=0, le=100)
    survived_claims: List[str] = Field(default_factory=list)
    collapsed_claims: List[str] = Field(default_factory=list)
    value_dependent_claims: List[str] = Field(default_factory=list)

    def to_networkx(self) -> nx.DiGraph:
        """Convert to NetworkX graph for analysis/visualization"""
        G = nx.DiGraph()
        
        for claim in self.claims:
            G.add_node(
                claim.id,
                text=claim.text,
                type=claim.claim_type.value,
                confidence=claim.confidence
            )
            
            # Add support edges
            for supported_id in claim.supports:
                G.add_edge(claim.id, supported_id, relation="supports")
            
            # Add contradiction edges
            for contradicted_id in claim.contradicts:
                G.add_edge(claim.id, contradicted_id, relation="contradicts")
        
        return G


class ArgumentDecomposer:
    """
    Phase 1: Break down complex arguments into atomic claims
    This is the foundation of ARGUS's reasoning capability
    """
    
    DECOMPOSITION_PROMPT = """You are ARGUS, a reasoning system that decomposes arguments into atomic claims.

Given this argument: {input_text}

Break it down into atomic claims following these rules:
1. Each claim should be independently verifiable
2. Identify the TYPE of each claim (empirical, normative, causal, definitional, predictive)
3. Extract hidden ASSUMPTIONS behind each claim
4. Identify what EVIDENCE would be needed to verify each claim
5. Map which claims SUPPORT or CONTRADICT each other

Return a structured breakdown."""

    @staticmethod
    async def decompose(input_text: str) -> List[AtomicClaim]:
        """
        Decompose argument into atomic claims
        In production: this calls an LLM with structured output
        """
        # This is where we'd call Claude/GPT with structured output
        # For now, returning the structure that would be populated
        
        return []  # Populated by LLM call
    
    @staticmethod
    def extract_assumptions(claim: str) -> List[str]:
        """Find implicit assumptions in a claim"""
        ASSUMPTION_PROMPT = f"""What unstated assumptions does this claim rely on?
        
Claim: {claim}

List only the critical hidden assumptions that, if false, would invalidate the claim."""
        
        # LLM call here
        return []


class ArgumentAttacker:
    """
    Phase 2: Generate adversarial arguments against claims
    This is the 'Devil's Advocate' mode
    """
    
    ATTACK_VECTORS = [
        "false_causality",
        "weak_assumption",
        "counterexample",
        "alternative_explanation",
        "missing_evidence",
        "scope_limitation",
        "temporal_invalidity",
        "category_error"
    ]
    
    @staticmethod
    async def generate_attacks(
        claim: AtomicClaim,
        persona: Persona = Persona.ACADEMIC
    ) -> List[CounterArgument]:
        """Generate multiple attack vectors on a claim"""
        
        ATTACK_PROMPT = f"""You are ARGUS in ATTACK mode, arguing as a {persona.value}.

Target claim: {claim.text}
Claim type: {claim.claim_type.value}
Assumptions: {claim.assumptions}

Generate strong counterarguments using these vectors:
- Identify weak assumptions
- Provide counterexamples
- Suggest alternative explanations
- Point out missing evidence
- Highlight scope limitations

Be ruthless but logical. Attack the reasoning, not the person."""
        
        # LLM call returns structured CounterArgument objects
        return []


class ArgumentDefender:
    """
    Phase 3: Steelman the argument
    Strengthen claims by addressing weaknesses
    """
    
    @staticmethod
    async def strengthen_claim(
        claim: AtomicClaim,
        attacks: List[CounterArgument]
    ) -> DefenseArgument:
        """Generate strongest possible version of claim"""
        
        DEFENSE_PROMPT = f"""You are ARGUS in DEFENSE mode.

Original claim: {claim.text}
Attacks received: {[a.counterpoint for a in attacks]}

Create the STRONGEST possible version of this claim by:
1. Removing strawman interpretations
2. Adding necessary qualifications
3. Incorporating valid criticism
4. Providing supporting evidence
5. Clarifying scope and limitations

Make the best case possible, even if you disagree with it."""
        
        # LLM call
        return DefenseArgument(
            original_claim_id=claim.id,
            strengthened_claim="",
            additional_support=[],
            removed_weaknesses=[]
        )


class FallacyDetector:
    """
    Phase 4: Identify logical fallacies
    """
    
    FALLACY_TYPES = {
        "strawman": "Misrepresenting opponent's position",
        "ad_hominem": "Attacking person instead of argument",
        "false_dichotomy": "Presenting only two options when more exist",
        "circular_reasoning": "Conclusion assumed in premises",
        "appeal_to_authority": "Citing authority instead of evidence",
        "slippery_slope": "Assuming chain reaction without justification",
        "hasty_generalization": "Drawing broad conclusion from limited data",
        "post_hoc": "Assuming causation from correlation/sequence",
        "appeal_to_emotion": "Using emotions instead of logic",
        "tu_quoque": "You too / hypocrisy attack"
    }
    
    @staticmethod
    async def detect_fallacies(graph: ArgumentGraph) -> List[LogicalFallacy]:
        """Scan argument graph for logical fallacies"""
        
        DETECTION_PROMPT = f"""Analyze this argument for logical fallacies:

Claims: {[c.text for c in graph.claims]}
Relationships: [support/contradiction graph]

Identify any of these fallacies:
{FallacyDetector.FALLACY_TYPES}

For each fallacy found, explain:
- Where it occurs (which claim)
- Why it's a fallacy
- How severe it is (minor/moderate/severe)"""
        
        # LLM call
        return []


class BeliefScorer:
    """
    Phase 5: Calculate robustness of belief
    """
    
    @staticmethod
    def calculate_robustness(graph: ArgumentGraph) -> float:
        """
        Calculate 0-100 score for argument robustness
        
        Factors:
        - How many claims survived attacks
        - Severity of fallacies detected
        - Strength of supporting evidence
        - Whether claims are fact-based or value-based
        """
        
        if not graph.claims:
            return 0.0
        
        # Weight different factors
        survived_ratio = len(graph.survived_claims) / len(graph.claims)
        
        # Penalty for fallacies
        fallacy_penalty = sum(
            0.1 if f.severity == "minor" else
            0.2 if f.severity == "moderate" else
            0.4
            for f in graph.fallacies
        )
        
        # Bonus for empirical vs normative claims
        empirical_bonus = sum(
            0.1 for c in graph.claims 
            if c.claim_type == ClaimType.EMPIRICAL
        ) / len(graph.claims)
        
        score = (
            (survived_ratio * 60) +  # 60% weight on survival
            (empirical_bonus * 20) -  # 20% bonus for empiricism
            (fallacy_penalty * 20)    # 20% penalty for fallacies
        )
        
        return max(0.0, min(100.0, score))
    
    @staticmethod
    def categorize_claims(
        graph: ArgumentGraph,
        attacks: List[CounterArgument]
    ) -> tuple[List[str], List[str], List[str]]:
        """
        Categorize claims into:
        - Survived (withstood attacks)
        - Collapsed (defeated by attacks)
        - Value-dependent (can't be fact-checked)
        """
        
        survived = []
        collapsed = []
        value_dependent = []
        
        for claim in graph.claims:
            # Check if normative (value-based)
            if claim.claim_type == ClaimType.NORMATIVE:
                value_dependent.append(claim.id)
                continue
            
            # Check attack strength
            claim_attacks = [a for a in attacks if a.target_claim_id == claim.id]
            
            if not claim_attacks:
                survived.append(claim.id)
            else:
                avg_attack_strength = sum(a.strength for a in claim_attacks) / len(claim_attacks)
                
                if avg_attack_strength > 0.7:
                    collapsed.append(claim.id)
                else:
                    survived.append(claim.id)
        
        return survived, collapsed, value_dependent


class ARGUS:
    """
    Main orchestrator for the Universal Argument Engine
    """
    
    def __init__(self):
        self.decomposer = ArgumentDecomposer()
        self.attacker = ArgumentAttacker()
        self.defender = ArgumentDefender()
        self.fallacy_detector = FallacyDetector()
        self.scorer = BeliefScorer()
    
    async def analyze_argument(
        self,
        input_text: str,
        stance: ArgumentStance = ArgumentStance.DIALECTIC,
        persona: Persona = Persona.ACADEMIC,
        detect_fallacies: bool = True
    ) -> ArgumentGraph:
        """
        Complete ARGUS analysis pipeline
        
        Args:
            input_text: The argument to analyze
            stance: ATTACK, DEFENSE, or DIALECTIC mode
            persona: How to style the argument
            detect_fallacies: Whether to run fallacy detection
        
        Returns:
            Complete ArgumentGraph with all analysis
        """
        
        # Phase 1: Decompose into claims
        claims = await self.decomposer.decompose(input_text)
        
        graph = ArgumentGraph(
            original_input=input_text,
            claims=claims
        )
        
        # Phase 2: Generate attacks (if needed)
        attacks = []
        if stance in [ArgumentStance.ATTACK, ArgumentStance.DIALECTIC]:
            for claim in claims:
                claim_attacks = await self.attacker.generate_attacks(claim, persona)
                attacks.extend(claim_attacks)
            
            graph.attacks = attacks
        
        # Phase 3: Generate defenses (if needed)
        defenses = []
        if stance in [ArgumentStance.DEFENSE, ArgumentStance.DIALECTIC]:
            for claim in claims:
                claim_attacks = [a for a in attacks if a.target_claim_id == claim.id]
                defense = await self.defender.strengthen_claim(claim, claim_attacks)
                defenses.append(defense)
            
            graph.defenses = defenses
        
        # Phase 4: Detect fallacies (optional)
        if detect_fallacies:
            fallacies = await self.fallacy_detector.detect_fallacies(graph)
            graph.fallacies = fallacies
        
        # Phase 5: Score robustness
        survived, collapsed, value_dep = self.scorer.categorize_claims(graph, attacks)
        
        graph.survived_claims = survived
        graph.collapsed_claims = collapsed
        graph.value_dependent_claims = value_dep
        graph.robustness_score = self.scorer.calculate_robustness(graph)
        
        return graph
    
    async def dialectic_loop(
        self,
        input_text: str,
        rounds: int = 3,
        persona: Persona = Persona.ACADEMIC
    ) -> List[ArgumentGraph]:
        """
        Run multiple rounds of attack → defense → counter-attack
        
        Returns history of argument evolution
        """
        
        history = []
        current_text = input_text
        
        for round_num in range(rounds):
            # Analyze current state
            graph = await self.analyze_argument(
                current_text,
                stance=ArgumentStance.DIALECTIC,
                persona=persona
            )
            
            history.append(graph)
            
            # Prepare for next round using defended claims
            if graph.defenses:
                current_text = "\n".join([
                    d.strengthened_claim for d in graph.defenses
                ])
        
        return history


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def demo():
        argus = ARGUS()
        
        result = await argus.analyze_argument(
            input_text="AI will replace doctors",
            stance=ArgumentStance.DIALECTIC,
            persona=Persona.ACADEMIC
        )
        
        print(f"Robustness Score: {result.robustness_score}/100")
        print(f"Survived: {len(result.survived_claims)} claims")
        print(f"Collapsed: {len(result.collapsed_claims)} claims")
        print(f"Value-dependent: {len(result.value_dependent_claims)} claims")
    
    # asyncio.run(demo())
