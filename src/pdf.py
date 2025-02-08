from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from utils import preprocess_text

class PDFDocument():

    def __init__(self,
                 path):
        """
        PDF Document from which to extract text and generate chunks.

        @param path: Path to local .pdf file        
        """
        self.path = path
        # Loading .pdf file into a PyPDF reader
        self.reader = PyPDFLoader(path)

    def extract_text(self):
        """
        Loads the .pdf file and extracts the content of the pages into a str object
        """
        text = ""
        for page in self.reader.lazy_load():
            cleaned_text = preprocess_text(page.page_content)
            text += cleaned_text + "\n"
        return text
    
    def split_pdf_into_chunks(self,
                              chunk_size=500,
                              chunk_overlap=50):
        """
        Splits the loaded .pdf text into chunks of specified size

        @param chunk_size: Size of chunk in which to split the .pdf text
        @param chunk_overlap: Size of text that is overlaping between chunks        
        """
        # Extracting text from pdf
        text = self.extract_text()
        # Defining splitter 
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        # Splitting text into chunks and storing results
        self.text_chunks = text_splitter.split_text(text)
        return self.text_chunks

# PDF ANALTSIS : TO DO
# 1. Extraction des blocs de textes et identification des caractéristiques (police, taille, gras, italique, etc...)
#    Association des blocs successifs de même nature (pour simplifier les traitements). Détection de la nautre de
#    texte correspondant au contenu (le plus fréquent ?) 
# 2. Détection d'une potentielle table of content
# 3. Détection des blocs correspondant aux titres de chapitres, sections, etc... à partir de la police et des patternes
#    qui se répêtent.
# 4. Elaboration de la hiérarchie et de la structure du document. Ordre des chapitres, sous-chapitres, etc..
# 5. Association des blocs de textes aux différentes sections.
# 6. Créations des chunks à encoder -> sections si suffisamment petites, séparation en plusieurs chunks etc..