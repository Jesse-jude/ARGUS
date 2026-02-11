"""
ARGUS API — FastAPI Backend
RESTful API for the Universal Argument Engine
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime

from argus_core import (
    ARGUS,
    ArgumentGraph,
    ArgumentStance,
    Persona,
    AtomicClaim,
    LogicalFallacy,
    CounterArgument
)


app = FastAPI(
    title="ARGUS — Universal Argument Engine",
    description="If it can be believed, ARGUS can argue it.",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AnalysisRequest(BaseModel):
    """Request to analyze an argument"""
    input_text: str = Field(..., min_length=10, description="The argument to analyze")
    stance: ArgumentStance = Field(
        default=ArgumentStance.DIALECTIC,
        description="Analysis mode: attack, defense, or dialectic"
    )
    persona: Persona = Field(
        default=Persona.ACADEMIC,
        description="Argument style persona"
    )
    detect_fallacies: bool = Field(
        default=True,
        description="Run fallacy detection"
    )


class DialecticRequest(BaseModel):
    """Request for multi-round dialectic analysis"""
    input_text: str = Field(..., min_length=10)
    rounds: int = Field(default=3, ge=1, le=10)
    persona: Persona = Field(default=Persona.ACADEMIC)


class AnalysisResponse(BaseModel):
    """Response with full argument analysis"""
    analysis_id: str
    timestamp: datetime
    graph: ArgumentGraph
    execution_time_ms: float


class DialecticResponse(BaseModel):
    """Response for dialectic analysis"""
    analysis_id: str
    timestamp: datetime
    rounds: List[ArgumentGraph]
    execution_time_ms: float


class QuickScoreResponse(BaseModel):
    """Quick robustness score without full analysis"""
    input_text: str
    robustness_score: float
    summary: str


# Global ARGUS instance
argus_engine = ARGUS()

# Storage (in production: use Redis/PostgreSQL)
analysis_cache: dict[str, ArgumentGraph] = {}


@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "ARGUS — Universal Argument Engine",
        "status": "operational",
        "version": "1.0.0",
        "tagline": "If it can be believed, ARGUS can argue it."
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_argument(request: AnalysisRequest):
    """
    Main endpoint: Analyze an argument with full decomposition
    
    Returns:
    - Atomic claims
    - Attacks/defenses
    - Fallacy detection
    - Robustness score
    """
    
    try:
        from time import time
        start_time = time()
        
        # Run ARGUS analysis
        graph = await argus_engine.analyze_argument(
            input_text=request.input_text,
            stance=request.stance,
            persona=request.persona,
            detect_fallacies=request.detect_fallacies
        )
        
        execution_time = (time() - start_time) * 1000
        
        # Cache result
        analysis_id = str(uuid.uuid4())
        analysis_cache[analysis_id] = graph
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            timestamp=datetime.now(),
            graph=graph,
            execution_time_ms=execution_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/dialectic", response_model=DialecticResponse)
async def run_dialectic(request: DialecticRequest):
    """
    Run multi-round dialectic analysis
    
    Attack → Defense → Counter-attack cycles
    Shows evolution of argument strength over rounds
    """
    
    try:
        from time import time
        start_time = time()
        
        rounds = await argus_engine.dialectic_loop(
            input_text=request.input_text,
            rounds=request.rounds,
            persona=request.persona
        )
        
        execution_time = (time() - start_time) * 1000
        
        analysis_id = str(uuid.uuid4())
        
        return DialecticResponse(
            analysis_id=analysis_id,
            timestamp=datetime.now(),
            rounds=rounds,
            execution_time_ms=execution_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialectic failed: {str(e)}")


@app.post("/quick-score", response_model=QuickScoreResponse)
async def quick_score(input_text: str):
    """
    Fast robustness check without full analysis
    Useful for real-time feedback
    """
    
    try:
        graph = await argus_engine.analyze_argument(
            input_text=input_text,
            stance=ArgumentStance.ATTACK,
            detect_fallacies=True
        )
        
        # Generate summary
        if graph.robustness_score >= 70:
            summary = "Strong argument — withstands critical analysis"
        elif graph.robustness_score >= 40:
            summary = "Moderate argument — has vulnerabilities"
        else:
            summary = "Weak argument — significant logical issues"
        
        return QuickScoreResponse(
            input_text=input_text,
            robustness_score=graph.robustness_score,
            summary=summary
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")


@app.get("/analysis/{analysis_id}", response_model=ArgumentGraph)
async def get_analysis(analysis_id: str):
    """Retrieve cached analysis by ID"""
    
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_cache[analysis_id]


@app.get("/personas", response_model=List[dict])
async def list_personas():
    """Get all available argument personas"""
    
    return [
        {
            "value": p.value,
            "name": p.value.replace("_", " ").title(),
            "description": get_persona_description(p)
        }
        for p in Persona
    ]


@app.get("/stances", response_model=List[dict])
async def list_stances():
    """Get all available analysis stances"""
    
    return [
        {
            "value": s.value,
            "name": s.value.title(),
            "description": get_stance_description(s)
        }
        for s in ArgumentStance
    ]


def get_persona_description(persona: Persona) -> str:
    """Get human-readable persona description"""
    descriptions = {
        Persona.ACADEMIC: "Rigorous, evidence-based, formal citations",
        Persona.POLITICIAN: "Persuasive, appeals to values and constituency",
        Persona.ENGINEER: "Systems-thinking, first-principles, technical",
        Persona.TEENAGER: "Informal, emotional, relatable examples",
        Persona.RELIGIOUS: "Appeals to scripture, tradition, moral framework",
        Persona.ECONOMIST: "Cost-benefit analysis, incentives, data-driven",
        Persona.TWITTER: "Punchy, provocative, meme-aware",
        Persona.REDDIT_ATHEIST: "Skeptical, logical, anti-authority",
        Persona.CORPORATE: "ROI-focused, stakeholder-aware, diplomatic"
    }
    return descriptions.get(persona, "")


def get_stance_description(stance: ArgumentStance) -> str:
    """Get human-readable stance description"""
    descriptions = {
        ArgumentStance.ATTACK: "Devil's advocate — ruthlessly challenges claims",
        ArgumentStance.DEFENSE: "Steelman — builds strongest version of argument",
        ArgumentStance.DIALECTIC: "Full debate — attack, defense, and synthesis",
        ArgumentStance.NEUTRAL: "Objective analysis without taking sides"
    }
    return descriptions.get(stance, "")


# Example usage
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
