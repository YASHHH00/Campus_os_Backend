import logging
from pythonjsonlogger import jsonlogger
from config import settings

def setup_logging():
    logger = logging.getLogger()
    
    # Use setting level, fallback to INFO
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Remove default handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # Add JSON handler
    logHandler = logging.StreamHandler()
    # Define fields to include
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s',
        rename_fields={
            "levelname": "level",
            "asctime": "timestamp"
        }
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    # Suppress verbose loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
