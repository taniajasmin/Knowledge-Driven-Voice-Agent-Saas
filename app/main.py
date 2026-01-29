import os
from fastapi import FastAPI, UploadFile, File
from dotenv import load_dotenv

from app.extractor import extract_text
from app.report_generator import generate_ai_report

load_dotenv()

app = FastAPI()

# @app.post("/upload-doc/")
# async def upload_doc(file: UploadFile = File(...)):
#     file_path = f"uploads/{file.filename}"

#     with open(file_path, "wb") as f:
#         f.write(await file.read())

#     raw_text = extract_text(file_path)
#     report = generate_ai_report(raw_text)

#     report_path = f"reports/{file.filename}.txt"
#     with open(report_path, "w", encoding="utf-8") as f:
#         f.write(report)

#     return {"message": "Report generated", "report_file": report_path}

@app.post("/upload-doc/")
async def upload_doc(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # raw_text = extract_text(file_path)
    try:
        raw_text = extract_text(file_path)
    except ValueError as e:
        return {"error": str(e)}

    report = generate_ai_report(raw_text)

    report_path = f"reports/{file.filename}.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    return {"message": "Report generated", "report_file": report_path}