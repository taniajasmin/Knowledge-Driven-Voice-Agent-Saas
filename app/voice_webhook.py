# import os
# import requests
# from fastapi import Request
# from twilio.twiml.voice_response import VoiceResponse
# from fastapi.responses import Response

# from app.transcript_store import add_line
# from dotenv import load_dotenv
# from app.rag_answer import generate_answer

# load_dotenv()

# BASE_URL = os.getenv("BASE_URL")

# REPORT_PATH = "reports/current_report.txt"
# SCRIPT_PATH = "reports/current_script.txt"


# def get_greeting():
#     with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
#         script = f.read()

#     return script.split("GREETING:")[1].split("TONE:")[0].strip()


# async def voice_entry(request: Request):
#     vr = VoiceResponse()

#     greeting_line = get_greeting()
#     vr.say(greeting_line)

#     vr.gather(
#         input="speech",
#         action="/voice-process",
#         speechTimeout="auto"
#     )

#     # return str(vr)
#     return Response(content=str(vr), media_type="text/xml")



# async def voice_process(request: Request):
#     form = await request.form()

#     user_speech = form.get("SpeechResult")
#     call_id = form.get("CallSid")

#     add_line(call_id, "User", user_speech)

#     # Call RAG endpoint
#     # response = requests.post(
#     #     f"{BASE_URL}/ask/",
#     #     json={"question": user_speech}
#     # )

#     # ai_answer = response.json().get("answer")
#     ai_answer = generate_answer(
#         user_speech,
#         "reports/current_report.txt",
#         "reports/current_script.txt"
#     )


#     add_line(call_id, "AI", ai_answer)

#     vr = VoiceResponse()
#     vr.say(ai_answer)

#     vr.gather(
#         input="speech",
#         action="/voice-process",
#         speechTimeout="auto"
#     )

#     # return str(vr)
#     return Response(content=str(vr), media_type="text/xml")


import os
from fastapi import Request
from twilio.twiml.voice_response import VoiceResponse
from fastapi.responses import Response

from app.transcript_store import add_line
from app.rag_answer import generate_answer

#for error log
import traceback
from fastapi import Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse


REPORT_PATH = "reports/current_report.txt"
SCRIPT_PATH = "reports/current_script.txt"


def get_greeting():
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        script = f.read()

    return script.split("GREETING:")[1].split("TONE:")[0].strip()


# -------------------- ENTRY --------------------

async def voice_entry(request: Request):

    vr = VoiceResponse()

    try:
        greeting_line = get_greeting()
        vr.say(greeting_line)

    except Exception as e:
        print("\n=== VOICE ENTRY ERROR ===")
        traceback.print_exc()
        vr.say("System initialization error.")

    vr.gather(
        input="speech",
        action="/voice-process",
        speechTimeout="auto"
    )

    return Response(content=str(vr), media_type="text/xml")



# -------------------- PROCESS --------------------

# async def voice_process(request: Request):
#     form = await request.form()

#     user_speech = form.get("SpeechResult", "").strip()
#     call_id = form.get("CallSid")

#     vr = VoiceResponse()

#     # If user said nothing (silence / noise / timeout)
#     if not user_speech:
#         vr.say("I did not catch that. Could you please repeat?")
#         vr.gather(
#             input="speech",
#             action="/voice-process",
#             speechTimeout="auto"
#         )
#         return Response(content=str(vr), media_type="text/xml")

#     # Save user line
#     add_line(call_id, "User", user_speech)

#     # Get AI answer directly from RAG
#     ai_answer = generate_answer(
#         user_speech,
#         REPORT_PATH,
#         SCRIPT_PATH
#     )

#     # Save AI line
#     add_line(call_id, "AI", ai_answer)

#     # Speak answer
#     vr.say(ai_answer)

#     # VERY IMPORTANT — continue the conversation
#     vr.gather(
#         input="speech",
#         action="/voice-process",
#         speechTimeout="auto"
#     )

#     return Response(content=str(vr), media_type="text/xml")


async def voice_process(request: Request):

    vr = VoiceResponse()

    try:
        form = await request.form()

        print("\n--- Incoming Twilio Form ---")
        print(dict(form))

        user_speech = (form.get("SpeechResult") or "").strip()
        call_id = form.get("CallSid") or "unknown_call"

        if not user_speech:
            vr.say("I did not catch that. Please repeat.")
            vr.gather(
                input="speech",
                action="/voice-process",
                speechTimeout="auto"
            )
            return Response(content=str(vr), media_type="text/xml")

        print("User said:", user_speech)

        add_line(call_id, "User", user_speech)

        print("Calling RAG...")

        ai_answer = generate_answer(
            user_speech,
            REPORT_PATH,
            SCRIPT_PATH
        )

        print("AI Answer:", ai_answer)

        add_line(call_id, "AI", ai_answer)

        vr.say(ai_answer)

    except Exception:
        print("\n=== VOICE PROCESS CRASH ===")
        traceback.print_exc()

        vr.say("Sorry, a system error occurred.")

    vr.gather(
        input="speech",
        action="/voice-process",
        speechTimeout="auto"
    )

    return Response(content=str(vr), media_type="text/xml")
