# import os
# from openai import OpenAI
# import numpy as np

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# def chunk_text(text, chunk_size=500):
#     chunks = []
#     for i in range(0, len(text), chunk_size):
#         chunks.append(text[i:i + chunk_size])
#     return chunks


# def embed(texts):
#     response = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=texts
#     )
#     return [r.embedding for r in response.data]


# def cosine_similarity(a, b):
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# def find_relevant_chunk(question: str, report_text: str) -> str:
#     chunks = chunk_text(report_text)

#     chunk_embeddings = embed(chunks)
#     question_embedding = embed([question])[0]

#     scores = [
#         cosine_similarity(question_embedding, emb)
#         for emb in chunk_embeddings
#     ]

#     best_index = int(np.argmax(scores))
#     return chunks[best_index]


import os
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv

load_dotenv()

def chunk_text(text, chunk_size=500):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks


def embed(texts):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [r.embedding for r in response.data]


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def find_relevant_chunk(question: str, report_text: str) -> str:
    chunks = chunk_text(report_text)

    chunk_embeddings = embed(chunks)
    question_embedding = embed([question])[0]

    scores = [
        cosine_similarity(question_embedding, emb)
        for emb in chunk_embeddings
    ]

    best_index = int(np.argmax(scores))
    return chunks[best_index]