# ARGUS Example Arguments
# Test cases covering different argument types and complexity levels

examples = {
    
    # Simple Predictive Arguments
    "ai_doctors": {
        "input": "AI will replace doctors",
        "expected_claims": [
            "Diagnosis can be automated",
            "Human medical judgment is reducible to algorithms",
            "Patients will trust AI doctors",
            "Medical licensing will allow AI practitioners"
        ],
        "expected_claim_types": ["empirical", "empirical", "empirical", "normative"],
        "stance": "dialectic",
        "persona": "academic"
    },
    
    # Philosophical Arguments
    "free_will": {
        "input": "Free will doesn't exist because all actions are predetermined by prior causes",
        "expected_claims": [
            "All actions have prior causes",
            "Prior causation eliminates choice",
            "Determinism is true"
        ],
        "expected_fallacies": ["circular_reasoning"],  # Assumes determinism to prove it
        "stance": "attack",
        "persona": "academic"
    },
    
    # Policy Arguments
    "crypto_ban": {
        "input": """Nigeria should ban cryptocurrency because:
        1. It facilitates money laundering
        2. It undermines the naira
        3. Most crypto investments are scams
        4. Government can't regulate it""",
        "expected_claims": [
            "Cryptocurrency enables money laundering",
            "Crypto trading weakens national currency",
            "Majority of crypto projects are fraudulent",
            "Cryptocurrency is inherently unregulatable"
        ],
        "expected_claim_types": ["empirical", "causal", "empirical", "empirical"],
        "stance": "dialectic",
        "persona": "economist"
    },
    
    # Scientific Arguments
    "climate_change": {
        "input": "Climate change is primarily caused by human CO2 emissions from fossil fuels",
        "expected_claims": [
            "CO2 emissions have increased due to human activity",
            "Increased CO2 causes global temperature rise",
            "Fossil fuels are the main source of anthropogenic CO2",
            "Human activity is the primary driver vs natural variation"
        ],
        "expected_claim_types": ["empirical", "causal", "empirical", "empirical"],
        "stance": "attack",
        "persona": "academic"
    },
    
    # Normative Arguments
    "universal_healthcare": {
        "input": "Healthcare is a human right and should be provided free by the government",
        "expected_claims": [
            "Healthcare meets criteria of human rights",
            "Human rights impose obligations on government",
            "Government-funded healthcare is morally required",
            "Free provision is economically feasible"
        ],
        "expected_claim_types": ["normative", "normative", "normative", "empirical"],
        "stance": "dialectic",
        "persona": "politician"
    },
    
    # Technology Arguments
    "social_media_harm": {
        "input": """Social media causes depression in teenagers through:
        - Constant social comparison
        - Cyberbullying
        - Sleep disruption
        - Dopamine manipulation""",
        "expected_claims": [
            "Social media enables social comparison",
            "Social comparison causes depression",
            "Cyberbullying is prevalent on social platforms",
            "Cyberbullying leads to depression",
            "Social media use disrupts sleep patterns",
            "Sleep disruption causes depression",
            "Social platforms use addictive design",
            "Dopamine manipulation harms mental health"
        ],
        "expected_claim_types": ["empirical", "causal", "empirical", "causal", "empirical", "causal", "empirical", "causal"],
        "stance": "attack",
        "persona": "academic"
    },
    
    # Economic Arguments
    "minimum_wage": {
        "input": "Raising minimum wage will hurt employment because businesses will hire fewer workers",
        "expected_claims": [
            "Minimum wage increase raises labor costs",
            "Higher labor costs reduce hiring",
            "Demand for labor is elastic enough to cause unemployment",
            "Benefits don't offset job losses"
        ],
        "expected_claim_types": ["empirical", "causal", "empirical", "normative"],
        "stance": "dialectic",
        "persona": "economist"
    },
    
    # Conspiracy Theory (Testing Fallacy Detection)
    "moon_landing": {
        "input": """The moon landing was faked because:
        - Flag appears to wave in vacuum
        - No stars visible in photos
        - Shadows aren't parallel
        - Radiation would have killed astronauts""",
        "expected_fallacies": [
            "hasty_generalization",  # Each point has alternative explanations
            "cherry_picking"  # Ignoring overwhelming contrary evidence
        ],
        "expected_low_robustness": True,  # Should score poorly
        "stance": "attack",
        "persona": "reddit_atheist"
    },
    
    # Strawman Example
    "evolution_strawman": {
        "input": "Evolution is false because it claims humans came from monkeys",
        "expected_fallacies": ["strawman"],  # Misrepresents evolutionary theory
        "stance": "attack",
        "persona": "academic"
    },
    
    # Slippery Slope Example
    "slippery_slope": {
        "input": "If we legalize marijuana, soon everyone will be doing heroin",
        "expected_fallacies": ["slippery_slope"],
        "stance": "attack",
        "persona": "reddit_atheist"
    },
    
    # False Dichotomy Example
    "false_dichotomy": {
        "input": "You're either with us or against us in this war",
        "expected_fallacies": ["false_dichotomy"],
        "stance": "attack",
        "persona": "politician"
    },
    
    # Ad Hominem Example
    "ad_hominem": {
        "input": "We shouldn't listen to his economic policy proposals because he's never run a business",
        "expected_fallacies": ["ad_hominem"],
        "stance": "attack",
        "persona": "academic"
    },
    
    # Complex Multi-Layer Argument
    "ai_safety": {
        "input": """We need AI safety regulation now because:
        
        1. AI systems are becoming more powerful
        2. More powerful AI has greater potential for harm
        3. Current safety measures are insufficient
        4. Regulation takes years to implement
        5. By the time harm occurs, it may be too late to regulate
        
        Therefore, we must act preemptively.""",
        "expected_claims": [
            "AI capability is increasing",
            "Greater AI capability increases risk",
            "Current safety protocols are inadequate",
            "Regulatory processes are slow",
            "AI harm could be irreversible",
            "Preemptive action is necessary"
        ],
        "expected_claim_types": ["empirical", "causal", "empirical", "empirical", "predictive", "normative"],
        "stance": "dialectic",
        "persona": "engineer"
    },
    
    # Twitter-Style Hot Take
    "twitter_take": {
        "input": "Working from home is objectively better. If your company forces RTO, they don't care about you. Full stop.",
        "expected_fallacies": [
            "hasty_generalization",
            "false_dichotomy"  # WFH vs RTO as only options
        ],
        "stance": "attack",
        "persona": "twitter"
    },
    
    # Religious Argument
    "religious": {
        "input": "Moral objectivity requires God, because without God, morality is just human opinion",
        "expected_claims": [
            "Objective morality exists",
            "Objective morality requires transcendent foundation",
            "God provides transcendent foundation",
            "Without God, morality is subjective"
        ],
        "expected_claim_types": ["normative", "normative", "normative", "normative"],
        "stance": "dialectic",
        "persona": "religious"
    },
    
    # Corporate Strategy
    "corporate": {
        "input": """We should invest in AI automation because:
        - Reduces operational costs by 30%
        - Scales without additional headcount
        - Competitors are already doing it
        - Shareholders expect innovation""",
        "expected_claims": [
            "AI automation reduces costs by 30%",
            "Cost reduction improves profitability",
            "AI scales without proportional cost increase",
            "Competitors gaining AI advantage",
            "Falling behind competitors hurts business",
            "Shareholders value innovation investment"
        ],
        "expected_claim_types": ["empirical", "causal", "empirical", "empirical", "empirical", "empirical"],
        "stance": "dialectic",
        "persona": "corporate"
    }
}


