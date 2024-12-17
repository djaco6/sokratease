import os
import json
import http.client
import sys
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

# --------- Function to process a single chunk file ---------
def process_single_chunk(txt_file_path):
    """
    Process a single .txt file and generate a question for it.
    
    Args:
        txt_file_path (str): Path to the .txt file to process
    
    Returns:
        str: Generated question content, or None if failed
    """
    # Check if file exists
    if not os.path.exists(txt_file_path):
        print(f"Error: File '{txt_file_path}' not found.")
        return None
    
    # Read the chunk text
    try:
        with open(txt_file_path, "r", encoding="utf-8") as f:
            chunk_text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    # Create the prompt
    filename = os.path.basename(txt_file_path)
    prompt = f"""
    Text to analyze ({filename}):
    {chunk_text}

    Task:
    - Write 1 multiple-choice comprehension question testing understanding of this chunk.
    - Provide 4 answer options (A–D).
    - Mark the correct answer clearly as "Answer: X".
    """

    # Generate the question
    print(f"Processing {filename}...")
    question = call_chatgpt(prompt)
    
    if question is None:
        print(f"Failed to generate question for {filename}")
        return None
    
    # Create output filename (same name but with _question suffix)
    base_name = os.path.splitext(filename)[0]
    output_dir = os.path.dirname(txt_file_path)
    
    # Check if question file already exists and find the next available number
    counter = 1
    while True:
        if counter == 1:
            output_filename = f"{base_name}_question.txt"
        else:
            output_filename = f"{base_name}_question{counter}.txt"
        
        output_path = os.path.join(output_dir, output_filename)
        
        if not os.path.exists(output_path):
            break
        
        counter += 1
    
    # Save the question
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(question)
        print(f"Question saved to: {output_path}")
    except Exception as e:
        print(f"Error saving question: {e}")
        return None
    
    return question

if __name__ == "__main__":
    # Check if a file argument was provided
    if len(sys.argv) != 2:
        print("Usage: python process_single_chunk.py <path_to_txt_file>")
        print("Example: python process_single_chunk.py chapter1_chunks/chunk1.txt")
        sys.exit(1)
    
    txt_file = sys.argv[1]
    result = process_single_chunk(txt_file)
    
    if result:
        print("\n" + "="*50)
        print("GENERATED QUESTION:")
        print("="*50)
        print(result)