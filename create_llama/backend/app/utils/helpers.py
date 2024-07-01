from pydantic import BaseModel
import re
from typing import Optional

class BaseArticle(BaseModel):
    headline: str
    publisher: str
    abstract: str

class Article(BaseArticle):
    authors: str

class GeneratorType(BaseArticle):
    publisher_weight: float
    headline_weight: float
    abstract_weight: float


def extract_article_data_from_string(input_string: str) -> Optional[Article]:
    pattern = r'(\w+)={(.*?)}'
    matches = re.findall(pattern, input_string)
    result = {key: value for key, value in matches}

    required_keys = {'headline', 'publisher', 'authors', 'abstract'}
    
    # Check if all required keys are present
    if not required_keys.issubset(result.keys()):
        return None

    return Article(**result)
