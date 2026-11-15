import requests
import json
from retrieval_engine import HybridRetriever

# 1. PASTE YOUR EXACT API KEY HERE (Starting with AQ...)
GEMINI_API_KEY = "YOUR_API_KEY_HERE"

print("Initializing System Engine...")
# 2. Load the custom retrieval engine
retriever = HybridRetriever("data/processed_corpus.csv")

def generate_answer(query):
    print("\n[Step 1] Retrieving relevant context from PDFs...")
    results = retriever.hybrid_rrf_search(query, top_k=2)
    
    context = ""
    for i, res in enumerate(results):
        context += f"[Document {i+1}]: {res['text']}\n\n"
        
    print("[Step 2] Generating answer via Google AI...")
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""You are an intelligent academic advisor named 'CourseCompass'.
    Based ONLY on the following syllabus context documents, answer the user's question clearly and politely in well-formatted markdown.
    If the answer is not present in the context, clearly state: "I don't have information about this in the syllabus."
    Do not use outside knowledge.
    
    Context Documents:
    {context}
    
    User Question: {query}
    """

    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    # Direct, pure API call with NO offline fallback. It will wait up to 30 seconds for the beautiful AI response.
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        response.raise_for_status() 
        result_json = response.json()
        answer = result_json['candidates'][0]['content']['parts'][0]['text']
        return answer
    except Exception as e:
        error_details = response.text if 'response' in locals() else 'No response data'
        return f"System Error: Failed to connect to Google API. \nDetails: {e}\nServer Response: {error_details}"

# --- Testing Phase ---
if __name__ == "__main__":
    print("\n" + "="*70)
    print(" Welcome to CourseCompass (RAG System Pipeline)")
    print("="*70)
    
    test_query = "What prerequisites are required to understand deep learning?"
    print(f"\nUser Query: {test_query}\n")
    
    final_answer = generate_answer(test_query)
    
    print("\n" + "="*70)
    print(" CourseCompass AI Response:")
    print("-" * 70)
    print(final_answer)
    print("="*70 + "\n")