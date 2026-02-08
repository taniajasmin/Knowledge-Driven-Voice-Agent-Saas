import os
from openai import OpenAI
from app.retriever import find_relevant_chunk
from dotenv import load_dotenv

load_dotenv()


def generate_answer(question: str, report_path: str, script_path: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("LLM_MODEL")

    with open(report_path, "r", encoding="utf-8") as f:
        report_text = f.read()

    with open(script_path, "r", encoding="utf-8") as f:
        script_text = f.read()

#     # Retrieve most relevant part of the report
#     relevant_chunk = find_relevant_chunk(question, report_text)

#     prompt = f"""
# You are a customer support voice assistant.

# Follow this greeting and tone exactly:
# {script_text}

# You MUST answer using ONLY the information written in the KNOWLEDGE section.
# Do NOT add explanations.
# Do NOT infer anything.
# Do NOT rephrase meaning.

# If the knowledge does not contain the answer, say:
# "Let me check that for you."

# KNOWLEDGE:
# {relevant_chunk}

# QUESTION:
# {question}
# """

#     response = client.chat.completions.create(
#         model=model,
#         messages=[{"role": "user", "content": prompt}]
#     )

#     return response.choices[0].message.content


    # Retrieve relevant section
    relevant_chunk = find_relevant_chunk(question, report_text)

    # Ask GPT if clarification is needed
    check_prompt = f"""
You are checking if a customer question is ambiguous.

Knowledge:
{relevant_chunk}

Question:
{question}

If the question could refer to multiple different things in the knowledge,
reply ONLY with:
CLARIFY

Otherwise reply ONLY with:
CLEAR
"""

    check = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": check_prompt}]
    ).choices[0].message.content.strip()

    # If ambiguous → ask clarification
    if "CLARIFY" in check:
        clarify_prompt = f"""
Using the knowledge below, ask a short clarification question to the customer.

Knowledge:
{relevant_chunk}

Original Question:
{question}
"""

        clarification = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": clarify_prompt}]
        ).choices[0].message.content

        return clarification

    # Step 3: If clear → answer normally
    answer_prompt = f"""
Follow this greeting and tone:
{script_text}

Answer ONLY using this knowledge:
{relevant_chunk}

Question:
{question}
"""

    answer = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": answer_prompt}]
    ).choices[0].message.content

    return answer