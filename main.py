from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from zoneinfo import ZoneInfo
from datetime import datetime

from schemas import MeetingPayload
from transcript import format_transcript
from agents import start_agent
from email_sender import send_html_email
import warnings

warnings.filterwarnings("ignore", message="Pydantic serializer warnings")

app = FastAPI()

@app.post("/")
def handle_meeting(payload: MeetingPayload):
    transcript = format_transcript(payload.transcript)
    
    duration_minutes = payload.duration
    meeting_date = datetime.fromtimestamp(payload.createdAt, tz=ZoneInfo("Asia/Bangkok"))
    local_meeting_date = meeting_date.strftime("%B %d, %Y at %H:%M")
    
    response = start_agent(transcript, duration_minutes, local_meeting_date)
    
    print(f"DEBUG: response = {response}")
    
    meeting_title = response["meeting_title"]
    
    send_html_email(response["filepath"], "alexander.stoliarchuk@data-science.com.ua", meeting_title)
    
    return {"status": "ok", "result": response["structured_response"]}
