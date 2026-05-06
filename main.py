from dotenv import load_dotenv
load_dotenv()

import os
import threading
import warnings
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException

from agents import start_agent
from email_sender import send_html_email
from schemas import MeetingPayload
from transcript import format_transcript

warnings.filterwarnings("ignore", message="Pydantic serializer warnings")

app = FastAPI()

_processed_meetings: set[str] = set()
_processed_lock = threading.Lock()


@app.get("/")
def root():
    """Health check endpoint. Returns 200 to GET probes so bots don't clutter logs."""
    return {"status": "ok"}


@app.post("/")
def handle_meeting(
    payload: MeetingPayload,
    background_tasks: BackgroundTasks,
    x_webhook_secret: str = Header(None),
):
    expected = os.environ.get("WEBHOOK_SECRET")
    if expected and x_webhook_secret != expected:
        raise HTTPException(status_code=403, detail="Forbidden")

    with _processed_lock:
        if payload.meetingId in _processed_meetings:
            return {"status": "already_processed"}
        _processed_meetings.add(payload.meetingId)

    background_tasks.add_task(process_meeting, payload)
    return {"status": "processing"}


def process_meeting(payload: MeetingPayload):
    """Run the agent and send the analysis email. Runs in background."""
    transcript = format_transcript(payload.transcript)

    duration_minutes = payload.duration
    meeting_date = datetime.fromtimestamp(payload.createdAt, tz=ZoneInfo("Asia/Bangkok"))
    local_meeting_date = meeting_date.strftime("%B %d, %Y at %H:%M")

    response = start_agent(transcript, duration_minutes, local_meeting_date)

    print(f"DEBUG: response keys = {list(response.keys())}")

    meeting_title = response.get("meeting_title")
    filepath = response.get("filepath")

    if not meeting_title or not filepath:
        meeting_type = response.get("meeting_type", "unknown")
        print(f"Skipping email — no analysis produced (meeting_type={meeting_type})")
        return

    send_html_email(filepath, "alexander.stoliarchuk@data-science.com.ua", meeting_title)
    print(f"Email sent for meeting: {meeting_title}")