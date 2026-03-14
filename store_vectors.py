from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

pdf_path = Path(__file__).parent / "sample.pdf"
chroma_path = Path(__file__).parent / "chroma_db"

loader = PyPDFLoader(str(pdf_path))
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embedding,
    persist_directory=str(chroma_path)
)

print("Embeddings stored successfully.")
print("Total chunks stored:", len(chunks))
print("ChromaDB folder created at:", chroma_path)