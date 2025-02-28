class RAQAMException(Exception):
    def __init__(self, error, message, status_code, stack_trace=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error = error
        self.stack_trace = stack_trace

class InvalidInputDataException(RAQAMException):
    def __init__(self, message):
        super().__init__(error="Invalid input data", 
                         status_code=400,
                         message=message)
        
class DocumentParsingException(RAQAMException):
    def __init__(self, stack_trace):
        super().__init__(error="Document parsing error", 
                         status_code=401,
                         message="Something went wrong during document parsing",
                         stack_trace=stack_trace)
        
class QuizGenerationException(RAQAMException):
    def __init__(self, stack_trace):
        super().__init__(error="Quiz generation error", 
                         status_code=401,
                         message="Something went wrong during quiz generation",
                         stack_trace=stack_trace)   
        
class FlashcardsGenerationException(RAQAMException):
    def __init__(self, stack_trace):
        super().__init__(error="Flashcards generation error", 
                         status_code=401,
                         message="Something went wrong during flashcards generation",
                         stack_trace=stack_trace)   

class NotImplementedException(RAQAMException):
    def __init__(self):
        super().__init__(error="Quiz generation error", 
                         status_code=402,
                         message="Not implemented yet")     
        
class WebPageException(RAQAMException):
    def __init__(self, message):
        super().__init__(error="WebPageException", 
                         status_code=403,
                         message=message)         
