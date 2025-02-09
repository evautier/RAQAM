from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from src.exception import InvalidInputDataException
from src.templates import question_prompt_template, retrieval_query
from src.utils import read_yaml

config = read_yaml("config.yaml")

class QuizConfig():
    def __init__(self,
                 model_name,
                 embdeddings_model_name,
                 embedding_batch_size,
                 min_text_length,
                 chunk_size,
                 chunk_overlap,
                 local_vector_store_path):
        # Setting up configuration attrivutes
        self.embedding_batch_size = embedding_batch_size
        self.min_text_length = min_text_length
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.question_prompt_template = question_prompt_template
        self.retrieval_query = retrieval_query
        self.local_vector_store_path = local_vector_store_path
        # Building LLM and embeddings models
        self.llm = ChatOpenAI(model=model_name)
        self.embedding_model = OpenAIEmbeddings(model=embdeddings_model_name)
    
    def parse_input_data(self,
                         data):
        """
        Parses input data from request to add into quiz configuration

        @param data: Input data to parse into quiz configuration
        """
        # Setting up data source arguments
        arg_values = [data.get(arg) for arg in config["query_source_arguments"]]
        if not any([arg_value is not None for arg_value in arg_values]):
            raise InvalidInputDataException(message=f"Must provide at least one data source argument")
        for arg, arg_value in zip(config["query_source_arguments"], arg_values):
            self.__setattr__(arg, arg_value)
        # Setting up settings arguments
        for arg in config["query_settings_arguments"]:
            arg_value = data.get(arg)
            if not arg_value:
                raise InvalidInputDataException(message=f"Must provide {arg} argument")
            self.__setattr__(arg, arg_value)
        # Checking if settings arguments are parsable and > 0
        for arg in config["forced_positive_arguments"]:
            try:
                arg_value = int(self.__getattribute__(arg))
            except Exception as e:
                raise InvalidInputDataException(message=f"Couldn't parse {arg} to integer")
            if not arg_value > 0:
                raise InvalidInputDataException(message=f"Argument {arg} must be strictly positive")
            self.__setattr__(arg, arg_value)
