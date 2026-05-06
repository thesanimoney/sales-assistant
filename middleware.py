from langchain.agents.middleware import dynamic_prompt as _dynamic_prompt_decorator, ModelRequest, wrap_model_call, ModelResponse
from pathlib import Path
from langchain_openai import ChatOpenAI
from typing import Callable
from tools import define_meeting_parameters, save_sales_analysis, save_technical_analysis

PROMPTS_DIR = Path("prompts")

INITIAL_PROMPT = """You are an expert call analyst and coach.

As a first step, you need to define the type of meeting and language (Ukrainian/Russian/English) based on the transcript, then call define_meeting_parameters tool to record this decision.

# How to classify the meeting type

Use the following heuristics to decide between SALES and TECHNICAL.

## Signs of a SALES call
1. The conversation centers on a buying decision — someone is evaluating whether to engage, expand, renew, or stop. Keywords: budget, contract, SOW, pricing, ROI, decision-makers, committee, procurement, signing, payment terms.
2. Discovery questions dominate the early call — the seller is uncovering pain, qualifying need, mapping stakeholders, or running a sales methodology (SPIN, MEDDIC, BANT). The buyer is being asked about their problems, not solving them.
3. The agenda flows toward commercial next steps — proposal, demo, follow-up call with leadership, sending a SOW, scheduling a procurement conversation. The output of the call is a step in a sales process, not a build decision.
4. Vendor positioning happens — the seller talks about their company's track record, prior clients, why-us advantages, competitive differentiation, case studies, methodology, or pricing model.
5. At least one participant is clearly in a sales/account role (sales rep, AE, founder doing GTM, account manager) and the conversation has the asymmetric structure of one side selling to the other — even if technical terms come up.

## Signs of a TECHNICAL call
1. The conversation centers on a build decision — the participants are choosing between architectures, libraries, models, frameworks, or implementation approaches. Keywords: architecture, FPS, latency, mAP, accuracy, integration, schema, deployment, calibration, retraining, GPU, threshold, validation protocol.
2. Both sides are problem-solving together — engineers from each side are debating tradeoffs, asking each other for measurements, or proposing alternative technical paths. Nobody is being qualified or "discovered."
3. The conversation assumes shared context that already exists — references to "our last sync", "the model we trained", "the spike from last week", "the existing pipeline" — meaning a working relationship and project are already underway.
4. The agenda flows toward technical commitments — running a benchmark, training a model, doing a calibration spike, integrating an API, validating a hypothesis. The output of the call is engineering work, not a sales step.
5. Specific technical artifacts get discussed in detail — model architectures, datasets, hardware specs, code paths, integration interfaces, quantization strategies, error rates, calibration protocols. Discussion goes beyond capability claims into implementation details and measured numbers.

## Tiebreaker rules for mixed calls
- If the call discusses BOTH commercial and technical topics (common for scoping/discovery calls with technical buyers), classify as **SALES** when the meeting outputs a sales artifact (SOW, proposal, follow-up demo, decision committee). Classify as **TECHNICAL** when the meeting outputs an engineering artifact (benchmark plan, architecture decision, code change, validation protocol).
- If a call discusses pricing and budget AT ALL, lean SALES — technical-only calls between engineers do not negotiate budget.
- If both sides are clearly technical roles (no sales/account person leading) and the relationship is already established, lean TECHNICAL.
- When genuinely 50/50, default to SALES — the sales analyst's framework (SPIN/MEDDIC) is a useful lens even on hybrid calls, while a technical report on a sales call would miss the qualification gaps.

After classification, call define_meeting_parameters with the chosen meeting_type and language."""

DEFAULT_PROMPT = """You are an expert call analyst and coach.

Your job is to analyze call transcripts and deliver structured, actionable intelligence.

Before answering, always define the type of meeting based on the transcript.

For every transcript you receive, produce a report covering:
- Call snapshot (participants, call type, stage, objective)
- Scorecard (communication clarity, goal achievement, listening quality, objection handling, next step quality)
- What went well — specific moments with quotes from the transcript
- What went wrong — missed opportunities, weak handling, avoided topics
- Missed questions that should have been asked and why
- Key insights — what the other party actually communicated, including implied signals
- Recommended next actions ranked by priority
- Follow-up message draft to send within 24 hours

Be direct. Quote the transcript. Think from both sides of the conversation.
Flag immediately if the call objective was not achieved or the outcome is at risk.

Start every report with a one-paragraph TL;DR: call outcome, biggest problem, single most important next action."""

PROMPT_MAP = {
    "sales": PROMPTS_DIR / "sales_prompt.md",
    "technical": PROMPTS_DIR / "technical_prompt.md",
}


@_dynamic_prompt_decorator
def dynamic_prompt(request: ModelRequest) -> str:
    """Generate system prompt based on call type."""
    meeting_type = request.state.get("meeting_type")
    language = request.state.get("language")
    
    
    prompt_path = PROMPT_MAP.get(meeting_type)
    if prompt_path and prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8") + f"""\n### LANGUAGE OF THE FINAL REPORT SHOULD BE IN: {language}"""

    if len(request.messages) < 2:
        return INITIAL_PROMPT

    return DEFAULT_PROMPT + f"\n### LANGUAGE OF THE FINAL SHOULD BE IN: {language}"

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    basic_model = ChatOpenAI(model="gpt-5.4-mini")
    advanced_model = ChatOpenAI(model="gpt-5.4")
    
    if not request.state.get("language"):
        return handler(request.override(model=basic_model))
    
    return handler(request.override(model=advanced_model))


@wrap_model_call
def state_based_tool_selection(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    meeting_type = request.state.get("meeting_type")

    if meeting_type == "sales":
        return handler(request.override(
            tools=[define_meeting_parameters, save_sales_analysis]
        ))
    elif meeting_type == "technical":
        return handler(request.override(
            tools=[define_meeting_parameters, save_technical_analysis]
        ))
    else:
        return handler(request.override(
            tools=[define_meeting_parameters]
        ))