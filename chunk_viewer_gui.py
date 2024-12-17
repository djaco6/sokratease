import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import glob

class ChunkViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Chunk File Viewer")
        self.root.geometry("800x600")
        
        # Initialize variables
        self.chunk_files = []
        self.current_index = 0
        self.current_folder = ""
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Top frame for folder selection
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, padx=10, fill='x')
        
        self.folder_label = tk.Label(top_frame, text="No folder selected", 
                                    bg='lightgray', relief='sunken', anchor='w')
        self.folder_label.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.select_folder_btn = tk.Button(top_frame, text="Select Folder", 
                                          command=self.select_folder)
        self.select_folder_btn.pack(side='right')
        
        # Middle frame for file info
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5, padx=10, fill='x')
        
        self.file_info_label = tk.Label(info_frame, text="No chunks loaded", 
                                       font=('Arial', 12, 'bold'))
        self.file_info_label.pack()
        
        # Main content area with scrollable text
        content_frame = tk.Frame(self.root)
        content_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.text_area = scrolledtext.ScrolledText(content_frame, 
                                                  wrap=tk.WORD, 
                                                  font=('Arial', 11),
                                                  state='disabled')
        self.text_area.pack(fill='both', expand=True)
        
        # Bottom frame for navigation
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=10, fill='x')
        
        # Navigation buttons
        self.prev_btn = tk.Button(nav_frame, text="◀ Previous", 
                                 command=self.previous_chunk, 
                                 state='disabled', width=12)
        self.prev_btn.pack(side='left', padx=20)
        
        self.next_btn = tk.Button(nav_frame, text="Next ▶", 
                                 command=self.next_chunk, 
                                 state='disabled', width=12)
        self.next_btn.pack(side='right', padx=20)
        
        # Generate question button (centered)
        self.generate_btn = tk.Button(nav_frame, text="Generate Question", 
                                     command=self.generate_question,
                                     state='disabled', bg='lightblue', width=15)
        self.generate_btn.pack(side='top', pady=5)
        
    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder containing chunk files")
        if folder_path:
            self.current_folder = folder_path
            self.load_chunks()
            
    def load_chunks(self):
        # Find all .txt files in the selected folder
        pattern = os.path.join(self.current_folder, "*.txt")
        all_files = glob.glob(pattern)
        
        # Filter out question files (files containing "_question")
        self.chunk_files = [f for f in all_files if "_question" not in os.path.basename(f)]
        self.chunk_files.sort()
        
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
            self.text_area.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")
            
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
            self.generate_btn.config(state='disabled')
            return
            
        # Enable/disable based on current position
        self.prev_btn.config(state='normal' if self.current_index > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_index < len(self.chunk_files) - 1 else 'disabled')
        self.generate_btn.config(state='normal')
        
    def generate_question(self):
        if not self.chunk_files:
            return
            
        current_file = self.chunk_files[self.current_index]
        filename = os.path.basename(current_file)
        
        # Import and use the process_single_chunk function
        try:
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
                else:
                    messagebox.showerror("Error", "Failed to generate question. Check console for details.")
                    
        except ImportError:
            messagebox.showerror("Error", "process_single_chunk.py not found in current directory")
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Error", f"Error generating question: {e}")

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