from src.raqam import QuizGenerator
from src.document import Document
from src.quiz_config import QuizConfig
from src.utils import load_config

# Loading models

config = load_config()

if __name__ == "__main__":
    with open("lotr.txt", 'r') as f:
        text_content = f.read()
    quiz_config = QuizConfig(**config["base_quiz_config"])       
    quiz_config.parse_input_data({"text_content": text_content, "num_questions": 4, "num_choices": 4}) 
    quiz_generator = QuizGenerator(**quiz_config.__dict__)
    quiz = quiz_generator.generate_quiz()
    quiz_context = quiz_generator.get_context()
    print(quiz.json())
