# import os
# from fastapi import FastAPI, UploadFile, File
# from dotenv import load_dotenv

# from app.extractor import extract_text
# from app.report_generator import generate_ai_report
# from app.script_generator import generate_voice_script

# from app.rag_answer import generate_answer
# from pydantic import BaseModel

# from app.script_generator import generate_voice_script
# from app.voice_webhook import voice_entry, voice_process
# from fastapi import Request
# from app.transcript_store import get_transcript, clear_call
# from app.call_logger import save_call_log
# from app.call_summary import generate_summary

# from app.transcript_store import get_transcript

# load_dotenv()

# app = FastAPI()

# @app.post("/upload-doc/")
# async def upload_doc(file: UploadFile = File(...)):
#     os.makedirs("uploads", exist_ok=True)
#     os.makedirs("reports", exist_ok=True)

#     file_path = f"uploads/{file.filename}"

#     with open(file_path, "wb") as f:
#         f.write(await file.read())

#     try:
#         raw_text = extract_text(file_path)
#     except ValueError as e:
#         return {"error": str(e)}

#     # Step 1: Generate AI Knowledge Report
#     report = generate_ai_report(raw_text)
#     report_path = f"reports/{file.filename}_report.txt"

#     with open(report_path, "w", encoding="utf-8") as f:
#         f.write(report)

#     # Step 2: Generate Voice Script
#     script = generate_voice_script(report)
#     script_path = f"reports/{file.filename}_script.txt"

#     with open(script_path, "w", encoding="utf-8") as f:
#         f.write(script)

#     return {
#         "message": "Report and Script generated",
#         "report_file": report_path,
#         "script_file": script_path
#     }



# class Question(BaseModel):
#     question: str
#     report_file: str
#     script_file: str


# @app.post("/ask/")
# async def ask_question(data: Question):
#     answer = generate_answer(
#         data.question,
#         data.report_file,
#         data.script_file
#     )
#     return {"answer": answer}


# @app.post("/voice")
# async def voice(request: Request):
#     return await voice_entry(request)

# @app.post("/voice-process")
# async def voice_process_route(request: Request):
#     return await voice_process(request)


# @app.post("/call-end")
# async def call_end(request: Request):
#     form = await request.form()
#     call_id = form.get("CallSid")

#     transcript = get_transcript(call_id)

#     save_call_log(call_id, transcript)
#     summary = generate_summary(call_id, transcript)

#     clear_call(call_id)

#     return {"status": "saved", "summary": summary}


# # For transcript
# @app.get("/live-transcript/{call_id}")
# async def live_transcript(call_id: str):
#     return {"transcript": get_transcript(call_id)}

import os
from fastapi import FastAPI, UploadFile, File, Request
from dotenv import load_dotenv
from pydantic import BaseModel

from app.extractor import extract_text
from app.report_generator import generate_ai_report
from app.script_generator import generate_voice_script
from app.rag_answer import generate_answer

from app.voice_webhook import voice_entry, voice_process
from app.transcript_store import get_transcript, clear_call
from app.call_logger import save_call_log
from app.call_summary import generate_summary

load_dotenv()

app = FastAPI()


# ------------------ UPLOAD DOC ------------------

@app.post("/upload-doc/")
async def upload_doc(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    raw_text = extract_text(file_path)

    # Generate report
    report = generate_ai_report(raw_text)

    # Generate script
    script = generate_voice_script(report)

    # Save versioned (optional history)
    with open(f"reports/{file.filename}_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    with open(f"reports/{file.filename}_script.txt", "w", encoding="utf-8") as f:
        f.write(script)

    # Save CURRENT (used by voice + ask)
    with open("reports/current_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    with open("reports/current_script.txt", "w", encoding="utf-8") as f:
        f.write(script)

    return {"message": "Report and Script updated for current system"}


# ------------------ ASK (RAG) ------------------

class Question(BaseModel):
    question: str


@app.post("/ask/")
async def ask_question(data: Question):
    answer = generate_answer(
        data.question,
        "reports/current_report.txt",
        "reports/current_script.txt"
    )
    return {"answer": answer}


# ------------------ VOICE ------------------

@app.post("/voice")
async def voice(request: Request):
    return await voice_entry(request)


@app.post("/voice-process")
async def voice_process_route(request: Request):
    return await voice_process(request)


# ------------------ CALL END (save logs + summary) ------------------

@app.post("/call-end")
async def call_end(request: Request):
    form = await request.form()
    call_id = form.get("CallSid")

    transcript = get_transcript(call_id)

    save_call_log(call_id, transcript)
    summary = generate_summary(call_id, transcript)

    clear_call(call_id)

    return {"status": "saved", "summary": summary}


# ------------------ LIVE TRANSCRIPT ------------------

@app.get("/live-transcript/{call_id}")
async def live_transcript(call_id: str):
    return {"transcript": get_transcript(call_id)}
