import typing
from create_llama.backend.app.utils.doc_processor import process_table_data
from fastapi import HTTPException
from pydantic import BaseModel
import re
from typing import Optional
from src.core.services.gcp import docs_service
from src.schema import Document, DocumentResponse

class BaseArticle(BaseModel):
    headline: str
    publisher: str
    abstract: str

class Article(BaseArticle):
    authors: str
    url: str
    order: int

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

def process_table_contents(data):
    def process_table_cell(cell):
        for p in cell['content']:
            if any('inlineObjectElement' in element for element in p['paragraph']['elements']):
                return {'content': [process_image(p) for p in cell['content']]}
            
        return {'content': [process_paragraph(p) for p in cell['content']]}


    def process_image(paragraph):
        elements = paragraph['paragraph']['elements']
        processed_elements = []

        for element in elements:
            if 'inlineObjectElement' in element:
                processed_element = {
                    'inlineObjectElement': element['inlineObjectElement']
                }
                processed_elements.append(processed_element)
            elif 'textRun' in element:  # To handle textRuns in image paragraphs
                processed_element = process_text_run(element)
                processed_elements.append(processed_element)

        return {
            'elements': processed_elements,
        }

    def process_paragraph(paragraph):
        elements = paragraph['paragraph']['elements']
        return {
            'elements': [process_text_run(e) for e in elements],
        }

    def process_text_run(element):
        if 'textRun' in element:
            return {
                'textRun': {
                    'content': element['textRun']['content'],
                    'textStyle': element['textRun']['textStyle']
                }
            }
        return element

    processed_tables = []
    tables = [item.get('table') for item in data if 'table' in item]

    for item in tables:
        processed_table = {
            'tableRows': [
                {'tableCells': [process_table_cell(cell) for cell in row['tableCells']]}
                for row in item['tableRows']
            ],
        }
        processed_tables.append(processed_table)

    return processed_tables


async def get_document(document_id: str) -> typing.List[Document]:
    document = docs_service.documents().get(documentId=document_id).execute()

    title = document.get('title')
    body = document.get('body')
    content = body.get('content')

    # New code to extract image URLs
    inline_objects = document.get('inlineObjects', {})

    documents: typing.List[Document] = []

    processed_table_data = process_table_contents(content)

    for processed_data in processed_table_data:
        document = Document(title=title, content=content, inline_objects=inline_objects)
        document.content = processed_data
        documents.append(document)

    return documents




async def get_document_by_url(url: str) -> typing.List[DocumentResponse]:
    match = re.search(r'document/d/([a-zA-Z0-9-_]+)/edit', url)
    if match is None:
        raise HTTPException(status_code=404, detail="Document id not found in the URL")

    document_id = match.group(1)
    
    if not document_id:
        # Correct way to raise HTTPException
        raise HTTPException(status_code=404, detail="Document not found")

    docs_data  = await get_document(document_id)

    response: typing.List[DocumentResponse] = []

    for doc in docs_data:
        table_rows_data = doc.content['tableRows']
        document_response = process_table_data(table_rows_data)
        
        if(document_response.headline != '' and document_response.authors != ''
           and document_response.publication != '' and document_response.summary != ''):

            response.append(document_response)


    return response