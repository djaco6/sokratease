import os
import re
import shutil
from pathlib import Path

class LibraryManager:
    def __init__(self, library_path="myLibrary"):
        """
        Initialize the Library Manager.
        
        Args:
            library_path (str): Path to the library directory
        """
        self.library_path = Path(library_path)
        self.library_path.mkdir(exist_ok=True)
    
    def add_file_to_library(self, source_file_path, chunk_size=1000, overlap=100):
        """
        Add a text file to the library by creating a folder, copying the file,
        and chunking it automatically.
        
        Args:
            source_file_path (str): Path to the source text file
            chunk_size (int): Target size of each chunk in words
            overlap (int): Number of words to overlap between chunks
            
        Returns:
            str: Path to the created book folder, or None if failed
        """
        source_path = Path(source_file_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_file_path}")
        
        if not source_path.suffix.lower() == '.txt':
            raise ValueError("Only .txt files are supported")
        
        # Create a clean folder name from the filename
        book_name = self._create_clean_folder_name(source_path.stem)
        book_folder = self.library_path / book_name
        
        # Create the book folder
        book_folder.mkdir(exist_ok=True)
        
        # Copy the source file to the book folder
        dest_file = book_folder / source_path.name
        shutil.copy2(source_path, dest_file)
        
        # Create chunks folder
        chunks_folder = book_folder / "chunks"
        chunks_folder.mkdir(exist_ok=True)
        
        # Chunk the file
        chunk_count = self._chunk_file(dest_file, chunks_folder, chunk_size, overlap)
        
        print(f"✅ Successfully added '{book_name}' to library")
        print(f"📁 Location: {book_folder}")
        print(f"📄 Original file: {dest_file.name}")
        print(f"🔢 Created {chunk_count} chunks in: {chunks_folder}")
        
        return str(book_folder)
    
    def _create_clean_folder_name(self, filename):
        """
        Create a clean folder name from filename by removing problematic characters.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Clean folder name
        """
        # Remove file extension if present
        clean_name = os.path.splitext(filename)[0]
        
        # Replace problematic characters with underscores or remove them
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', clean_name)
        
        # Replace multiple spaces/underscores with single underscore
        clean_name = re.sub(r'[_\s]+', '_', clean_name)
        
        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')
        
        # Truncate if too long
        if len(clean_name) > 50:
            clean_name = clean_name[:50].rstrip('_')
        
        # Ensure it's not empty
        if not clean_name:
            clean_name = "UnknownBook"
        
        # Handle duplicate names
        original_name = clean_name
        counter = 1
        while (self.library_path / clean_name).exists():
            clean_name = f"{original_name}_{counter}"
            counter += 1
        
        return clean_name
    
    def _chunk_file(self, file_path, output_folder, chunk_size, overlap):
        """
        Chunk a text file into smaller pieces, preserving paragraph boundaries.
        
        Args:
            file_path (Path): Path to the text file
            output_folder (Path): Folder to save chunks
            chunk_size (int): Target size of each chunk in words
            overlap (int): Number of words to overlap between chunks
            
        Returns:
            int: Number of chunks created
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"Could not decode file {file_path}")
        
        if not text.strip():
            raise ValueError("File appears to be empty or contains no readable text")
        
        # Split text into paragraphs (split on double line breaks or more)
        paragraphs = re.split(r'\n\s*\n', text.strip())
        
        # Clean paragraphs and add tab indentation
        formatted_paragraphs = []
        for para in paragraphs:
            # Clean up the paragraph (remove extra whitespace, preserve single line breaks)
            cleaned_para = re.sub(r'\s+', ' ', para.strip())
            if cleaned_para:  # Only add non-empty paragraphs
                # Check if this paragraph is too long for a chunk
                para_word_count = len(cleaned_para.split())
                
                if para_word_count > chunk_size * 1.5:  # If paragraph is significantly larger than chunk size
                    # Split long paragraph into sentences for better chunking
                    sentences = re.split(r'(?<=[.!?])\s+', cleaned_para)
                    
                    current_section = []
                    current_section_words = 0
                    
                    for sentence in sentences:
                        sentence_words = len(sentence.split())
                        
                        if current_section_words + sentence_words > chunk_size and current_section:
                            # Save current section as a formatted paragraph
                            section_text = ' '.join(current_section)
                            formatted_para = f"\t{section_text}"
                            formatted_paragraphs.append(formatted_para)
                            
                            # Start new section
                            current_section = [sentence]
                            current_section_words = sentence_words
                        else:
                            current_section.append(sentence)
                            current_section_words += sentence_words
                    
                    # Add the last section if it has content
                    if current_section:
                        section_text = ' '.join(current_section)
                        formatted_para = f"\t{section_text}"
                        formatted_paragraphs.append(formatted_para)
                else:
                    # Add tab at the beginning for normal-sized paragraphs
                    formatted_para = f"\t{cleaned_para}"
                    formatted_paragraphs.append(formatted_para)
        
        if not formatted_paragraphs:
            raise ValueError("No paragraphs found in the text")
        
        chunk_num = 1
        current_chunk_paragraphs = []
        current_word_count = 0
        
        i = 0
        while i < len(formatted_paragraphs):
            paragraph = formatted_paragraphs[i]
            para_word_count = len(paragraph.split())
            
            # Check if adding this paragraph would exceed chunk size
            if current_word_count + para_word_count > chunk_size and current_chunk_paragraphs:
                # Save current chunk
                self._save_chunk(output_folder, chunk_num, current_chunk_paragraphs)
                chunk_num += 1
                
                # Start new chunk with overlap
                if overlap > 0 and len(current_chunk_paragraphs) > 1:
                    # Calculate how many paragraphs to include for overlap
                    overlap_paragraphs = []
                    overlap_words = 0
                    
                    # Go backwards through current chunk paragraphs to build overlap
                    for j in range(len(current_chunk_paragraphs) - 1, -1, -1):
                        para_words = len(current_chunk_paragraphs[j].split())
                        if overlap_words + para_words <= overlap:
                            overlap_paragraphs.insert(0, current_chunk_paragraphs[j])
                            overlap_words += para_words
                        else:
                            break
                    
                    current_chunk_paragraphs = overlap_paragraphs
                    current_word_count = overlap_words
                else:
                    current_chunk_paragraphs = []
                    current_word_count = 0
            
            # Add current paragraph to chunk
            current_chunk_paragraphs.append(paragraph)
            current_word_count += para_word_count
            i += 1
        
        # Save the last chunk if it has content
        if current_chunk_paragraphs:
            self._save_chunk(output_folder, chunk_num, current_chunk_paragraphs)
        
        return chunk_num
    
    def _save_chunk(self, output_folder, chunk_num, paragraphs):
        """
        Save a chunk with proper paragraph formatting in its own folder.
        
        Args:
            output_folder (Path): Output directory (chunks folder)
            chunk_num (int): Chunk number
            paragraphs (list): List of formatted paragraphs
        """
        # Create individual chunk folder
        chunk_folder_name = f"chunk{chunk_num}"
        chunk_folder_path = output_folder / chunk_folder_name
        chunk_folder_path.mkdir(exist_ok=True)
        
        # Save chunk file inside its own folder
        chunk_filename = f"chunk{chunk_num}.txt"
        chunk_path = chunk_folder_path / chunk_filename
        
        # Join paragraphs with double line breaks to preserve paragraph structure
        chunk_text = '\n\n'.join(paragraphs)
        
        with open(chunk_path, 'w', encoding='utf-8') as f:
            f.write(chunk_text)
    
    def list_books(self):
        """
        List all books in the library.
        
        Returns:
            list: List of book folder names
        """
        if not self.library_path.exists():
            return []
        
        books = []
        for item in self.library_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                books.append(item.name)
        
        return sorted(books)
    
    def get_book_info(self, book_name):
        """
        Get information about a book in the library.
        
        Args:
            book_name (str): Name of the book folder
            
        Returns:
            dict: Book information including original file, chunk count, etc.
        """
        book_folder = self.library_path / book_name
        
        if not book_folder.exists():
            return None
        
        info = {
            'name': book_name,
            'folder_path': str(book_folder),
            'original_files': [],
            'chunks_folder': None,
            'chunk_count': 0
        }
        
        # Find original text files
        for file_path in book_folder.glob('*.txt'):
            info['original_files'].append(file_path.name)
        
        # Check chunks folder
        chunks_folder = book_folder / 'chunks'
        if chunks_folder.exists():
            info['chunks_folder'] = str(chunks_folder)
            # Count chunk folders (not chunk files directly)
            chunk_folders = [d for d in chunks_folder.iterdir() if d.is_dir() and d.name.startswith('chunk')]
            info['chunk_count'] = len(chunk_folders)
        
        return info

# Convenience function for GUI integration
def add_file_to_library_gui(source_file_path, library_path="myLibrary", chunk_size=1000, overlap=100):
    """
    Convenience function to add a file to the library (for GUI use).
    
    Args:
        source_file_path (str): Path to the source file
        library_path (str): Path to library directory
        chunk_size (int): Words per chunk
        overlap (int): Overlap between chunks
        
    Returns:
        tuple: (success: bool, message: str, book_folder: str or None)
    """
    try:
        manager = LibraryManager(library_path)
        book_folder = manager.add_file_to_library(source_file_path, chunk_size, overlap)
        return True, "File successfully added to library!", book_folder
    except Exception as e:
        return False, f"Error adding file to library: {str(e)}", None

if __name__ == "__main__":
    # Example usage
    manager = LibraryManager()
    
    print("Library Manager - Available Books:")
    books = manager.list_books()
    
    if books:
        for book in books:
            info = manager.get_book_info(book)
            print(f"📚 {book}")
            print(f"   Original files: {', '.join(info['original_files'])}")
            print(f"   Chunks: {info['chunk_count']}")
            print(f"   Path: {info['folder_path']}")
            print()
    else:
        print("No books found in library.")
        print(f"Library location: {manager.library_path.absolute()}")