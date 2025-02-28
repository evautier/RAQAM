question_prompt_template = """
You are a helpful assistant. Based on the following content, generate {num_questions} detailed multiple-choice questions that tests understanding of the material. 

Content:
{content}

Make the questions specific and ensure it relates directly to the provided material. Include:
- A question
- Four choices (one correct and three plausible distractors)
- The correct answer
- An explanation

Provide a general quiz name about this content
"""

flashcards_prompt_template = """
You are a helpful assistant. Based on the following content, generate flashcards to summarize the main subjects. 
A flashcard can be either a term with its definition or an important notion with an explanation.
You can generate up to 4 flashcards.

Content:
{content}

For each flashcard, include :
- The front of the card : the term, the notion or the question
- The back of the card : the definition, the explanation or the answer
"""

retrieval_query = """
Extract detailed and specific content from the document to generate questions.
"""