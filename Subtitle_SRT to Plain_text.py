import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import os

class SRTConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT to Plain Text Converter")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="SRT to Plain Text Converter", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection
        ttk.Label(main_frame, text="Select SRT file:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(main_frame, textvariable=self.file_path_var, width=50)
        file_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        
        browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=1, column=2, padx=(5, 0), pady=5)
        
        # Input text area
        ttk.Label(main_frame, text="Input SRT Text:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=(10, 5))
        self.input_text = scrolledtext.ScrolledText(main_frame, height=12, width=70)
        self.input_text.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                            padx=(10, 0), pady=(10, 5))
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        convert_btn = ttk.Button(btn_frame, text="Convert", command=self.convert_text)
        convert_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_all)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(btn_frame, text="Save Output", command=self.save_output)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Output text area
        ttk.Label(main_frame, text="Plain Text Output:").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=(10, 5))
        self.output_text = scrolledtext.ScrolledText(main_frame, height=12, width=70)
        self.output_text.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                             padx=(10, 0), pady=(10, 5))
        
        # Load sample data
        self.load_sample_data()
    
    def load_sample_data(self):
        """Load the sample SRT data provided by the user."""
        sample_srt = ""
        
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, sample_srt)
    
    def browse_file(self):
        """Open file dialog to select SRT file."""
        file_path = filedialog.askopenfilename(
            title="Select SRT file",
            filetypes=[("SRT files", "*.srt"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(1.0, content)
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as file:
                        content = file.read()
                    self.input_text.delete(1.0, tk.END)
                    self.input_text.insert(1.0, content)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not read file: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {str(e)}")
    
    def convert_srt_to_plain_text(self, srt_content):
        """Convert SRT content to plain text."""
        if not srt_content.strip():
            return ""
        
        # Split content into blocks (separated by empty lines)
        blocks = re.split(r'\n\s*\n', srt_content.strip())
        
        extracted_sentences = []
        
        for block in blocks:
            if not block.strip():
                continue
            
            lines = block.strip().split('\n')
            
            # Filter out empty lines
            lines = [line.strip() for line in lines if line.strip()]
            
            if len(lines) < 2:
                continue
            
            # Find the timestamp line (contains --> )
            timestamp_line_index = -1
            for i, line in enumerate(lines):
                if '-->' in line:
                    timestamp_line_index = i
                    break
            
            if timestamp_line_index == -1:
                continue
            
            # Everything after the timestamp line is subtitle text
            subtitle_lines = lines[timestamp_line_index + 1:]
            
            # Clean and join the subtitle lines
            cleaned_lines = []
            for line in subtitle_lines:
                # Remove HTML/XML tags (including <v Instructor>, <i>, etc.)
                clean_line = re.sub(r'<[^>]*>', '', line)
                # Remove subtitle formatting codes like {color} etc.
                clean_line = re.sub(r'\{[^}]*\}', '', clean_line)
                # Remove speaker annotations like [Speaker:] or (Speaker:)
                clean_line = re.sub(r'[\[\(][^:\]]*:[^\]\)]*[\]\)]', '', clean_line)
                # Remove extra whitespace
                clean_line = re.sub(r'\s+', ' ', clean_line).strip()
                if clean_line:
                    cleaned_lines.append(clean_line)
            
            if cleaned_lines:
                # Join multiple lines of the same subtitle with space
                subtitle_text = ' '.join(cleaned_lines)
                extracted_sentences.append(subtitle_text.strip())
        
        # Join all sentences with spaces
        plain_text = ' '.join(extracted_sentences)
        
        # Clean up multiple spaces
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        
        return plain_text
    
    def convert_text(self):
        """Convert the input SRT text to plain text."""
        input_content = self.input_text.get(1.0, tk.END).strip()
        
        if not input_content:
            messagebox.showwarning("Warning", "Please enter SRT text or load a file first.")
            return
        
        try:
            plain_text = self.convert_srt_to_plain_text(input_content)
            
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, plain_text)
            
            if plain_text:
                pass#messagebox.showinfo("Success", "Conversion completed successfully!")
            else:
                messagebox.showwarning("Warning", "No text was extracted. Please check the SRT format.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error during conversion: {str(e)}")
    
    def clear_all(self):
        """Clear all text areas."""
        self.input_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.file_path_var.set("")
    
    def save_output(self):
        """Save the output text to a file."""
        output_content = self.output_text.get(1.0, tk.END).strip()
        
        if not output_content:
            messagebox.showwarning("Warning", "No output text to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save plain text",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(output_content)
                messagebox.showinfo("Success", f"File saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")

def main():
    root = tk.Tk()
    app = SRTConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()