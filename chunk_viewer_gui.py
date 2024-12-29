import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import os
import glob
import sys
import re
from library_manager import add_file_to_library_gui

class ChunkViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Chunk File Viewer")
        self.root.geometry("800x600")
        
        # Initialize variables
        self.chunk_files = []
        self.current_index = 0
        self.current_folder = ""
        self.question_files = []
        self.current_question_index = 0
        self.current_question_content = ""
        self.answer_shown = False
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Top frame for folder selection
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, padx=10, fill='x')
        
        self.folder_label = tk.Label(top_frame, text="No folder selected", 
                                    bg='lightgray', relief='sunken', anchor='w')
        self.folder_label.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Buttons frame
        buttons_frame = tk.Frame(top_frame)
        buttons_frame.pack(side='right')
        
        self.add_file_btn = tk.Button(buttons_frame, text="Add File to Library", 
                                     command=self.add_file_to_library,
                                     bg='lightblue', width=15)
        self.add_file_btn.pack(side='left', padx=(0, 10))
        
        self.select_folder_btn = tk.Button(buttons_frame, text="Select Folder", 
                                          command=self.select_folder, width=12)
        self.select_folder_btn.pack(side='right')
        
        # Middle frame for file info
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5, padx=10, fill='x')
        
        self.file_info_label = tk.Label(info_frame, text="No chunks loaded", 
                                       font=('Arial', 12, 'bold'))
        self.file_info_label.pack()
        
        # Main content area with scrollable text - now in a horizontal layout
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Left side: Chunk content
        chunk_frame = tk.LabelFrame(main_frame, text="Chunk Content", font=('Arial', 10, 'bold'))
        chunk_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.text_area = scrolledtext.ScrolledText(chunk_frame, 
                                                  wrap=tk.WORD, 
                                                  font=('Arial', 11),
                                                  state='disabled')
        self.text_area.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configure text formatting tags
        self.text_area.tag_configure('bold_quote', font=('Arial', 11, 'bold'), background='lightyellow')
        
        # Right side: Questions
        question_frame = tk.LabelFrame(main_frame, text="Questions", font=('Arial', 10, 'bold'))
        question_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Question info and controls
        question_info_frame = tk.Frame(question_frame)
        question_info_frame.pack(fill='x', padx=5, pady=5)
        
        self.question_info_label = tk.Label(question_info_frame, text="No questions found", 
                                           font=('Arial', 9))
        self.question_info_label.pack(side='left')
        
        self.generate_question_btn = tk.Button(question_info_frame, text="Generate New", 
                                              command=self.generate_question,
                                              state='disabled', bg='lightblue', width=12)
        self.generate_question_btn.pack(side='right', padx=(5, 0))
        
        # Question content area
        self.question_area = scrolledtext.ScrolledText(question_frame, 
                                                      wrap=tk.WORD, 
                                                      font=('Arial', 10),
                                                      state='disabled',
                                                      height=15)
        self.question_area.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        
        # Show answer button
        answer_button_frame = tk.Frame(question_frame)
        answer_button_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        self.show_answer_btn = tk.Button(answer_button_frame, text="Show Answer", 
                                        command=self.toggle_answer,
                                        state='disabled', bg='lightgreen', width=12)
        self.show_answer_btn.pack()
        
        # Question navigation
        question_nav_frame = tk.Frame(question_frame)
        question_nav_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        self.prev_question_btn = tk.Button(question_nav_frame, text="◀ Prev Q", 
                                          command=self.previous_question, 
                                          state='disabled', width=8)
        self.prev_question_btn.pack(side='left')
        
        self.next_question_btn = tk.Button(question_nav_frame, text="Next Q ▶", 
                                          command=self.next_question, 
                                          state='disabled', width=8)
        self.next_question_btn.pack(side='right')
        
        # Bottom frame for navigation
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10, fill='x')
        
        # Navigation buttons
        self.prev_btn = tk.Button(nav_frame, text="◀ Previous Chunk", 
                                 command=self.previous_chunk, 
                                 state='disabled', width=15)
        self.prev_btn.pack(side='left', padx=20)
        
        self.next_btn = tk.Button(nav_frame, text="Next Chunk ▶", 
                                 command=self.next_chunk, 
                                 state='disabled', width=15)
        self.next_btn.pack(side='right', padx=20)
        
    def add_file_to_library(self):
        """Add a new text file to the library with chunking."""
        # File selection dialog
        file_path = filedialog.askopenfilename(
            title="Select text file to add to library",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Get chunking parameters
        try:
            chunk_size = simpledialog.askinteger(
                "Chunk Size",
                "Enter chunk size (words per chunk):",
                initialvalue=1000,
                minvalue=100,
                maxvalue=5000
            )
            
            if chunk_size is None:
                return
            
            overlap = simpledialog.askinteger(
                "Chunk Overlap",
                "Enter overlap between chunks (words):",
                initialvalue=100,
                minvalue=0,
                maxvalue=min(500, chunk_size // 2)
            )
            
            if overlap is None:
                return
                
        except Exception:
            messagebox.showerror("Error", "Invalid input for chunk parameters")
            return
        
        # Show processing message
        self.root.config(cursor="wait")
        self.root.update()
        
        try:
            # Add file to library
            success, message, book_folder = add_file_to_library_gui(
                file_path, 
                library_path="myLibrary",
                chunk_size=chunk_size,
                overlap=overlap
            )
            
            self.root.config(cursor="")
            
            if success:
                # Ask if user wants to open the new chunks folder
                result = messagebox.askyesno(
                    "Success", 
                    f"{message}\n\nWould you like to open the chunks folder for this book?"
                )
                
                if result and book_folder:
                    chunks_folder = os.path.join(book_folder, "chunks")
                    if os.path.exists(chunks_folder):
                        self.current_folder = chunks_folder
                        self.load_chunks()
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            
    def select_folder(self):
        # Start from myLibrary directory if it exists
        initial_dir = os.path.join(os.getcwd(), "myLibrary")
        if not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
            
        folder_path = filedialog.askdirectory(
            title="Select chunks folder (e.g., myLibrary/BookName/chunks)", 
            initialdir=initial_dir
        )
        
        if folder_path:
            self.current_folder = folder_path
            self.load_chunks()
            
    def load_chunks(self):
        # Find all chunk folders in the selected folder
        if not os.path.exists(self.current_folder):
            messagebox.showerror("Error", f"Folder not found: {self.current_folder}")
            return
        
        # Look for chunk folders (chunk1, chunk2, etc.)
        chunk_folders = []
        for item in os.listdir(self.current_folder):
            item_path = os.path.join(self.current_folder, item)
            if os.path.isdir(item_path) and item.startswith('chunk'):
                # Find the chunk file inside this folder
                chunk_file = os.path.join(item_path, f"{item}.txt")
                if os.path.exists(chunk_file):
                    chunk_folders.append(chunk_file)
        
        if not chunk_folders:
            messagebox.showwarning("No Files", "No chunk folders found in the selected directory")
            self.folder_label.config(text="No valid chunk folders found")
            return
        
        # Sort files numerically instead of alphabetically
        def extract_number(filepath):
            # Extract number from filepath like ".../chunk1/chunk1.txt", ".../chunk10/chunk10.txt", etc.
            folder_name = os.path.basename(os.path.dirname(filepath))
            match = re.search(r'chunk(\d+)', folder_name)
            return int(match.group(1)) if match else 0
        
        self.chunk_files = sorted(chunk_folders, key=extract_number)
        
        if self.chunk_files:
            self.current_index = 0
            self.folder_label.config(text=f"Folder: {self.current_folder}")
            self.display_current_chunk()
            self.update_navigation_buttons()
            messagebox.showinfo("Success", f"Loaded {len(self.chunk_files)} chunk files")
        else:
            messagebox.showwarning("No Files", "No chunk files found in the selected folder")
            self.folder_label.config(text="No valid chunk files found")
            
    def display_current_chunk(self):
        if not self.chunk_files:
            return
            
        current_file = self.chunk_files[self.current_index]
        filename = os.path.basename(current_file)
        
        # Update file info
        self.file_info_label.config(text=f"File {self.current_index + 1} of {len(self.chunk_files)}: {filename}")
        
        # Read and display file content
        try:
            with open(current_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Enable text area, insert content, then disable
            self.text_area.config(state='normal')
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, content)
            # Clear any existing highlighting
            self.text_area.tag_remove('bold_quote', 1.0, tk.END)
            self.text_area.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")
        
        # Load and display questions for this chunk
        self.load_questions_for_current_chunk()
    
    def load_questions_for_current_chunk(self):
        if not self.chunk_files:
            return
            
        current_file = self.chunk_files[self.current_index]
        # Get the chunk folder (parent directory of the chunk file)
        chunk_folder = os.path.dirname(current_file)
        base_name = os.path.splitext(os.path.basename(current_file))[0]  # e.g., "chunk1"
        
        # Find all question files for this chunk in the same folder
        pattern = os.path.join(chunk_folder, f"{base_name}_question*.txt")
        self.question_files = glob.glob(pattern)
        
        # Sort question files numerically
        def extract_question_number(filename):
            match = re.search(r'_question(\d*)', os.path.basename(filename))
            if match:
                return int(match.group(1)) if match.group(1) else 1
            return 0
        
        self.question_files = sorted(self.question_files, key=extract_question_number)
        self.current_question_index = 0
        
        self.display_current_question()
        self.update_question_navigation_buttons()
    
    def display_current_question(self):
        if not self.question_files:
            self.question_info_label.config(text="No questions found")
            self.question_area.config(state='normal')
            self.question_area.delete(1.0, tk.END)
            self.question_area.insert(1.0, "No questions available for this chunk.\nClick 'Generate New' to create one.")
            self.question_area.config(state='disabled')
            self.show_answer_btn.config(state='disabled')
            self.current_question_content = ""
            self.answer_shown = False
            return
            
        current_question_file = self.question_files[self.current_question_index]
        filename = os.path.basename(current_question_file)
        
        # Update question info
        self.question_info_label.config(text=f"Question {self.current_question_index + 1} of {len(self.question_files)}: {filename}")
        
        # Read and store full question content
        try:
            with open(current_question_file, 'r', encoding='utf-8') as f:
                self.current_question_content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read question file: {e}")
            return
        
        # Reset answer state and show question without answer
        self.answer_shown = False
        self.show_question_without_answer()
        self.show_answer_btn.config(state='normal', text="Show Answer")
    
    def show_question_without_answer(self):
        """Display the question content without the answer line and supporting quote."""
        if not self.current_question_content:
            return
            
        # Split content by lines
        lines = self.current_question_content.split('\n')
        question_lines = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Stop adding lines if we encounter "answer" or "from the text"
            if ('answer' in line_lower and 
                (line_lower.startswith('answer') or '**answer' in line_lower)):
                break
            if 'from the text' in line_lower:
                break
                
            question_lines.append(line)
        
        # Remove any trailing empty lines
        while question_lines and not question_lines[-1].strip():
            question_lines.pop()
        
        question_only = '\n'.join(question_lines).strip()
        
        # Display question without answer
        self.question_area.config(state='normal')
        self.question_area.delete(1.0, tk.END)
        self.question_area.insert(1.0, question_only)
        self.question_area.config(state='disabled')
    
    def toggle_answer(self):
        """Toggle between showing and hiding the answer."""
        if not self.current_question_content:
            return
            
        if self.answer_shown:
            # Hide answer
            self.show_question_without_answer()
            self.show_answer_btn.config(text="Show Answer")
            self.answer_shown = False
            # Remove highlighting from chunk text
            self.remove_text_highlighting()
        else:
            # Show full content including answer
            self.question_area.config(state='normal')
            self.question_area.delete(1.0, tk.END)
            self.question_area.insert(1.0, self.current_question_content)
            self.question_area.config(state='disabled')
            self.show_answer_btn.config(text="Hide Answer")
            self.answer_shown = True
            # Highlight quoted evidence in chunk text
            self.highlight_quoted_evidence()
    
    def previous_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.display_current_question()
            self.update_question_navigation_buttons()
    
    def next_question(self):
        if self.current_question_index < len(self.question_files) - 1:
            self.current_question_index += 1
            self.display_current_question()
            self.update_question_navigation_buttons()
    
    def update_question_navigation_buttons(self):
        if not self.question_files:
            self.prev_question_btn.config(state='disabled')
            self.next_question_btn.config(state='disabled')
            return
            
        # Enable/disable based on current position
        self.prev_question_btn.config(state='normal' if self.current_question_index > 0 else 'disabled')
        self.next_question_btn.config(state='normal' if self.current_question_index < len(self.question_files) - 1 else 'disabled')
            
    def previous_chunk(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_chunk()
            self.update_navigation_buttons()
            
    def next_chunk(self):
        if self.current_index < len(self.chunk_files) - 1:
            self.current_index += 1
            self.display_current_chunk()
            self.update_navigation_buttons()
            
    def update_navigation_buttons(self):
        if not self.chunk_files:
            self.prev_btn.config(state='disabled')
            self.next_btn.config(state='disabled')
            self.generate_question_btn.config(state='disabled')
            return
            
        # Enable/disable based on current position
        self.prev_btn.config(state='normal' if self.current_index > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_index < len(self.chunk_files) - 1 else 'disabled')
        self.generate_question_btn.config(state='normal')
        
    def generate_question(self):
        if not self.chunk_files:
            return
            
        current_file = self.chunk_files[self.current_index]
        filename = os.path.basename(current_file)
        
        # Import and use the process_single_chunk function
        try:
            # Add the current working directory (where process_single_chunk.py is located) to Python path
            current_dir = os.getcwd()
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            from process_single_chunk import process_single_chunk
            
            # Show processing message
            result = messagebox.askyesno("Generate Question", 
                                       f"Generate a question for {filename}?")
            if result:
                self.root.config(cursor="wait")
                self.root.update()
                
                question = process_single_chunk(current_file)
                
                self.root.config(cursor="")
                
                if question:
                    messagebox.showinfo("Success", "Question generated successfully!")
                    # Refresh the question panel to show the new question
                    self.load_questions_for_current_chunk()
                else:
                    messagebox.showerror("Error", "Failed to generate question. Check console for details.")
                    
        except ImportError as e:
            messagebox.showerror("Error", f"process_single_chunk.py not found: {e}")
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Error", f"Error generating question: {e}")

    def extract_quoted_evidence(self):
        """Extract quoted evidence from the question content."""
        if not self.current_question_content:
            return []
        
        quotes = []
        lines = self.current_question_content.split('\n')
        
        # Look for quoted text in the answer section
        in_answer_section = False
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Check if we've reached the answer section
            if 'answer' in line_lower and (line_lower.startswith('answer') or '**answer' in line_lower):
                in_answer_section = True
                continue
            
            # If we're in the answer section, look for quoted text
            if in_answer_section and line_stripped:
                # Look for text in quotes (various quote styles)
                import re
                quote_patterns = [
                    r'"([^"]+)"',                    # Double quotes
                    r'"([^"]+)"',                    # Smart double quotes
                    r'['']([^'']+)['']',             # Smart single quotes
                    r"'([^']+)'",                    # Regular single quotes
                ]
                
                for pattern in quote_patterns:
                    matches = re.findall(pattern, line_stripped)
                    for match in matches:
                        # Clean up the quote (remove extra whitespace)
                        cleaned_quote = ' '.join(match.split())
                        if len(cleaned_quote) > 10:  # Only consider substantial quotes
                            quotes.append(cleaned_quote)
        
        return quotes

    def highlight_quoted_evidence(self):
        """Highlight quoted evidence in the chunk text area."""
        quotes = self.extract_quoted_evidence()
        
        if not quotes:
            return
        
        # Get the current chunk text
        self.text_area.config(state='normal')
        chunk_text = self.text_area.get(1.0, tk.END)
        
        # Find and highlight each quote
        for quote in quotes:
            # Find all occurrences of the quote in the text
            start_idx = 0
            while True:
                # Search for the quote (case-insensitive)
                pos = chunk_text.lower().find(quote.lower(), start_idx)
                if pos == -1:
                    break
                
                # Convert character position to tkinter text position
                lines_before = chunk_text[:pos].count('\n')
                chars_in_line = pos - chunk_text.rfind('\n', 0, pos) - 1
                if chars_in_line < 0:
                    chars_in_line = pos
                
                start_pos = f"{lines_before + 1}.{chars_in_line}"
                end_pos = f"{lines_before + 1}.{chars_in_line + len(quote)}"
                
                # Apply highlighting
                self.text_area.tag_add('bold_quote', start_pos, end_pos)
                
                start_idx = pos + 1
        
        self.text_area.config(state='disabled')

    def remove_text_highlighting(self):
        """Remove all text highlighting from the chunk text area."""
        self.text_area.config(state='normal')
        self.text_area.tag_remove('bold_quote', 1.0, tk.END)
        self.text_area.config(state='disabled')

def main():
    root = tk.Tk()
    app = ChunkViewer(root)
    
    # Keyboard shortcuts
    root.bind('<Left>', lambda e: app.previous_chunk())
    root.bind('<Right>', lambda e: app.next_chunk())
    root.bind('<Return>', lambda e: app.generate_question())
    
    root.mainloop()

if __name__ == "__main__":
    main()