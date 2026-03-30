import os
import fitz  # PyMuPDF
import re
from docx import Document

def clean_psych_text(text):
    """Specific filters for Psychology textbooks and Children's literature."""
    # 1. Remove Citations like (Author, Year) or (Author et al., Year)
    text = re.sub(r'\([A-Z][a-z]+(?: et al\.)?,\s\d{4}\)', '', text)
    
    # 2. Remove textbook boilerplate (ISBN, Copyright, Publisher info)
    noise_patterns = [
        r'ISBN[:\s]*[\d\-xX]+', 
        r'Copyright\s*©.*', 
        r'All rights reserved',
        r'Printed in.*',
        r'Library of Congress.*',
        r'www\.[a-z0-9\.]+'
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # 3. Remove Page Headers/Footers (usually short lines with digits)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that look like page numbers or are too short to be meaningful prose
        if re.match(r'^\d+$', stripped) or len(stripped) < 15:
            continue
        cleaned_lines.append(stripped)
    
    return " ".join(cleaned_lines)

def process_to_chunks(input_folder, output_file, chunk_size=1500):
    valid_exts = ('.pdf', '.docx')
    all_text = ""

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(valid_exts): continue
        file_path = os.path.join(input_folder, filename)
        print(f"Reading: {filename}")
        
        try:
            current_file_text = ""
            if filename.endswith(".pdf"):
                with fitz.open(file_path) as doc:
                    for page in doc:
                        current_file_text += page.get_text("text") + " "
            elif filename.endswith(".docx"):
                doc = Document(file_path)
                current_file_text = " ".join([p.text for p in doc.paragraphs if p.text.strip()])
            
            all_text += clean_psych_text(current_file_text) + " <|endoftext|> "
        except Exception as e:
            print(f"Error {filename}: {e}")

    # Sliding Window Chunking: This prevents the model from memorizing short segments
    words = all_text.split()
    with open(output_file, "w", encoding="utf-8") as f:
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            f.write(chunk + "\n")

if __name__ == "__main__":
    process_to_chunks("phsyc_data", "cleaned_dataset.txt")