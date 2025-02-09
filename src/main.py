from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from src.raqam import QuizGenerator
from src.document import Document
from src.templates import prompt_template, retrieval_query

# Loading models
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini")

if __name__ == "__main__":
    with open("story.txt", 'r') as f:
        text_content = f.read()
    text_document = Document(text_data=[text_content], chunk_size=2000, chunk_overlap=100)
    quiz_generator = QuizGenerator(content_source="text",
                                   text_document=text_document,
                                   embedding_model=embeddings,
                                   embedding_batch_size=10,
                                   llm=llm,
                                   question_prompt_template=prompt_template,
                                   retrieval_query=retrieval_query,
                                   nb_questions=4,
                                   local_vector_store_path="faiss_vector_store")
    quiz = quiz_generator.generate_quiz()
    quiz_context = quiz_generator.get_context()
    print(quiz.json())
