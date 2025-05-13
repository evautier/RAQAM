import os
import traceback
from functools import reduce
from tqdm import tqdm

from langchain.prompts import PromptTemplate

from src.exception import QuizGenerationException, FlashcardsGenerationException, InvalidInputDataException, NotImplementedException
from src.document import Document
from src.web_page import WebPage
from src.pdf import PDFDocument
from src.vector_store import VectorStore
from src.quiz import Quiz, FlashCards
from src.utils import get_questions_distribution, count_tokens

model_costs = {
    "gpt-4o-mini": {"input": 0.075, "output": 0.600},
    "text-embedding-3-small": {"input": 0.020}
}

class QuizGenerator():
    def __init__(self,
                 llm,
                 embedding_model,
                 embedding_batch_size,
                 min_text_length,
                 chunk_size,
                 chunk_overlap,
                 question_prompt_template,
                 flashcards_prompt_template,
                 retrieval_query,
                 num_questions,
                 num_choices=None,
                 text_content=None,
                 url=None,
                 youtube_url=None,
                 pdf_file=None,
                 video_file=None,
                 local_vector_store_path=None):
        """
        Quiz generator working with retrieval on .pdf embedded content. 
        
        @param llm: Langchain LLM to use for text generation (ex: llm = OpenAI(model="gpt-4-turbo"))
        @param embedding_model: Model for embeddings to use for vector store
        @param embedding_batch_size: Batch size for embeddings generation
        @param min_text_length: Minimum text length to generate quiz
        @param chunk_size: Size of chunk for text treatment
        @param chunk_overlap: Number of characters for chunk overlap
        @param question_prompt_template: Prompt template to use to generate question on content
        @param flashcards_prompt_template: Prompt template to use to generate flashcards on content
        @param retrieval_query: Query to use to extract relevant content for quiz generation
        @param num_questions: Number of questions to generate for this quiz
        @param num_choices: Number of choices to generate per question
        @param text_content: Text content to use for quiz generation
        @param url: URL for which to extract text for quiz generation
        @param youtube_url: URL for a youtube video from which to extract content
        @param pdf_filepath: Filepath to .pdf file for which to extract text for quiz generation
        @param video_filepath: Filepath to video file from which to extract content
        @param local_vector_store_path: Path where to save vector store to avoid multiplying embeddings generation
        """
        # Setting-up class attributes
        self.quiz_llm = llm.with_structured_output(schema=Quiz)
        self.flaschards_llm = llm.with_structured_output(schema=FlashCards)
        self.embedding_model = embedding_model
        self.embedding_batch_size = embedding_batch_size
        self.min_text_length = min_text_length
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.question_prompt_template = question_prompt_template
        self.flashcards_prompt_template = flashcards_prompt_template
        self.retrieval_query = retrieval_query
        self.num_questions = num_questions
        self.num_choices = num_choices
        self.text_content = text_content if text_content != '' else None
        self.url = url if url != '' else None
        self.youtube_url = youtube_url if youtube_url != '' else None
        self.pdf_file = pdf_file
        self.video_file = video_file
        self.local_vector_store_path = local_vector_store_path
        # Saving generation data
        self.model_name = llm.model_name
        self.embedding_model_name = embedding_model.model
        self.prompts_tokens = 0
        self.responses_tokens = 0
        self.embeddings_tokens = 0
        # Building text document from input sources (text content > url > pdf filepath)
        self.build_text_document()
        # Performing embedding on text document's text chunks if necessary (will be None if only one chunk)
        self.vector_store = self.create_vector_store()

    def build_text_document(self):
        """
        Builds text document from input sources (text content > url > pdf filepath) 
        """
        sources_arguments = ["text_content", "url", "youtube_url", "pdf_file", "video_file"]
        if not any([arg_value is not None for arg_value in sources_arguments]):
            raise InvalidInputDataException(message=f"Must provide at least one data source argument")
        if self.text_content is not None:
            text_contents = [self.text_content]
            self.content_source = "text"
        elif self.url is not None:
            web_page = WebPage(url=self.url)
            text_contents = [web_page.extract_text()]
            self.content_source = "web_page"
        elif self.youtube_url is not None:
            raise NotImplementedException()
        elif self.pdf_file is not None:
            pdf_document = PDFDocument(pdf_file=self.pdf_file)
            text_contents = [pdf_document.extract_text()]
            self.content_source = "pdf_file"
        elif self.video_file is not None:
            raise NotImplementedException()            
        # Building text document from extracted text content
        self.text_document = Document(text_data=text_contents, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)

    
    def get_context(self):
        """
        Builds a dictionnary containing informations about quiz generation        
        """
        # Calculating costs foe every request on api
        self.prompts_cost = (self.prompts_tokens / 1e6) * model_costs[self.model_name]["input"]
        self.responses_cost = (self.responses_tokens / 1e6) * model_costs[self.model_name]["output"]
        self.embeddings_cost = (self.embeddings_tokens / 1e6) * model_costs[self.embedding_model_name]["input"]
        self.total_cost = self.prompts_cost + self.responses_cost + self.embeddings_cost
        return {
            "contentSource": self.content_source,
            "contentLength": self.text_document.content_length,
            "chunkSize": self.text_document.chunk_size,
            "chunkOverlap": self.text_document.chunk_overlap,
            "nbChunks": len(self.text_document.text_chunks),
            "generationModelName": self.model_name,
            "embeddingModelName": self.embedding_model_name,
            "hasEmbeddedChunks": self.vector_store is not None,
            "tokens": {
                "prompts": self.prompts_tokens,
                "responses": self.responses_tokens,
                "embeddings": self.embeddings_tokens,
                "total": self.prompts_tokens + self.responses_tokens + self.embeddings_tokens 
            },
            "costs": {
                "prompts": f"{round(self.prompts_cost, 6):.6f} $",
                "responses": f"{round(self.responses_cost, 6):.6f} $",
                "embeddings": f"{round(self.embeddings_cost, 6):.6f} $",
                "total": f"{round(self.total_cost, 6):.6f} $"
            }
        }

    def create_vector_store(self):
        """
        Creates a vector store and performs embedding on document text chunks if necessary               
        """
        if self.num_questions > 0 and len(self.text_document.text_chunks) > self.num_questions:
            # Defining vector store and storing text chunks using embedding
            vector_store = VectorStore(embedding_model=self.embedding_model,
                                       embedding_batch_size=self.embedding_batch_size,
                                       local_vector_store_path=self.local_vector_store_path)
            if self.local_vector_store_path is None or not os.path.exists(self.local_vector_store_path):
                print("Creating embeddings from extracted chunks and storing into vector store")
                vector_store.add_embedded_chunks(chunks=self.text_document.text_chunks)
                # Adding input tokens for embedding
                self.embeddings_tokens += sum([count_tokens(chunk, self.embedding_model_name) for chunk in self.text_document.text_chunks])
            # Saving vector store in local
            if self.local_vector_store_path:
                vector_store.save_vector_store(path=self.local_vector_store_path)
            return vector_store

    def generate_question(self,
                          content,
                          num_questions=1):
        """
        Generates a multiple choice question based on the provided content.

        @param num_questions: Number of questions to generate on this specific content
        @param content: Content for which to generate a question        
        """
        # Building prompt using prompt template and content
        prompt = PromptTemplate(input_variables=["num_questions", "content"], template=self.question_prompt_template)
        formatted_prompt = prompt.format(num_questions=num_questions, content=content)        
        # Generating question using LLM
        response = self.quiz_llm.invoke(formatted_prompt)
        # Adding generated token for input and output
        self.prompts_tokens += count_tokens(text=formatted_prompt, model=self.model_name)
        self.responses_tokens += count_tokens(text=response.json(), model=self.model_name)
        return response

    def generate_quiz(self):
        """
        Generates a quiz on the stored document with prompt template using langchain retrieval chain.
        """
        # Performing retrieval on full document to find relevant content for questions
        try:
            if self.vector_store:
                print("Extracting relevant chunks from embedded document")
                relevant_content = self.vector_store.find_relevant_chunks(query=self.retrieval_query,
                                                                          k=self.num_questions)
                # Generating question for each content that has been found
                print("Generating questions from relevant content")
                quiz = [self.generate_question(content=content.page_content) for content in tqdm(relevant_content, desc="Generating questions")]
            else:
                relevant_content = self.text_document.text_chunks  
                questions_distribution = get_questions_distribution(nb_text_chunks=len(relevant_content), num_questions=self.num_questions) 
                quiz = [self.generate_question(num_questions=questions_distribution[i], content=content) for i, content in tqdm(enumerate(relevant_content), desc="Generating questions") if questions_distribution[i] > 0]          
            quiz = reduce(lambda x, y: x+y, quiz) 
            # Randomizing questions and choices questions in order to avoid redondancy
            quiz.randomize()
            return quiz       
        except Exception as e:
            raise QuizGenerationException(stack_trace=traceback.format_exc())

    def generate_flashcards_on_content(self,
                                       content):
        """
        Generate one or several flashcards on a specific content.

        @param content: Content for which to generate flashcards on        
        """        
        # Building prompt using prompt template and content
        prompt = PromptTemplate(input_variables=["content"], template=self.flashcards_prompt_template)
        formatted_prompt = prompt.format(content=content)        
        # Generating question using LLM
        response = self.flaschards_llm.invoke(formatted_prompt)
        # Adding generated token for input and output
        self.prompts_tokens += count_tokens(text=formatted_prompt, model=self.model_name)
        self.responses_tokens += count_tokens(text=response.json(), model=self.model_name)
        return response        

    def generate_flashcards(self):
        """
        Generates flashcards on the stored document with prompt template.        
        """
        try:
            flashcards = [self.generate_flashcards_on_content(content=chunk) for chunk in tqdm(self.text_document.text_chunks, desc="Generating flashcards on content")]
            flashcards = reduce(lambda x,y: x+y, flashcards)
            return flashcards
        except Exception as e:
            raise FlashcardsGenerationException(stack_trace=traceback.format_exc())        
