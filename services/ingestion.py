from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

base_path = Path(__file__).parent.parent
chroma_path = base_path / "chroma_db"

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def process_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    # add filename metadata
    for doc in chunks:
        doc.metadata["filename"] = Path(file_path).name

    Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=str(chroma_path)
    )

    return len(documents), len(chunks)