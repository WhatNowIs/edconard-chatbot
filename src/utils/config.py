from dotenv import load_dotenv
import os
from utils.logger import get_logger

load_dotenv()
logger = get_logger()

def get_config(name):
    try:
        value = os.getenv(name)
        if value is None:
            logger.error(f"Environment variable {name} not configured")
            raise Exception(f"Environment variable {name} not configured")
        
        return str(value)
    except Exception as e:
        logger.error(f"Failed to get environment variable {name} with error: {str(e)}")
        raise Exception(f"Failed to get environment variable {name} with error: {str(e)}")