from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from transformers import pipeline

# Path to saved ChromaDB
chroma_path = Path(__file__).parent / "chroma_db"

# Same embedding model used while storing vectors
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load the saved vector database
vectorstore = Chroma(
    persist_directory=str(chroma_path),
    embedding_function=embedding
)

# Retriever to fetch top relevant chunks
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Load a text generation model
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    max_new_tokens=200
)

# Take user question
query = input("Enter your question: ")

# Retrieve relevant chunks
docs = retriever.invoke(query)

# Combine retrieved chunks into one context
context = "\n\n".join([doc.page_content for doc in docs])

# Create prompt for the model
prompt = f"""
Answer the question based only on the context below.

Context:
{context}

Question:
{query}

Answer:
"""

# Generate final answer
result = generator(prompt)

print("\nFinal Answer:\n")
print(result[0]["generated_text"])