from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from transformers import pipeline

app = FastAPI()

# Path to database
chroma_path = Path(__file__).parent / "chroma_db"

# Load embedding model
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load vector database
vectorstore = Chroma(
    persist_directory=str(chroma_path),
    embedding_function=embedding
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Load LLM
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    max_new_tokens=200
)


# Request format
class QueryRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "DocuMind API is running"}


@app.post("/query")
def ask_question(request: QueryRequest):

    query = request.question

    docs = retriever.invoke(query)

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
Answer the question based only on the context below.

Context:
{context}

Question:
{query}

Answer:
"""

    result = generator(prompt)

    return {"answer": result[0]["generated_text"]}