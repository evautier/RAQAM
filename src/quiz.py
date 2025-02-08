from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

class MCQuestion(BaseModel):
    """
    Schema for a multiple-choice question with choices, correct answer, and explanation.
    """
    question: str = Field(description="The question being asked.")
    choices: List[str] = Field(description="List of possible choices for the question.")
    answer: str = Field(description="The correct answer to the question.")
    explanation: str = Field(description="Explanation of the correct answer.")

    def to_dict(self):
        return (
            {
                "questionText": self.question,
                "questionAnswer": self.answer,
                "questionChoices": self.choices,
                "answerExplanation": self.explanation
            }
        )

class Quiz(BaseModel):
    """
    Schema for a quiz containing multiple-choice questions
    """
    questions: List[MCQuestion]
    quiz_name: str = Field(description="Name that describes the quiz")

    def __add__(self, other):
        return Quiz(questions=self.questions + other.quuestions)
    
    def to_dict(self):
        return (
            {
                "quizName": self.quiz_name,
                "questionCards": [
                    question.to_dict() for question in self.questions
                ]                
            }
        )
