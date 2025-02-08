from src.raqam import QuizGenerator

from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from src.document import Document
from src.templates import prompt_template, retrieval_query

import requests

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini")

if __name__ == "__main__":
    with open("lotr.txt", 'r') as f:
        text = f.read()
    url = "http://127.0.0.1:5000/generate-quiz"
    payload = {"text_content": text, "nb_questions": 4}
    response = requests.post(url, json=payload)
    print(response.json())
