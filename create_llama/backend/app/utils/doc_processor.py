from typing import Any, List
from src.schema import DocumentResponse


def get_cell_content(cell):
    """Extract content from a cell."""
    return cell['content']

def get_elements_from_content(content):
    """Extract elements from content."""
    return [element for c in content for element in c.get('elements', [])]

def is_matching_text_run(element, text):
    """Check if the element is a textRun matching the given text."""
    return str(element.get('textRun', {}).get('content', '')).replace("\n", "").strip() == text

def find_value_cell(row, current_cell_index):
    """Find the cell that follows the current cell in the row."""
    value_cell_index =  current_cell_index + 1

    if value_cell_index < len(row.get('tableCells', [])):
        return row['tableCells'][value_cell_index]
    
    return None


def get_extracted_results(value_cell, text_runs, is_hyperlink):
    for value_content in value_cell:
        for value_elem in value_content['elements']:
            if 'textRun' in value_elem:
                if is_hyperlink:
                    text_style = value_elem['textRun'].get('textStyle', {})
                    has_text_link = 'link' in text_style
                    is_text_run_contains_data =  'hyperlink' in text_runs and len(text_runs['hyperlink']) > 0
                    value = value_elem['textRun']['content']

                    if has_text_link:
                        hyperlink = f"<a href=\"{str(text_style.get('link', {}).get('url')).strip()}\">{value}</a>"                            
                        text_runs = {
                            'text': f"{text_runs['text']}{value}" if is_text_run_contains_data else value,
                            'hyperlink': (f"{text_runs['hyperlink']}{hyperlink}" ) if is_text_run_contains_data else hyperlink
                        }               
                    else:
                        text_runs = {
                            'text': f"{text_runs['text']} {value}" if is_text_run_contains_data else value,
                            'hyperlink': (f"{text_runs['hyperlink']}{value}" ) if is_text_run_contains_data else value
                        }
                else:
                    text_runs = {
                        'text': f"{text_runs['text'] if 'text' in text_runs else ''}{value_elem['textRun']['content']}"
                    }

    return text_runs


def find_text_run(data, element_name, is_tweet=False):
    """
    Find the textRun objects for a given element name.

    :param data: The JSON data representing the table rows.
    :param element_name: The name of the element to find.
    :return: The content of the value cell corresponding to the element name.
    """

    search_results = []
    result: Any = None

    for row in data:
        for current_cell_index, cell in enumerate(row.get('tableCells', [])):
            content = get_cell_content(cell)
            # print(cell)
            elements = get_elements_from_content(content)
            for element in elements:
                if is_matching_text_run(element, element_name):
                    value_cell = find_value_cell(row, current_cell_index)
                    if value_cell:
                        result = get_cell_content(value_cell)
                        if not is_tweet:
                            return result
                        else:                            
                            search_results.append(result)

    return search_results

def extract_text(data, search_text, is_hyperlink=False, is_tweet=False) -> dict:
    """
    Extract text content from a textRun object.

    :param data: The JSON data representing the table rows.
    :param search_text: The text to search for in the textRun objects.
    :param is_hyperlink: Whether to extract hyperlink information.
    :return: A dictionary containing the extracted text content.
    """
    results = find_text_run(data, search_text, is_tweet=is_tweet)

    if len(results) == 0:
        return None

    text_runs: dict = {}

    tweet_runs: List[dict] = []
    
    if is_tweet:
        for value_cell in results:
            text_runs = {}
            text_runs = get_extracted_results(value_cell=value_cell, text_runs=text_runs, is_hyperlink=False)
            
            tweet_runs.append(text_runs)
    else:
        text_runs = get_extracted_results(value_cell=results, text_runs=text_runs, is_hyperlink=is_hyperlink)


    return text_runs if not is_tweet else tweet_runs

def extract_document_headlines(data, value_search, is_tweet:bool = False) -> str | None:
    result = extract_text(data=data, search_text=value_search, is_tweet=is_tweet)

    if result is not None and not is_tweet and 'text' in result:
        return result['text']
    elif is_tweet:
        return result

    return  None

def convert_to_html(data, search_text) -> str:
    processed_data = find_text_run(data, search_text)
    html_output = ''

    for paragraph in processed_data:
        paragraph_html = ''
        for element in paragraph['elements']:
            text_run = element.get('textRun')
            if text_run:
                content = text_run.get('content', '')
                content = content.replace('\n', '') 
                paragraph_html += content

        if paragraph_html.strip():
            html_output += f'{paragraph_html.strip()}'

    return html_output


def process_table_data(table_rows_data) -> DocumentResponse:

    document_headline = extract_document_headlines(
        table_rows_data, 'Headline*') 
    
    authors = extract_document_headlines(table_rows_data, 'Author(s)*')

    publication = extract_document_headlines(table_rows_data, 'Publication*')
    
    order_of_appearance = extract_document_headlines(table_rows_data, 'Order of Appearance')

    publication = extract_document_headlines(table_rows_data, 'Publication*')
    
    summary = convert_to_html(table_rows_data, 'Summary*')

    document_response = DocumentResponse(
        headline=document_headline.strip() if document_headline else '', 
        summary=summary.strip() if summary else '',
        authors=authors.strip() if authors else '',
        publication=publication.strip() if publication else '',
        order_of_appearance=order_of_appearance.strip() if order_of_appearance else '',
    )

    return document_response