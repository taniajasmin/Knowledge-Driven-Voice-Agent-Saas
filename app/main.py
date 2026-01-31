import os
from fastapi import FastAPI, UploadFile, File
from dotenv import load_dotenv

from app.extractor import extract_text
from app.report_generator import generate_ai_report
from app.script_generator import generate_voice_script

from app.rag_answer import generate_answer
from pydantic import BaseModel


load_dotenv()

app = FastAPI()

# @app.post("/upload-doc/")
# async def upload_doc(file: UploadFile = File(...)):
#     os.makedirs("uploads", exist_ok=True)
#     os.makedirs("reports", exist_ok=True)

#     file_path = f"uploads/{file.filename}"

#     with open(file_path, "wb") as f:
#         f.write(await file.read())

#     # raw_text = extract_text(file_path)
#     try:
#         raw_text = extract_text(file_path)
#     except ValueError as e:
#         return {"error": str(e)}

#     report = generate_ai_report(raw_text)

#     report_path = f"reports/{file.filename}.txt"
#     with open(report_path, "w", encoding="utf-8") as f:
#         f.write(report)

#     return {"message": "Report generated", "report_file": report_path}

from app.script_generator import generate_voice_script

@app.post("/upload-doc/")
async def upload_doc(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        raw_text = extract_text(file_path)
    except ValueError as e:
        return {"error": str(e)}

    # -------- Step 1: Generate AI Knowledge Report --------
    report = generate_ai_report(raw_text)
    report_path = f"reports/{file.filename}_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    # -------- Step 2: Generate Voice Script --------
    script = generate_voice_script(report)
    script_path = f"reports/{file.filename}_script.txt"

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)

    return {
        "message": "Report and Script generated",
        "report_file": report_path,
        "script_file": script_path
    }



class Question(BaseModel):
    question: str
    report_file: str
    script_file: str


@app.post("/ask/")
async def ask_question(data: Question):
    answer = generate_answer(
        data.question,
        data.report_file,
        data.script_file
    )
    return {"answer": answer}