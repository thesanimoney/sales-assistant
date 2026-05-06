from pathlib import Path
from uuid import uuid4
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from schemas import AnalysisReport, MeetingType, TechnicalAnalysisReport
from utils import sales_report_to_html
from utils import technical_report_to_html

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

@tool
def define_meeting_parameters(tool_runtime: ToolRuntime, meeting_type: MeetingType, language: str) -> Command:
    """Define the type of meeting and language based on the transcript."""
    return Command(update={
        "meeting_type": meeting_type,
        "language": language,
        "messages": [
            ToolMessage(
                f"Meeting type defined as {meeting_type.value}, now analyse transcript.",
                tool_call_id=tool_runtime.tool_call_id
            )
        ]
    })

@tool
def save_sales_analysis(
    analysis: AnalysisReport,
    tool_runtime: ToolRuntime,
) -> Command:
    """Save a sales meeting analysis. Use only when meeting_type is 'sales'."""

    meeting_title = analysis.meeting_title
    meeting_id = tool_runtime.state.get("meeting_id", str(uuid4()))
    duration_minutes = tool_runtime.context.duration_minutes
    meeting_date = tool_runtime.context.meeting_date

    filename = f"{meeting_date}_sales_{meeting_id}.html"
    filepath = REPORTS_DIR / filename

    sales_report_to_html(analysis, "sales", meeting_date, duration_minutes, filepath)

    return Command(update={
        "filepath": str(filepath),
        "meeting_title": meeting_title,
        "messages": [
            ToolMessage(
                content=f"Sales analysis saved to {filepath}.",
                tool_call_id=tool_runtime.tool_call_id,
            )
        ]
    })


@tool
def save_technical_analysis(
    analysis: TechnicalAnalysisReport,
    tool_runtime: ToolRuntime,
) -> Command:
    """Save a technical meeting analysis. Use only when meeting_type is 'technical'."""

    meeting_title = analysis.meeting_title
    meeting_id = tool_runtime.state.get("meeting_id", str(uuid4()))
    duration_minutes = tool_runtime.context.duration_minutes
    meeting_date = tool_runtime.context.meeting_date

    filename = f"{meeting_date}_technical_{meeting_id}.html"
    filepath = REPORTS_DIR / filename

    technical_report_to_html(analysis, "technical", meeting_date, duration_minutes, filepath)

    return Command(update={
        "filepath": str(filepath),
        "meeting_title": meeting_title,
        "messages": [
            ToolMessage(
                content=f"Technical analysis saved to {filepath}.",
                tool_call_id=tool_runtime.tool_call_id,
            )
        ]
    })