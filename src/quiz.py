from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
import random

from src.utils import shuffle_with_mapping

class MCQuestion(BaseModel):
    """
    Schema for a multiple-choice question with choices, correct answer, and explanation.
    """
    question: str = Field(description="The question being asked.")
    choices: List[str] = Field(description="List of possible choices for the question.")
    answer_index: int = Field(description="Index of the correct answer to the question.")
    explanation: str = Field(description="Explanation of the correct answer.", default="Default explanation")

    def to_dict(self):
        return (
            {
                "questionText": self.question,
                "questionAnswerIndex": self.answer_index,
                "questionChoices": self.choices,
                "answerExplanation": self.explanation
            }
        )

class Quiz(BaseModel):
    """
    Schema for a quiz containing multiple-choice questions
    """
    questions: List[MCQuestion]
    quiz_name: str = Field(description="Name that describes the quiz", default="Default quiz name")

    def __add__(self, other):
        return Quiz(questions=self.questions + other.questions,
                    quiz_name=self.quiz_name)
    
    def to_dict(self):
        return (
            {
                "quizName": self.quiz_name,
                "questionCards": [
                    question.to_dict() for question in self.questions
                ]                
            }
        )
    
    def randomize(self):
        # Randomizing order of questions
        random.shuffle(self.questions)
        # Randomizing order of choices for each questions
        for i in range(len(self.questions)):
            shuffled_choices, mapping = shuffle_with_mapping(self.questions[i].choices)
            self.questions[i].choices = shuffled_choices[:]  
            self.questions[i].answer_index = mapping[self.questions[i].answer_index]

class FlashCard(BaseModel):
    """
    Schema for a flashcard about a specific subject
    """
    front: str = Field(description="The front of the card. A term, a notion or a question.")
    back: str = Field(description="The back of the card. A definition, an explanation or an answer.")

class FlashCards(BaseModel):
    """
    Schema for list of flashcards about a document subjects.
    """
    flashcards: List[FlashCard]

    def __add__(self, other):
        return FlashCards(flashcards=self.flashcards + other.flashcards)
    
    def to_dict(self):
        return (
            {
                "flashcards": [flashcard.__dict__ for flashcard in self.flashcards]
            }
        )