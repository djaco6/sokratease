import os
import glob
import json
import http.client
from config import OPENAI_API_KEY as API_KEY

# --------- Function to call OpenAI API ---------
def call_chatgpt(prompt, model="gpt-4o-mini"):
    conn = http.client.HTTPSConnection("api.openai.com")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that writes clear multiple-choice comprehension questions."},
            {"role": "user", "content": prompt}
        ]
    }
    conn.request("POST", "/v1/chat/completions", body=json.dumps(data), headers=headers)
    resp = conn.getresponse()
    result = json.loads(resp.read().decode())
    conn.close()
    
    # Debug: Print the actual response to see what's wrong
    if "choices" not in result:
        print("Error: API response doesn't contain 'choices'")
        print("Full response:", result)
        if "error" in result:
            print("API Error:", result["error"])
        return None
    
    return result["choices"][0]["message"]["content"]

# --------- Main pipeline ---------
def generate_questions(input_folder="chapter1_chunks", output_folder="questions"):
    os.makedirs(output_folder, exist_ok=True)

    chunk_files = sorted(glob.glob(os.path.join(input_folder, "*.txt")))

    for idx, filepath in enumerate(chunk_files, 1):
        with open(filepath, "r", encoding="utf-8") as f:
            chunk_text = f.read()

        prompt = f"""
        Text to analyze (Chunk {idx}):
        {chunk_text}

        Task:
        - Write 1 multiple-choice comprehension question testing understanding of this chunk.
        - Provide 4 answer options (A–D).
        - Mark the correct answer clearly as "Answer: X".
        """

        question = call_chatgpt(prompt)
        
        if question is None:
            print(f"Failed to generate question for {filepath}, skipping...")
            continue

        outpath = os.path.join(output_folder, f"q{idx}.txt")
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(question)

        print(f"Generated question for {filepath} -> {outpath}")

if __name__ == "__main__":
    generate_questions()
