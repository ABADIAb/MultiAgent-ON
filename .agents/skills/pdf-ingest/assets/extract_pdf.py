import os
import sys
import argparse
import pymupdf4llm
from pathlib import Path
import re

def clean_teams_transcript(md_text, title):
    """Detects and cleans MS Teams transcript exports."""
    # Heuristic to detect MS Teams transcript
    if "intentionally omitted" not in md_text and "Transcripción de la reunión" not in md_text and "started transcription" not in md_text:
        return md_text # Not a Teams transcript, return as is

    md_text = re.sub(r'\*\*==> picture.*?intentionally omitted <==\*\*\n?', '', md_text)
    md_text = re.sub(r'\*\*.*?\*\* started transcription\n?', '', md_text)
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)
    md_text = re.sub(r'^## \*\*(.*?)\*\*', r'**\1**', md_text, flags=re.MULTILINE)
    
    lines = md_text.split('\n')
    new_lines = []
    participants = set()
    
    speaker_pattern = re.compile(r'^\*\*(.*?)\*\*\s+(\d+:\d{2})(?:\s+(.*))?$')
    in_speech = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_speech:
                new_lines.append('')
            continue
            
        match = speaker_pattern.match(line)
        if match:
            speaker = match.group(1).strip()
            timestamp = match.group(2).strip()
            speech_text = match.group(3)
            
            participants.add(speaker)
            new_lines.append(f"**{speaker}** [{timestamp}]:")
            in_speech = True
            
            if speech_text and speech_text.strip():
                new_lines.append(f"> {speech_text.strip()}")
        else:
            if in_speech and not line.startswith('#'):
                if 'Transcripción' in line or ('May ' in line and '20' in line):
                    continue
                new_lines.append(f"> {line}")
                
    participants_md = "\n".join([f"- **{p}**" for p in sorted(participants) if p])
    
    yaml_header = f"""---
title: "{title}"
date: YYYY-MM-DD
tags: [transcription, meeting]
status: completed
---

# Meeting Transcript: {title}

**Participants:**
{participants_md}

**Context:** Automatically ingested Teams transcription.

---

## Transcript

"""
    return yaml_header + '\n'.join(new_lines) + '\n'

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
        
        # Apply MS Teams transcript cleanup if applicable
        md_text = clean_teams_transcript(md_text, pdf_path.stem)
        
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
