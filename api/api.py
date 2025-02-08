from flask import Flask, request, jsonify, render_template

from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from src.raqam import QuizGenerator
from src.document import Document
from src.templates import prompt_template, retrieval_query

# Loading models
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini")

app = Flask(__name__)

@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    # Isolating query parameters
    data = request.get_json()
    text_content = data.get("text_content")
    nb_questions = int(data.get("num_questions"))
    nb_choices = int(data.get("num_choices"))
    # Generating quiz with RAQAM
    text_document = Document(text_data=[text_content], chunk_size=2000, chunk_overlap=100)
    quiz_generator = QuizGenerator(text_document=text_document,
                                   embedding_model=embeddings,
                                   embedding_batch_size=10,
                                   llm=llm,
                                   question_prompt_template=prompt_template,
                                   retrieval_query=retrieval_query,
                                   nb_questions=nb_questions,
                                   local_vector_store_path=None)
    quiz = quiz_generator.generate_quiz()
    return jsonify(quiz.to_dict())  

@app.route("/quiz-sandbox")
def quiz_sandbox():
    return render_template("quiz_sandbox.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
