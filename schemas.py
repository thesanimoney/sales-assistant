from pydantic import BaseModel, Field
from dataclasses import dataclass
from enum import Enum
from typing import Literal

class TranscriptEntry(BaseModel):
    speaker: str
    text: str

class MeetingPayload(BaseModel):
    attendees: list[str]
    createdAt: int
    duration: float
    meetingId: str
    title: str
    transcript: list[TranscriptEntry]
    type: str
    videoId: str

class MeetingType(str, Enum):
    sales = "sales"
    technical = "technical"
    other = "other"

class CustomAgentState(BaseModel):
    meeting_type: MeetingType
    meeting_title: str
    filepath: str
    language: str

@dataclass
class CustomContext:
    meeting_date: str
    duration_minutes: float
    
class DealStage(str, Enum):
    discovery = "discovery"
    qualification = "qualification"
    demo = "demo"
    negotiation = "negotiation"
    closing = "closing"

class MeddicStatus(str, Enum):
    strong = "strong"
    partial = "partial"
    weak = "weak"
    missing = "missing"

class QuestionType(str, Enum):
    situation = "situation"
    problem = "problem"
    implication = "implication"
    need_payoff = "need_payoff"
    meddic = "meddic"

class ObjectionType(str, Enum):
    product_maturity = "product_maturity"
    price = "price"
    trust = "trust"
    change_management = "change_management"
    competition = "competition"
    budget = "budget"
    stakeholder = "stakeholder"
    other = "other"


# --- Building blocks ---

class Stakeholder(BaseModel):
    name: str
    role: str
    influence_level: str  # "decision_maker" | "influencer" | "user" | "unknown"

class Score(BaseModel):
    score: int = Field(ge=1, le=10)
    comment: str

class Scorecard(BaseModel):
    discovery_depth: Score
    decision_process_clarity: Score
    budget_signals: Score
    competition_awareness: Score
    value_articulation: Score
    next_step_quality: Score
    rapport_and_trust: Score
    listening_ratio: Score
    spin_execution: Score
    overall: Score

class SpinSection(BaseModel):
    score: int = Field(ge=1, le=10)
    questions_asked: list[str]
    efficiency_assessment: str
    critical_gaps: list[str]
    suggested_questions: list[str]

class SpinAnalysis(BaseModel):
    situation: SpinSection
    problem: SpinSection
    implication: SpinSection
    need_payoff: SpinSection
    overall_score: int = Field(ge=1, le=10)
    overall_verdict: str

class MissedQuestion(BaseModel):
    question: str
    type: QuestionType
    why_it_matters: str
    best_moment_to_ask: str

class Objection(BaseModel):
    objection: str
    type: ObjectionType
    how_it_was_handled: str
    how_it_should_have_been_handled: str
    better_language: str


class MeddicPillar(BaseModel):
    status: MeddicStatus
    evidence: str
    gap: str

class MeddicAssessment(BaseModel):
    metrics: MeddicPillar
    economic_buyer: MeddicPillar
    decision_criteria: MeddicPillar
    decision_process: MeddicPillar
    identify_pain: MeddicPillar
    champion: MeddicPillar
    overall_score: int = Field(ge=1, le=10)

class NextAction(BaseModel):
    action: str
    why: str
    do_by: str
    priority: int  # 1 = highest

class FollowUpEmail(BaseModel):
    subject: str
    body: str


# --- Main report schema ---

class DealSnapshot(BaseModel):
    company: str
    stage: DealStage
    stakeholders: list[Stakeholder]
    estimated_deal_size: str
    deal_health_verdict: str

class AnalysisReport(BaseModel):
    # Meta
    meeting_title: str
    participants: list[str]

    # TL;DR
    tldr: str
    deal_health: str
    biggest_problem: str
    most_important_next_action: str

    # Sections
    deal_snapshot: DealSnapshot
    scorecard: Scorecard
    spin_analysis: SpinAnalysis
    missed_questions: list[MissedQuestion]
    objections: list[Objection]
    competitive_intelligence: list[str]
    meddic: MeddicAssessment
    next_actions: list[NextAction]
    follow_up_email: FollowUpEmail
    
        
