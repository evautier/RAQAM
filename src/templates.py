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

retrieval_query = """
Extract detailed and specific content from the document to generate questions.
"""