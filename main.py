from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
import shutil

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from transformers import pipeline

app = FastAPI()

# Paths
base_path = Path(__file__).parent
upload_path = base_path / "uploaded_files"
chroma_path = base_path / "chroma_db"

# Create upload folder if not present
upload_path.mkdir(exist_ok=True)

# Embedding model
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# LLM
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    max_new_tokens=200
)


class QueryRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "DocuMind API is running"}


@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    # Check file type
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are allowed"}

    # Clear old ChromaDB
    if chroma_path.exists():
        shutil.rmtree(chroma_path)

    # Save uploaded PDF
    file_path = upload_path / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load PDF
    loader = PyPDFLoader(str(file_path))
    documents = loader.load()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(documents)

    # Store in fresh ChromaDB
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=str(chroma_path)
    )

    return {
        "message": "PDF uploaded and processed successfully",
        "filename": file.filename,
        "total_pages": len(documents),
        "total_chunks": len(chunks)
    }


@app.post("/query")
def ask_question(request: QueryRequest):
    query = request.question

    vectorstore = Chroma(
        persist_directory=str(chroma_path),
        embedding_function=embedding
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a helpful document question-answering assistant.

Answer the question using only the context provided below.
If the answer is not present in the context, say:
"I could not find the answer in the uploaded document."

Context:
{context}

Question:
{query}

Give a clear and concise answer.
"""

    result = generator(prompt)

    sources = []
    for doc in docs:
        sources.append({
            "page": doc.metadata.get("page", "unknown"),
            "source": doc.metadata.get("source", "unknown"),
            "content": doc.page_content
        })

    return {
        "answer": result[0]["generated_text"],
        "sources": sources
    }