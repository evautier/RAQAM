import fitz  # PyMuPDF
import re
from collections import defaultdict

def extract_pdf_structure(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    
    # Initialize structure
    structure = defaultdict(lambda: defaultdict(list))  # Chapter -> Section -> Text Blocks
    
    # Define regex patterns for chapters and sections
    chapter_pattern = re.compile(r"^Chapter\s\d+|^\d+\.\s.*")
    section_pattern = re.compile(r"^\d+\.\d+.*")
    
    current_chapter = None
    current_section = None
    
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]  # Extract text blocks
        for block in blocks:
            # Extract text and bounding box
            text = " ".join([line["spans"][0]["text"] for line in block.get("lines", [])])
            bbox = block["bbox"]
            if block["lines"]:
                font_size = block["lines"][0]["spans"][0]["size"]
                font_flags = block["lines"][0]["spans"][0]["flags"]  # Bold/Italic info
                
                # Detect chapters
                if chapter_pattern.match(text):
                    current_chapter = text
                    current_section = None
                    structure[current_chapter]["_metadata"] = {"page": page_num, "font_size": font_size}
                    continue
                
                # Detect sections
                if section_pattern.match(text) and current_chapter:
                    current_section = text
                    structure[current_chapter][current_section] = {"page": page_num, "font_size": font_size}
                    continue
                
                # Associate text blocks
                if current_chapter:
                    if current_section:
                        structure[current_chapter][current_section].setdefault("text_blocks", []).append(text)
                    else:
                        structure[current_chapter].setdefault("text_blocks", []).append(text)
        
    return structure


# Path to PDF
pdf_file = "louro_optics.pdf"

# Extract structure
pdf_structure = extract_pdf_structure(pdf_file)

# Output structure
import json
print(json.dumps(pdf_structure, indent=4))
