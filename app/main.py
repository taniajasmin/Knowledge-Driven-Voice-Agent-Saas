import os
from fastapi import FastAPI, UploadFile, File, Request
from dotenv import load_dotenv
from pydantic import BaseModel

from app.extractor import extract_text
from app.report_generator import generate_ai_report
from app.script_generator import generate_voice_script
from app.rag_answer import generate_answer

load_dotenv()

app = FastAPI()

# -----------------------------------------------------
# Ensure required folders exist
# -----------------------------------------------------
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)


# =====================================================
# DOCUMENT UPLOAD → REPORT → SCRIPT
# =====================================================

@app.post("/upload-doc/")
async def upload_doc(file: UploadFile = File(...)):
    """
    Upload company knowledge document.
    Generates:
    - AI knowledge report
    - Voice assistant behavior script
    """

    file_path = f"uploads/{file.filename}"

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text from document
    raw_text = extract_text(file_path)

    # Generate structured knowledge report
    report = generate_ai_report(raw_text)

    # Generate greeting + tone script
    script = generate_voice_script(report)

    # Save versioned history (optional)
    with open(f"reports/{file.filename}_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    with open(f"reports/{file.filename}_script.txt", "w", encoding="utf-8") as f:
        f.write(script)

    # Save ACTIVE configuration
    with open("reports/current_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    with open("reports/current_script.txt", "w", encoding="utf-8") as f:
        f.write(script)

    return {"message": "Document processed. AI agent updated."}


# RAG QUESTION ANSWERING 

class Question(BaseModel):
    question: str


@app.post("/ask/")
async def ask_question(data: Question):
    """
    Ask the AI agent a question using current knowledge base.
    """

    answer = generate_answer(
        data.question,
        "reports/current_report.txt",
        "reports/current_script.txt"
    )

    return {"answer": answer}