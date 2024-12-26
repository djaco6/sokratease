import os
import json
import http.client
import sys
import glob
import re
from config import OPENAI_API_KEY as API_KEY

# --------- Function to find existing questions ---------
def find_existing_questions(txt_file_path):
    """
    Find all existing question files for a given chunk file in the same folder.
    
    Args:
        txt_file_path (str): Path to the .txt chunk file
    
    Returns:
        list: List of question contents from existing question files
    """
    base_name = os.path.splitext(os.path.basename(txt_file_path))[0]  # e.g., "chunk1"
    chunk_folder = os.path.dirname(txt_file_path)  # Get the chunk's own folder
    
    # Find all question files for this chunk in the same folder
    pattern = os.path.join(chunk_folder, f"{base_name}_question*.txt")
    question_files = glob.glob(pattern)
    
    if not question_files:
        return []
    
    # Sort question files numerically
    def extract_question_number(filename):
        match = re.search(r'_question(\d*)', os.path.basename(filename))
        if match:
            return int(match.group(1)) if match.group(1) else 1
        return 0
    
    question_files = sorted(question_files, key=extract_question_number)
    
    # Read the content of each question file
    existing_questions = []
    for i, question_file in enumerate(question_files, 1):
        try:
            with open(question_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                existing_questions.append(f"EXISTING QUESTION {i}:\n{content}")
        except Exception as e:
            print(f"Warning: Could not read question file {question_file}: {e}")
    
    return existing_questions

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
    
    # Find existing questions for this chunk
    existing_questions = find_existing_questions(txt_file_path)
    
    # Create the prompt
    filename = os.path.basename(txt_file_path)
    
    if existing_questions:
        # If there are existing questions, create a more sophisticated prompt
        existing_questions_text = "\n\n".join(existing_questions)
        prompt = f"""
        Text to analyze ({filename}):
        {chunk_text}

        EXISTING QUESTIONS FOR THIS TEXT:
        {existing_questions_text}

        Task:
        - Write 1 NEW multiple-choice comprehension question that is DIFFERENT from the existing questions above.
        - Focus on a DIFFERENT aspect, theme, or part of the text that hasn't been covered yet.
        - Avoid overlapping with the subject matter of the existing questions.
        - Look for different concepts, details, relationships, or interpretations in the text.
        - Provide 4 answer options (A–D).
        - Mark the correct answer clearly as "Answer: X".
        - After the answer, provide a relevant quote from the text that supports the correct answer.
        - Mark the quote as "From the text: [quote]".
        
        Make sure your new question tests understanding of content that is distinct from what the existing questions already cover.
        """
    else:
        # If no existing questions, use the original prompt
        prompt = f"""
        Text to analyze ({filename}):
        {chunk_text}

        Task:
        - Write 1 multiple-choice comprehension question testing understanding of this chunk.
        - Provide 4 answer options (A–D).
        - Mark the correct answer clearly as "Answer: X".
        - After the answer, provide a relevant quote from the text that supports the correct answer.
        - Mark the quote as "From the text: [quote]".
        """

    # Generate the question
    if existing_questions:
        print(f"Processing {filename}... (Found {len(existing_questions)} existing questions)")
    else:
        print(f"Processing {filename}... (No existing questions)")
    
    question = call_chatgpt(prompt)
    
    if question is None:
        print(f"Failed to generate question for {filename}")
        return None
    
    # Create output filename (same folder as the chunk)
    base_name = os.path.splitext(filename)[0]
    chunk_folder = os.path.dirname(txt_file_path)  # Get the chunk's folder
    
    # Check if question file already exists and find the next available number
    counter = 1
    while True:
        if counter == 1:
            output_filename = f"{base_name}_question.txt"
        else:
            output_filename = f"{base_name}_question{counter}.txt"
        
        output_path = os.path.join(chunk_folder, output_filename)
        
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