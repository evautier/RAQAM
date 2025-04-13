import json
import base64
import traceback

from src.exception import RAQAMException
from src.raqam import QuizGenerator
from src.quiz_config import QuizConfig
from src.utils import load_config

config = load_config()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "https://quiz-tonic.flutterflow.app",  # Or "*" to allow all origins
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Headers": "Content-Type"
}

def lambda_handler(event, context):
    try:
        # Handle preflight CORS request
        if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
            return {
                "statusCode": 204,
                "headers": CORS_HEADERS,
                "body": ""
            }

        # Parsing request body (API Gateway sends body as a string)
        body = json.loads(event["body"])
        print(body)

        # Extract PDF file (Base64 encoded if sent via API Gateway)
        pdf_file = body.get("pdf_file")
        if pdf_file:
            pdf_file = base64.b64decode(pdf_file)  # Decoding Base64 string

        # Extracting data object
        data = body.get("data")
        data["pdf_file"] = pdf_file

        # Initialize Quiz Configuration
        quiz_config = QuizConfig(**config["base_quiz_config"])
        quiz_config.parse_input_data(data)

        # Initialize Quiz Generator
        quiz_generator = QuizGenerator(**quiz_config.__dict__)
        output_data = {}

        # Generate Flashcards (if required)
        if data.get("generate_flashcards"):
            flashcards = quiz_generator.generate_flashcards()
            output_data.update(flashcards.to_dict())

        # Generate Quiz (if number of questions > 0)
        if int(data.get("num_questions", 0)) > 0:
            quiz = quiz_generator.generate_quiz()
            output_data.update(quiz.to_dict())

        # Add Quiz Context
        quiz_context = quiz_generator.get_context()
        output_data["quizContext"] = quiz_context

        return {
            "statusCode": 200,
            "headers": {
                **CORS_HEADERS,
                "Content-Type": "application/json"
            },
            "body": json.dumps(output_data, indent=4, sort_keys=False)
        }

    except RAQAMException as e:
        print(f"Error: {e.message}\nStack Trace: {e.stack_trace}")
        return {
            "statusCode": e.status_code,
            "headers": CORS_HEADERS,
            "body": json.dumps(e.__dict__)
        }

    except Exception as e:
        print(f"Unexpected error: {str(e)}\nStack Trace: {traceback.format_exc()}")
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "InternalServerError", "message": str(e)})
        }
