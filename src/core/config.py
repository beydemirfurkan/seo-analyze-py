import os
from dotenv import load_dotenv
from .exceptions import ConfigurationError

load_dotenv()

class Config:
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    
    LLM_MODEL = os.getenv('LLM_MODEL', 'meta-llama/llama-3.3-70b-instruct:free')
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '5'))
    INITIAL_DELAY = int(os.getenv('INITIAL_DELAY', '3'))
    
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', '5000'))
    MAX_HEADINGS = int(os.getenv('MAX_HEADINGS', '10'))
    MAX_IMAGES = int(os.getenv('MAX_IMAGES', '10'))
    MAX_LINKS = int(os.getenv('MAX_LINKS', '10'))
    
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'comprehensive_seo_analysis.json')
    
    MIN_TITLE_LENGTH = int(os.getenv('MIN_TITLE_LENGTH', '30'))
    MAX_TITLE_LENGTH = int(os.getenv('MAX_TITLE_LENGTH', '60'))
    MIN_META_DESC_LENGTH = int(os.getenv('MIN_META_DESC_LENGTH', '120'))
    MAX_META_DESC_LENGTH = int(os.getenv('MAX_META_DESC_LENGTH', '160'))
    
    @classmethod
    def validate_config(cls):
        if not cls.OPENROUTER_API_KEY or cls.OPENROUTER_API_KEY == "":
            raise ConfigurationError("OpenRouter API key .env dosyasında OPENROUTER_API_KEY olarak ayarlanmamış!")
        
        if not cls.OPENROUTER_API_KEY.startswith('sk-or-v1-'):
            raise ConfigurationError("Geçersiz OpenRouter API key formatı! 'sk-or-v1-' ile başlamalı.")
        
        return True
    
    @classmethod
    def get_api_url(cls, endpoint="chat/completions"):
        base_url = cls.OPENROUTER_BASE_URL.rstrip('/')
        return f"{base_url}/{endpoint}" 