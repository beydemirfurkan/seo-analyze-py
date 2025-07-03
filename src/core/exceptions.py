from .logger import Logger
import functools

class SEOAnalyzerError(Exception):
    def __init__(self, message="SEO Analyzer Error"):
        self.message = message
        super().__init__(self.message)
        Logger.error(f"SEOAnalyzerError: {message}")

class ConfigurationError(SEOAnalyzerError):
    def __init__(self, message="Configuration Error"):
        super().__init__(f"Configuration Error: {message}")

class NetworkError(SEOAnalyzerError):
    def __init__(self, message="Network Error"):
        super().__init__(f"Network Error: {message}")

class ParsingError(SEOAnalyzerError):
    def __init__(self, message="Parsing Error"):
        super().__init__(f"Parsing Error: {message}")

class APIError(SEOAnalyzerError):
    def __init__(self, message="API Error"):
        super().__init__(f"API Error: {message}")

class ValidationError(SEOAnalyzerError):
    def __init__(self, message="Validation Error"):
        super().__init__(f"Validation Error: {message}")

def handle_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SEOAnalyzerError:
            raise
        except Exception as e:
            Logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise SEOAnalyzerError(f"Unexpected error: {str(e)}")
    return wrapper

class ExceptionHandler:
    @staticmethod
    def handle_network_error(url, error):
        message = f"Cannot connect to URL: {url} - {str(error)}"
        Logger.error(message)
        raise NetworkError(message)
    
    @staticmethod
    def handle_parsing_error(content_type, error):
        message = f"Cannot parse {content_type}: {str(error)}"
        Logger.error(message)
        raise ParsingError(message)
    
    @staticmethod
    def handle_api_error(service, error):
        message = f"{service} API error: {str(error)}"
        Logger.error(message)
        raise APIError(message)
    
    @staticmethod
    def handle_validation_error(field, value, expected):
        message = f"Invalid {field}: {value} (expected: {expected})"
        Logger.error(message)
        raise ValidationError(message) 