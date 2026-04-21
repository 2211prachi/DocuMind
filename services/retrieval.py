from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path

chroma_path = Path(__file__).parent.parent / "chroma_db"

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def retrieve_docs(query: str, filename: str = None, k=5):
    vectorstore = Chroma(
        persist_directory=str(chroma_path),
        embedding_function=embedding
    )

    # Filter at the database level so only chunks from the target file are searched
    if filename:
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        docs = vectorstore.similarity_search(
            query,
            k=k,
            filter={"filename": filename}
        )
    else:
        docs = vectorstore.similarity_search(query, k=k)

    docs = sorted(docs, key=lambda x: len(x.page_content), reverse=True)

    return docs[:3]