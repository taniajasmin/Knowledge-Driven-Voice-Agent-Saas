import os
import requests
from fastapi import Request
from twilio.twiml.voice_response import VoiceResponse
from app.transcript_store import add_line, get_transcript, clear_call
from app.call_logger import save_call_log
from app.call_summary import generate_summary


BASE_URL = os.getenv("BASE_URL")


def extract_paths(request: Request):
    """
    Read report and script paths from query parameters
    """
    report_path = request.query_params.get("report")
    script_path = request.query_params.get("script")
    return report_path, script_path


async def voice_entry(request: Request):
    vr = VoiceResponse()

    report_path, script_path = extract_paths(request)

    # Read greeting from script file
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()

    greeting_line = script.split("GREETING:")[1].split("TONE:")[0].strip()

    vr.say(greeting_line)

    # Pass paths forward to next step
    action_url = (
        f"/voice-process?report={report_path}&script={script_path}"
    )

    vr.gather(input="speech", action=action_url, speechTimeout="auto")

    return str(vr)


async def voice_process(request: Request):
    form = await request.form()
    user_speech = form.get("SpeechResult")
    call_id = request.form().get("CallSid")
    add_line(call_id, "User", user_speech)


    report_path, script_path = extract_paths(request)

    response = requests.post(
        f"{BASE_URL}/ask/",
        json={
            "question": user_speech,
            "report_file": report_path,
            "script_file": script_path
        }
    )

    ai_answer = response.json().get("answer", "Let me check that for you.")
    add_line(call_id, "AI", ai_answer)

    vr = VoiceResponse()

    # keep passing paths
    action_url = (
        f"/voice-process?report={report_path}&script={script_path}"
    )

    vr.say(ai_answer)
    vr.gather(input="speech", action=action_url, speechTimeout="auto")

    return str(vr)