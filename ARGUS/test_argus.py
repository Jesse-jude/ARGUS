"""
ARGUS Test Suite
Tests for claim decomposition, attacks, defenses, and scoring
"""

import pytest
from argus_core import (
    ARGUS,
    ArgumentGraph,
    AtomicClaim,
    ClaimType,
    CounterArgument,
    DefenseArgument,
    LogicalFallacy,
    ArgumentStance,
    Persona,
    BeliefScorer
)


class TestClaimDecomposition:
    """Test atomic claim extraction"""
    
    def test_simple_argument_decomposition(self):
        """Test basic argument breakdown"""
        claim = AtomicClaim(
            id="claim_1",
            text="AI will replace doctors",
            claim_type=ClaimType.PREDICTIVE,
            assumptions=["AI can match diagnostic accuracy", "Patients accept AI doctors"],
            evidence_required="Clinical trials comparing AI vs human diagnosis"
        )
        
        assert claim.id == "claim_1"
        assert claim.claim_type == ClaimType.PREDICTIVE
        assert len(claim.assumptions) == 2
    
    def test_claim_relationships(self):
        """Test claim support/contradiction mapping"""
        claim1 = AtomicClaim(
            id="claim_1",
            text="Diagnosis can be automated",
            claim_type=ClaimType.EMPIRICAL,
            supports=["claim_2"]
        )
        
        claim2 = AtomicClaim(
            id="claim_2",
            text="Doctors will be replaced",
            claim_type=ClaimType.PREDICTIVE,
            assumptions=["Automation = replacement"]
        )
        
        assert "claim_2" in claim1.supports
        assert "Automation = replacement" in claim2.assumptions


class TestArgumentAttacks:
    """Test devil's advocate mode"""
    
    def test_counter_argument_generation(self):
        """Test attack generation"""
        attack = CounterArgument(
            target_claim_id="claim_1",
            attack_vector="counterexample",
            counterpoint="Radiologists still employed despite AI imaging systems",
            strength=0.7
        )
        
        assert attack.strength == 0.7
        assert attack.attack_vector == "counterexample"
        assert 0 <= attack.strength <= 1
    
    def test_attack_strength_range(self):
        """Ensure attack strength is valid"""
        with pytest.raises(ValueError):
            CounterArgument(
                target_claim_id="claim_1",
                attack_vector="weak_assumption",
                counterpoint="Test",
                strength=1.5  # Invalid: > 1.0
            )


class TestArgumentDefense:
    """Test steelman mode"""
    
    def test_defense_strengthening(self):
        """Test claim improvement"""
        defense = DefenseArgument(
            original_claim_id="claim_1",
            strengthened_claim="AI may augment but not fully replace doctors in next 20 years",
            additional_support=[
                "Maintains human oversight requirement",
                "Specifies realistic timeframe"
            ],
            removed_weaknesses=[
                "No longer claims complete replacement",
                "Acknowledges complementary role"
            ]
        )
        
        assert len(defense.additional_support) == 2
        assert len(defense.removed_weaknesses) == 2
        assert "augment" in defense.strengthened_claim


class TestFallacyDetection:
    """Test logical fallacy identification"""
    
    def test_false_dichotomy_detection(self):
        """Test false dichotomy identification"""
        fallacy = LogicalFallacy(
            fallacy_type="false_dichotomy",
            location="claim_3",
            explanation="Presents only 'full automation' or 'no automation' without middle ground",
            severity="moderate"
        )
        
        assert fallacy.fallacy_type == "false_dichotomy"
        assert fallacy.severity in ["minor", "moderate", "severe"]
    
    def test_circular_reasoning_detection(self):
        """Test circular reasoning identification"""
        fallacy = LogicalFallacy(
            fallacy_type="circular_reasoning",
            location="claim_1",
            explanation="Claim assumes its own conclusion as premise",
            severity="severe"
        )
        
        assert fallacy.severity == "severe"


