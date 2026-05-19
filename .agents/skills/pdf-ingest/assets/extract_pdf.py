import os
import sys
import argparse
import pymupdf4llm
from pathlib import Path

def extract_pdf_to_md(pdf_path):
    """
    Extracts text from a PDF file and saves it as a Markdown file
    in the same directory.
    """
    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.exists():
        print(f"Error: File {pdf_path} does not exist.")
        sys.exit(1)

    if pdf_path.suffix.lower() != '.pdf':
        print(f"Error: File {pdf_path} is not a PDF.")
        sys.exit(1)

    print(f"Processing: {pdf_path.name}...")
    
    try:
        # Extract content to markdown
        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        
        # Define output path (same dir, same name, .md extension)
        output_path = pdf_path.with_suffix('.md')
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_text)
            
        print(f"Successfully extracted to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Failed to extract PDF: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract PDF to Markdown")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    
    args = parser.parse_args()
    extract_pdf_to_md(args.pdf_path)