class MeetingAnalysis(BaseModel):
    meeting_type: MeetingType
    analysis_report: AnalysisReport
    

# --- Reusable score primitive (matches your sales schema pattern) ---
class ScoreItem(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Score 0-10")
    comment: str


# --- Technical call snapshot ---
class TechnicalSnapshot(BaseModel):
    technical_context: str = Field(..., description="What the conversation was about technically")
    objective: str = Field(..., description="The stated goal of the call")
    systems_and_stack: list[str] = Field(..., description="Technologies, platforms, languages, frameworks mentioned")


# --- Technical scorecard ---
class TechnicalScorecard(BaseModel):
    problem_clarity: ScoreItem
    solution_alignment: ScoreItem
    technical_depth: ScoreItem
    requirement_completeness: ScoreItem
    risk_identification: ScoreItem
    next_step_quality: ScoreItem
    overall: ScoreItem


# --- What went well / wrong (structured) ---
class TranscriptMoment(BaseModel):
    """A specific moment from the call with a quote and analysis."""
    moment: str = Field(..., description="What happened, in one sentence")
    quote: str = Field(..., description="Direct quote from the transcript")
    why_it_matters: str = Field(..., description="Engineering-perspective takeaway")


# --- Missed technical questions ---
class MissedTechnicalQuestion(BaseModel):
    question: str
    category: Literal[
        "architecture", "data", "integration", "security",
        "performance", "scale", "deployment", "testing", "other"
    ]
    why_it_matters: str
    best_moment_to_ask: str


# --- Requirements extracted ---
class ExtractedRequirements(BaseModel):
    functional: list[str] = Field(..., description="What the system must do")
    non_functional: list[str] = Field(..., description="Performance, security, availability, etc.")
    constraints: list[str] = Field(..., description="Technical, regulatory, budget, timeline limits")
    assumptions: list[str] = Field(..., description="Things we are taking as true but haven't validated")


# --- Risks ---
class TechnicalRisk(BaseModel):
    risk: str
    severity: Literal["high", "medium", "low"]
    category: Literal[
        "technical_debt", "scope_creep", "unrealistic_expectations",
        "integration", "security", "performance", "team_capacity", "other"
    ]
    evidence: str = Field(..., description="What in the call suggested this risk")
    mitigation: str = Field(..., description="What can be done about it")

# --- Open questions ---
class OpenQuestion(BaseModel):
    question: str
    blocks: str = Field(..., description="What this blocks if unresolved (e.g. 'estimate', 'architecture decision', 'kickoff')")
    owner: str = Field(..., description="Who should answer this — client, us, or both")

# --- Next actions (reusable from sales report; same shape) ---
class TechnicalNextAction(BaseModel):
    action: str
    why: str
    do_by: str
    priority: int = Field(..., ge=1)

# --- Follow-up message ---
class TechnicalFollowUp(BaseModel):
    subject: str
    body: str

# --- The full report ---
class TechnicalAnalysisReport(BaseModel):
    meeting_title: str
    participants: list[str]
    tldr: str = Field(..., description="One paragraph: alignment status, biggest risk, top next action")

    snapshot: TechnicalSnapshot
    scorecard: TechnicalScorecard

    what_went_well: list[TranscriptMoment]
    what_went_wrong: list[TranscriptMoment]
    missed_questions: list[MissedTechnicalQuestion]

    requirements: ExtractedRequirements
    risks: list[TechnicalRisk]
    open_questions: list[OpenQuestion]

    next_actions: list[TechnicalNextAction]
    follow_up_message: TechnicalFollowUp
    

#--- Response schema ---

class Response(BaseModel):
    text_response: str = Field(..., description="Short text response, whether report was successfully generated or not")