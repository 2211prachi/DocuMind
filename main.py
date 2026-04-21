from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
import shutil
import time

# Services
from services.ingestion import process_pdf
from services.retrieval import retrieve_docs
from services.generation import generate_answer
from services.agent import rewrite_query

app = FastAPI()

# Paths
base_path = Path(__file__).parent
upload_path = base_path / "uploaded_files"
chroma_path = base_path / "chroma_db"

# Create upload folder if not present
upload_path.mkdir(exist_ok=True)

# Simple in-memory chat history
chat_history = []

class QueryRequest(BaseModel):
    question: str
    filename: str = None

@app.get("/")
def home():
    return {"message": "DocuMind API is running"}


# Upload API
@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF files allowed"}

    file_path = upload_path / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages, chunks = process_pdf(str(file_path))

    return {
        "message": "PDF processed successfully",
        "filename": file.filename,
        "pages": pages,
        "chunks": chunks
    }


# TOOL NODE
def tool_node(query: str):
    import datetime

    if "time" in query.lower():
        return f"Current time is {datetime.datetime.now().strftime('%H:%M:%S')}"
    
    if "date" in query.lower():
        return f"Today's date is {datetime.datetime.now().strftime('%Y-%m-%d')}"
    
    return None  


# EVAL NODE
def eval_node(answer: str):
    if len(answer.split()) < 10:
        return 0.5
    return 0.8


# Query API
@app.post("/query")
def ask_question(request: QueryRequest):
    query = request.question
    filename = request.filename

    rewritten_query = rewrite_query(query)

    # ROUTER
    tool_result = tool_node(query)

    if tool_result:
        answer = tool_result
        docs = []
        retrieval_time = 0
    else:
        start = time.time()
        docs = retrieve_docs(rewritten_query, filename)
        retrieval_time = time.time() - start

        if not docs:
            return {
                "answer": f"No content found for document: {filename}",
                "sources": [],
                "explanation": [],
                "confidence": 0,
                "metrics": {
                    "retrieval_time": retrieval_time,
                    "chunks_used": 0
                }
            }

        answer = generate_answer(query, docs, chat_history)

    # EVALUATION
    score = eval_node(answer)

    if score < 0.7 and docs:
        answer = generate_answer(query, docs, chat_history)

    # MEMORY
    chat_history.append({
        "question": query,
        "answer": answer
    })
    chat_history[:] = chat_history[-5:]

    # SOURCES
    sources = [
        {
            "page": doc.metadata.get("page"),
            "file": doc.metadata.get("filename")
        }
        for doc in docs
    ]

    explanation = [
        f"Retrieved from page {doc.metadata.get('page')} of {doc.metadata.get('filename')}"
        for doc in docs
    ]

    return {
        "answer": answer,
        "sources": sources,
        "explanation": explanation,
        "confidence": round(score, 2),
        "metrics": {
            "retrieval_time": retrieval_time,
            "chunks_used": len(docs)
        }
    }