# Test Cases for Edge Cases
edge_cases = {
    
    "empty_input": {
        "input": "",
        "should_fail": True,
        "error": "Input too short"
    },
    
    "very_short": {
        "input": "Dogs are good",
        "expected_claims": ["Dogs have positive qualities"],
        "expected_claim_types": ["normative"]
    },
    
    "very_long": {
        "input": " ".join(["Claim number " + str(i) for i in range(100)]),
        "should_handle": True,
        "max_claims": 50  # Should intelligently group
    },
    
    "self_contradictory": {
        "input": "AI is both completely safe and extremely dangerous",
        "expected_contradictions": True,
        "expected_fallacies": ["contradiction"]
    },
    
    "tautology": {
        "input": "It will either rain tomorrow or it won't rain tomorrow",
        "expected_fallacies": ["tautology"],
        "expected_low_robustness": True
    }
}


# Dialectic Evolution Examples
# Shows how arguments should improve over rounds
dialectic_examples = {
    
    "ai_jobs": {
        "round_1": {
            "input": "AI will take all our jobs",
            "expected_score": 30  # Weak: overly broad
        },
        "round_2": {
            "strengthened": "AI will automate many routine jobs in next 20 years",
            "expected_score": 55  # Better: qualified
        },
        "round_3": {
            "strengthened": "AI will automate 30-40% of routine cognitive tasks by 2045, primarily affecting data entry, basic analysis, and customer service roles",
            "expected_score": 75  # Strong: specific, qualified, realistic
        }
    }
}


if __name__ == "__main__":
    # Print all example categories
    print("ARGUS Example Arguments\n")
    print(f"Total examples: {len(examples)}")
    print(f"Edge cases: {len(edge_cases)}")
    print(f"Dialectic examples: {len(dialectic_examples)}\n")
    
    print("Categories:")
    categories = {
        "Predictive": ["ai_doctors"],
        "Philosophical": ["free_will"],
        "Policy": ["crypto_ban", "universal_healthcare"],
        "Scientific": ["climate_change"],
        "Technology": ["social_media_harm"],
        "Economic": ["minimum_wage", "corporate"],
        "Fallacy Examples": ["moon_landing", "evolution_strawman", "slippery_slope", 
                             "false_dichotomy", "ad_hominem", "twitter_take"],
        "Complex": ["ai_safety"]
    }
    
    for category, example_names in categories.items():
        print(f"\n{category}:")
        for name in example_names:
            if name in examples:
                print(f"  - {name}: {examples[name]['input'][:60]}...")
