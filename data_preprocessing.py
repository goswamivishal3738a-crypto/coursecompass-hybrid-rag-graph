import os
import fitz  # PyMuPDF library for PDF extraction
import pandas as pd
import re

def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a given PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def clean_text(text):
    """Cleans the extracted text by removing extra whitespaces and newlines."""
    text = re.sub(r'\n+', ' ', text)  # Replace multiple newlines with a single space
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text.strip()

def chunk_text(text, source_name, chunk_size=100):
    """Divides the text into smaller passages (chunks) for better semantic search."""
    words = text.split()
    chunks = []
    # Create chunks of approximately 'chunk_size' words
    for i in range(0, len(words), chunk_size):
        chunk_text = " ".join(words[i:i+chunk_size])
        chunks.append({
            "source_document": source_name,
            "text_passage": chunk_text
        })
    return chunks

def process_corpus(data_directory):
    """Main function to process all PDFs in the data directory and save to CSV."""
    all_passages = []
    
    # Iterate through all files in the data folder
    for filename in os.listdir(data_directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(data_directory, filename)
            print(f"Processing document: {filename}...")
            
            # 1. Extract
            raw_text = extract_text_from_pdf(file_path)
            # 2. Clean
            cleaned_text = clean_text(raw_text)
            # 3. Chunk
            passages = chunk_text(cleaned_text, source_name=filename)
            all_passages.extend(passages)
            
    # Save the structured passages to a CSV file for the next modules
    if all_passages:
        df = pd.DataFrame(all_passages)
        output_file = os.path.join(data_directory, "processed_corpus.csv")
        df.to_csv(output_file, index=False)
        print(f"\nSUCCESS: Extracted and cleaned {len(df)} passages.")
        print(f"Data saved to: {output_file}")
    else:
        print("No PDF files found to process.")

if __name__ == "__main__":
    # Specify the folder containing the syllabus PDFs
    DATA_DIR = "data"
    process_corpus(DATA_DIR)