import os
from functools import reduce
from tqdm import tqdm

from langchain.prompts import PromptTemplate

from src.vector_store import VectorStore
from src.quiz import Quiz
from src.utils import get_questions_distribution

class QuizGenerator():
    def __init__(self,
                 text_document,
                 embedding_model,
                 embedding_batch_size,
                 llm,
                 question_prompt_template,
                 retrieval_query,
                 nb_questions,
                 local_vector_store_path=None):
        """
        Quiz generator working with retrieval on .pdf embedded content. 
        
        @param text_document: Text Document for which to generate quiz
        @param embedding_model: Model for embeddings to use for vector store
        @param embedding_batch_size: Batch size for embeddings generation
        @param llm: Langchain LLM to use for text generation (ex: llm = OpenAI(model="gpt-4-turbo"))
        @param question_prompt_template: Prompt template to use to generate question on content
        @param retrieval_query: Query to use to extract relevant content for quiz generation
        @param nb_questions: Number of questions to generate for this quiz 
        @param local_vector_store_path: Path where to save vector store to avoid multiplying embeddings generation
        """
        # Setting-up class attributes
        self.text_document = text_document
        self.embedding_model = embedding_model
        self.embedding_batch_size = embedding_batch_size
        self.llm = llm.with_structured_output(schema=Quiz)
        self.question_prompt_template = question_prompt_template
        self.retrieval_query = retrieval_query
        self.nb_questions = nb_questions
        self.local_vector_store_path = local_vector_store_path
        # Performing embedding on text document's text chunks if necessary (will be None if only one chunk)
        self.vector_store = self.create_vector_store()
    
    def create_vector_store(self):
        """
        Creates a vector store and performs embedding on document text chunks if necessary               
        """
        if len(self.text_document.text_chunks) > self.nb_questions:
            # Defining vector store and storing text chunks using embedding
            vector_store = VectorStore(embedding_model=self.embedding_model,
                                       embedding_batch_size=self.embedding_batch_size,
                                       local_vector_store_path=self.local_vector_store_path)
            if self.local_vector_store_path is None or not os.path.exists(self.local_vector_store_path):
                print("Creating embeddings from extracted chunks and storing into vector store")
                vector_store.add_embedded_chunks(chunks=self.text_document.text_chunks)
            # Saving vector store in local
            if self.local_vector_store_path:
                vector_store.save_vector_store(path=self.local_vector_store_path)
            return vector_store

    def generate_question(self,
                          content,
                          nb_questions=1):
        """
        Generates a multiple choice question based on the provided content.

        @param nb_questions: Number of questions to generate on this specific content
        @param content: Content for which to generate a question        
        """
        # Building prompt using prompt template and content
        prompt = PromptTemplate(input_variables=["nb_questions", "content"], template=self.question_prompt_template)
        formatted_prompt = prompt.format(nb_questions=nb_questions, content=content)        
        # Generating question using LLM
        response = self.llm.invoke(formatted_prompt)
        return response

    def generate_quiz(self):
        """
        Generates a quiz on the stored .pdf document with prompt template using langchain retrieval chain.
        """
        # Performing retrieval on full document to find relevant content for questions
        if self.vector_store:
            print("Extracting relevant chunks from embedded document")
            relevant_content = self.vector_store.find_relevant_chunks(query=self.retrieval_query,
                                                                      k=self.nb_questions)
            # Generating question for each content that has been found
            print("Generating questions from relevant content")
            quiz = [self.generate_question(content=content.page_content) for content in tqdm(relevant_content, desc="Generating questions")]
        else:
            relevant_content = self.text_document.text_chunks   
            questions_distribution = get_questions_distribution(nb_text_chunks=len(relevant_content), nb_questions=self.nb_questions) 
            quiz = [self.generate_question(nb_questions=questions_distribution[i], content=content) for i, content in tqdm(enumerate(relevant_content), desc="Generating questions") if questions_distribution[i] > 0]          
    
        return reduce(lambda x, y: x+y, quiz)
