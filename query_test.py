from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

chroma_path = Path(__file__).parent / "chroma_db"

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory=str(chroma_path),
    embedding_function=embedding
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

query = input("Enter your question: ")

docs = retriever.invoke(query)

print("\nTop matching chunks:\n")
for i, doc in enumerate(docs, 1):
    print(f"\n--- Result {i} ---")
    print(doc.page_content[:1000])