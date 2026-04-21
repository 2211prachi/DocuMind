from transformers import pipeline

generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    max_new_tokens=150
)

def generate_answer(query: str, docs, chat_history):
    context = ""
    for i, doc in enumerate(docs, 1):
        context += f"""
Source {i}:
{doc.page_content}
"""

    prompt = f"""
Answer the question based only on the context.

Context:
{context}

Question:
{query}

Answer:
"""

    
    result = generator(prompt)
    return result[0]["generated_text"]