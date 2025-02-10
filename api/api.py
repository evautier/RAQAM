from flask import Flask, request, jsonify, render_template, Response
import json

from src.exception import RAQAMException
from src.raqam import QuizGenerator
from src.quiz_config import QuizConfig
from src.utils import load_config, read_yaml, save_yaml

app = Flask(__name__)

config = load_config()

@app.errorhandler(RAQAMException)
def handle_api_error(error):
    response = jsonify({"error": error.error, "message": error.message, "stack_trace": error.stack_trace})
    response.status_code = error.status_code
    return response

@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    # Isolating query parameters
    data = request.get_json()    
    print(data)
    quiz_config = QuizConfig(**config["base_quiz_config"])
    quiz_config.parse_input_data(data)
    # Parsing document 
    quiz_generator = QuizGenerator(**quiz_config.__dict__)
    quiz = quiz_generator.generate_quiz()
    quiz_context = quiz_generator.get_context()
    output_data = {**quiz.to_dict(), **{"quizContext": quiz_context}}
    return Response(json.dumps(output_data, indent=4, sort_keys=False), mimetype="application/json")

@app.route("/quiz-sandbox")
def quiz_sandbox():
    return render_template("quiz_sandbox.html")

@app.route("/get-config", methods=["GET"])
def get_config():    
    return Response(json.dumps(config["base_quiz_config"], indent=4, sort_keys=False), mimetype="application/json")

@app.route("/get-default-config", methods=["GET"])
def get_default_config():    
    default_config = read_yaml("config/default_config.yaml")
    return Response(json.dumps(default_config["base_quiz_config"], indent=4, sort_keys=False), mimetype="application/json")

@app.route("/set-custom-config", methods=["POST"])
def set_custom_config():    
    custom_settings = request.get_json()
    config["base_quiz_config"] = custom_settings    
    save_yaml(config, "config/custom_config.yaml")
    return Response(json.dumps(config["base_quiz_config"], indent=4, sort_keys=False), mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
