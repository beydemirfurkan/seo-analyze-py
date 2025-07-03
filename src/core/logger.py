import logging
import os
from datetime import datetime
from pathlib import Path

class Logger:
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        log_filename = f"seo_analyzer_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = logs_dir / log_filename
        
        self._logger = logging.getLogger("seo_analyzer")
        self._logger.setLevel(logging.INFO)
        
        if not self._logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)
    
    def get_logger(self):
        return self._logger
    
    @classmethod
    def info(cls, message):
        logger = cls().get_logger()
        logger.info(message)
    
    @classmethod
    def warning(cls, message):
        logger = cls().get_logger()
        logger.warning(message)
    
    @classmethod
    def error(cls, message):
        logger = cls().get_logger()
        logger.error(message)
    
    @classmethod
    def debug(cls, message):
        logger = cls().get_logger()
        logger.debug(message)
    
    @classmethod
    def critical(cls, message):
        logger = cls().get_logger()
        logger.critical(message) 