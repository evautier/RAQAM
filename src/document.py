import traceback

from langchain.text_splitter import RecursiveCharacterTextSplitter

from functools import reduce

from src.exception import DocumentParsingException

class Document():
    def __init__(self,
                 text_data: list[str],
                 chunk_size: int=500,
                 chunk_overlap: int=50):
        """
        A document that is defined by its text content. Input data may be a list of texts in the
        case where a pre-split can be performed on original text.

        @param text_data: List of texts to feed as input for text document
        """
        # Defining class attributes
        self.text_data = text_data
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.content_length = sum([len(text) for text in text_data])
        # Defining text splitter to use
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        # Splitting input text data into chunks of text
        try:
            self.text_chunks = self.split_text_data_into_chunks(text_data=text_data)
            print(self.text_chunks)
        except Exception as e:
            raise DocumentParsingException(stack_trace=traceback.format_exc())

    def split_text_into_chunks(self,
                               text):
        """
        Splits a text (str) in chunks of text of size chunk_size and with an overlap of chunk_overlap
        characters

        @param text: Str text to split into chunks
        """
        return self.text_splitter.split_text(text)

    def split_text_data_into_chunks(self,
                                    text_data):
        """
        Splits text data into chunks of text. If text data is initially splitted (len(text_data) > 0) then
        splits the text for each original part.

        @param text_data: List of texts to split  
        """
        return reduce(lambda x,y: x+y, [self.split_text_into_chunks(text) for text in text_data])
