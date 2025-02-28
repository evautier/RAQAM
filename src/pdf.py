import pymupdf
import pymupdf4llm

class PDFDocument():

    def __init__(self,
                 pdf_file):
        """
        PDF Document from which to extract text and generate chunks.

        @param path: Path to local .pdf file        
        """
        # Opening pdf file
        self.pdf_file = pymupdf.open(stream=pdf_file, filetype="pdf")
    
    def extract_text(self):
        """
        Extracts the text content from the opened pdf file        
        """
        return pymupdf4llm.to_markdown(doc=self.pdf_file)
