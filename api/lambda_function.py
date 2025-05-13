import json
import base64
import traceback

from src.exception import RAQAMException
from src.raqam import QuizGenerator
from src.quiz_config import QuizConfig
from src.utils import load_config

config = load_config()


ALLOWED_ORIGINS = [
    "https://quiz-tonic.flutterflow.app",
    "http://quiztonic.app"
]

CORS_HEADERS_BASE = {
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Headers": "Content-Type"
}

def get_cors_headers(event):
    """Dynamically set CORS headers based on request Origin."""
    origin = event.get("headers", {}).get("origin") or event.get("headers", {}).get("Origin")
    headers = CORS_HEADERS_BASE.copy()
    if origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
    return headers


def lambda_handler(event, context):
    try:
        cors_headers = get_cors_headers(event)

        # Handle preflight CORS request
        if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
            return {
                "statusCode": 204,
                "headers": cors_headers,
                "body": ""
            }

        # Parsing request body (API Gateway sends body as a string)
        body = json.loads(event["body"])
        data = body.get("data")

        print({key: value for key, value in data.items() if key != "pdf_file"})

        pdf_file = data.get("pdf_file")
        if pdf_file:
            pdf_file = base64.b64decode(pdf_file)

        data["pdf_file"] = pdf_file

        quiz_config = QuizConfig(**config["base_quiz_config"])
        quiz_config.parse_input_data(data)

        quiz_generator = QuizGenerator(**quiz_config.__dict__)
        output_data = {}

        if data.get("generate_flashcards"):
            flashcards = quiz_generator.generate_flashcards()
            output_data.update(flashcards.to_dict())

        if int(data.get("num_questions", 0)) > 0:
            quiz = quiz_generator.generate_quiz()
            output_data.update(quiz.to_dict())

        quiz_context = quiz_generator.get_context()
        output_data["quizContext"] = quiz_context

        return {
            "statusCode": 200,
            "headers": {
                **cors_headers,
                "Content-Type": "application/json"
            },
            "body": json.dumps(output_data, indent=4, sort_keys=False)
        }

    except RAQAMException as e:
        print(f"Error: {e.message}\nStack Trace: {e.stack_trace}")
        return {
            "statusCode": e.status_code,
            "headers": cors_headers,
            "body": json.dumps(e.__dict__)
        }

    except Exception as e:
        print(f"Unexpected error: {str(e)}\nStack Trace: {traceback.format_exc()}")
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": "InternalServerError", "message": str(e)})
        }