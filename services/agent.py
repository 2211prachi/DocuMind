from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="gpt2",
    max_new_tokens=200
)

def rewrite_query(query: str):
    prompt = f"Rewrite this query for better document retrieval: {query}"
    result = generator(prompt)
    result = generator(prompt, do_sample=True, temperature=0.7)
    return result[0]["generated_text"].replace(prompt, "").strip()