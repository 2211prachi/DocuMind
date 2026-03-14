from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

pdf_path = Path(__file__).parent / "sample.pdf"

loader = PyPDFLoader(str(pdf_path))
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)

print("Total pages:", len(documents))
print("Total chunks:", len(chunks))
print("\nFirst chunk:\n")
print(chunks[0].page_content)
print()
print("\nSecond chunk:\n")
print(chunks[1].page_content)