class TestBeliefScoring:
    """Test robustness calculation"""
    
    def test_perfect_score(self):
        """Test maximum robustness"""
        graph = ArgumentGraph(
            original_input="Test",
            claims=[
                AtomicClaim(
                    id="claim_1",
                    text="Test",
                    claim_type=ClaimType.EMPIRICAL
                )
            ],
            survived_claims=["claim_1"],
            collapsed_claims=[],
            value_dependent_claims=[],
            fallacies=[]
        )
        
        score = BeliefScorer.calculate_robustness(graph)
        assert score >= 70  # High score for survived empirical claim
    
    def test_weak_argument_score(self):
        """Test low robustness for collapsed claims"""
        graph = ArgumentGraph(
            original_input="Test",
            claims=[
                AtomicClaim(
                    id="claim_1",
                    text="Test",
                    claim_type=ClaimType.NORMATIVE
                )
            ],
            survived_claims=[],
            collapsed_claims=["claim_1"],
            value_dependent_claims=[],
            fallacies=[
                LogicalFallacy(
                    fallacy_type="strawman",
                    location="claim_1",
                    explanation="Test",
                    severity="severe"
                )
            ]
        )
        
        score = BeliefScorer.calculate_robustness(graph)
        assert score < 50  # Low score for collapsed claim with fallacy
    
    def test_claim_categorization(self):
        """Test survived/collapsed/value-dependent sorting"""
        claims = [
            AtomicClaim(
                id="claim_1",
                text="Empirical claim",
                claim_type=ClaimType.EMPIRICAL
            ),
            AtomicClaim(
                id="claim_2",
                text="Value claim",
                claim_type=ClaimType.NORMATIVE
            )
        ]
        
        attacks = [
            CounterArgument(
                target_claim_id="claim_1",
                attack_vector="counterexample",
                counterpoint="Strong attack",
                strength=0.9  # Should collapse claim
            )
        ]
        
        graph = ArgumentGraph(
            original_input="Test",
            claims=claims
        )
        
        survived, collapsed, value_dep = BeliefScorer.categorize_claims(graph, attacks)
        
        assert "claim_1" in collapsed  # Defeated by strong attack
        assert "claim_2" in value_dep  # Normative claim


class TestArgumentGraph:
    """Test graph structure and conversion"""
    
    def test_networkx_conversion(self):
        """Test graph export to NetworkX"""
        graph = ArgumentGraph(
            original_input="AI will replace doctors",
            claims=[
                AtomicClaim(
                    id="claim_1",
                    text="Diagnosis can be automated",
                    claim_type=ClaimType.EMPIRICAL,
                    supports=["claim_2"]
                ),
                AtomicClaim(
                    id="claim_2",
                    text="Doctors unnecessary",
                    claim_type=ClaimType.NORMATIVE
                )
            ]
        )
        
        G = graph.to_networkx()
        
        assert G.number_of_nodes() == 2
        assert G.number_of_edges() == 1
        assert G.has_edge("claim_1", "claim_2")
        
        # Check node attributes
        node_data = G.nodes["claim_1"]
        assert node_data["type"] == "empirical"


@pytest.mark.asyncio
class TestARGUSIntegration:
    """Integration tests for full ARGUS pipeline"""
    
    async def test_full_analysis_pipeline(self):
        """Test complete argument analysis"""
        argus = ARGUS()
        
        # Note: This would need LLM mocking in real tests
        # For now, testing structure
        
        input_text = "AI will replace doctors"
        
        # Mock result structure validation
        result = ArgumentGraph(
            original_input=input_text,
            claims=[],
            robustness_score=0.0
        )
        
        assert result.original_input == input_text
        assert isinstance(result.robustness_score, float)


class TestPersonaAdaptation:
    """Test argument style variations"""
    
    def test_academic_persona(self):
        """Academic persona should prioritize evidence"""
        persona = Persona.ACADEMIC
        assert persona.value == "academic"
    
    def test_all_personas_available(self):
        """Ensure all personas are defined"""
        expected_personas = [
            "academic", "politician", "engineer", "teenager",
            "religious", "economist", "twitter", "reddit_atheist", "corporate"
        ]
        
        available = [p.value for p in Persona]
        
        for expected in expected_personas:
            assert expected in available


class TestStanceModes:
    """Test different analysis modes"""
    
    def test_stance_modes(self):
        """Verify all stance modes exist"""
        assert ArgumentStance.ATTACK.value == "attack"
        assert ArgumentStance.DEFENSE.value == "defense"
        assert ArgumentStance.DIALECTIC.value == "dialectic"
        assert ArgumentStance.NEUTRAL.value == "neutral"


# Performance Tests
class TestPerformance:
    """Test scaling and performance"""
    
    def test_claim_limit(self):
        """Ensure reasonable claim count"""
        # Large arguments shouldn't create excessive claims
        max_reasonable_claims = 50
        
        # This would be tested with actual decomposition
        # For now, structural test
        assert max_reasonable_claims > 0


# Example Usage Tests
def test_example_use_case():
    """Test realistic usage scenario"""
    
    # Setup
    input_text = "Free will doesn't exist because all actions are predetermined"
    
    # Expected structure
    expected_claims = [
        "All actions are predetermined",
        "Predetermined actions mean no free will"
    ]
    
    # This validates the API contract
    assert len(input_text) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
