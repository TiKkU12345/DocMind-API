import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query: str, chunks: list[str]) -> str:
    context = "\n\n".join(chunks)

    prompt = f"""You are a helpful AI assistant. Answer the user's question based only on the provided context. 
If the answer is not in the context, say "I don't have enough information to answer this."

Context:
{context}

Question: {query}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.1
    )

    return response.choices[0].message.content