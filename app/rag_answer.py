# import os
# from openai import OpenAI


# def generate_answer(question: str, report_path: str, script_path: str) -> str:
#     """
#     Uses the AI report (facts) and script (greeting + tone)
#     to answer a user question.
#     """

#     client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#     model = os.getenv("LLM_MODEL")

#     with open(report_path, "r", encoding="utf-8") as f:
#         report_text = f.read()

#     with open(script_path, "r", encoding="utf-8") as f:
#         script_text = f.read()

#     prompt = f"""
# You are an AI assistant answering customer questions.

# Follow this speaking configuration:
# {script_text}

# Answer ONLY using the knowledge below.
# If the answer is not found, say you are not sure.

# Knowledge:
# {report_text}

# Customer Question:
# {question}
# """

#     response = client.chat.completions.create(
#         model=model,
#         messages=[{"role": "user", "content": prompt}]
#     )

#     return response.choices[0].message.content


import os
from openai import OpenAI
from app.retriever import find_relevant_chunk


def generate_answer(question: str, report_path: str, script_path: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("LLM_MODEL")

    with open(report_path, "r", encoding="utf-8") as f:
        report_text = f.read()

    with open(script_path, "r", encoding="utf-8") as f:
        script_text = f.read()

    # REAL RAG STEP
    relevant_chunk = find_relevant_chunk(question, report_text)

    prompt = f"""
Follow this speaking configuration:
{script_text}

Answer ONLY using the knowledge below.

Knowledge:
{relevant_chunk}

Customer Question:
{question}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
