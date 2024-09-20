import os
import json
import time
from create_llama.backend.app.utils.schema import BatchResult
import openai
import requests
from typing import List

openai.api_key = os.getenv("OPENAI_API_KEY")
# Send the request to OpenAI API
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_batch_file(image_urls: List[str], batch_file_path: str):
    """
    Creates a .jsonl batch file for the image processing requests.
    
    :param image_urls: List of image URLs.
    :param batch_file_path: Path to save the batch .jsonl file.
    :return: Path to the batch .jsonl file.
    """
    with open(batch_file_path, 'w') as batch_file:
        for i, image_url in enumerate(image_urls):
            request_data = {
                "custom_id": f"request-{i+1}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Please extract relevant information from the image and provide a great summary"},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_url}
                                }
                            ]
                        }
                    ],
                    "max_tokens": 1000
                }
            }
            batch_file.write(json.dumps(request_data) + '\n')
    
    return batch_file_path

def upload_batch_file(file_path: str):
    """
    Uploads the batch file to OpenAI API.

    :param file_path: Path to the batch .jsonl file.
    :return: Uploaded file ID.
    """
    with open(file_path, 'rb') as file:
        response = client.files.create(file=file, purpose="batch")
        return response.id

def create_image_batch(batch_file_id: str):
    """
    Creates a batch for image processing based on the uploaded batch file.
    
    :param batch_file_id: The file ID of the uploaded batch file.
    :return: The created batch object.
    """
    batch = client.batches.create(
        input_file_id=batch_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",  # Adjust as needed
        metadata={"description": "Image content summary batch"}
    )
    return batch

def check_batch_status(batch_id: str):
    """
    Checks the status of the batch.

    :param batch_id: The ID of the batch.
    :return: The current batch status.
    """
    batch_status = openai.batches.retrieve(batch_id)
    return batch_status

def download_batch_results(batch_id: str, output_file_name: str):
    """
    Downloads the results of the batch once completed.
    
    :param batch_id: The ID of the batch.
    :return: Parsed list of results.
    """
    batch_status = check_batch_status(batch_id)
    
    if batch_status.status == 'completed':
        output_file_id = batch_status.output_file_id
                
        result_file = client.files.retrieve(output_file_id)

        content = client.files.content(result_file.id).content
        
        with open(output_file_name, 'wb') as file:
            file.write(content)        
    else:
        print(f"Batch {batch_id} is still in progress or has failed.")

    return output_file_name

def read_stored_batch_result(result_file_name: str) -> List[BatchResult]:
    results: List[BatchResult] = []
    with open(result_file_name, 'r') as file:
        for line in file:
            # Parsing the JSON string into a dict and appending to the list of results
            json_object = json.loads(line.strip())
            results.append(json_object)

    return results

def process_images_in_batch(image_urls: List[str], output_txt_file: str, batch_file_path: str = 'images/image_batch.jsonl'):
    """
    Executes the entire process of creating a batch file, uploading it, creating a batch,
    checking the batch status, downloading results, and saving them to a txt file.

    :param image_urls: List of image URLs to process.
    :param output_txt_file: Path to the output .txt file where the results will be saved.
    :param batch_file_path: Path for the batch .jsonl file.
    """
    create_batch_file(image_urls, batch_file_path)
    batch_file_id = upload_batch_file(batch_file_path)

    batch = create_image_batch(batch_file_id)
    print(f"Batch created with ID: {batch.id}")

    # Wait for batch completion by checking status repeatedly
    while True:
        batch_status = check_batch_status(batch.id)
        print(f"Batch status: {batch_status.status}")
        if batch_status.status == 'completed':
            break
        elif batch_status.status == 'failed':
            print("Batch failed to process.")
            return
        time.sleep(10) 

    # 5. Retrieve results once completed
    output_file_name = download_batch_results(batch.id, output_txt_file)
    final_result = read_stored_batch_result(output_file_name)

    final_results_data = []

    for index, result in enumerate(final_result):
        generated_summarie = result['response']['body']['choices'][0]['message']['content']
        summary_file = f"images/{image_urls[index]['folder_name']}/image_description.txt"

        with open(summary_file, "w") as summary_file_data:
            summary_file_data.write(generated_summarie)
        
        final_results_data.append({
            'featured_image_url': image_urls[index],
            'summary': generated_summarie,
            'summary_file': summary_file
        })

    return final_results_data

def get_image_content_summary(image_urls: List[str], batch_size: int = 5, max_tokens: int = 2048):
    """
    Sends image URLs in batches to OpenAI GPT-4 Vision API and returns key takeaways.

    :param image_urls: List of image URLs.
    :param batch_size: Number of images to send in each batch.
    :param max_tokens: Maximum tokens for the response.
    :return: List of takeaways for each image.
    """
    takeaways = []

    # Batch the image URLs
    for i in range(0, len(image_urls), batch_size):
        batch = image_urls[i:i+batch_size]
        # Send the request to OpenAI API                

        for image_url in batch:
            try:
                response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's in this image?"},
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                        },
                    ],
                    }
                ],
                max_tokens=500,
                )

                # Extract the response content
                summary = response.choices[0].message.content
                takeaways.append({"image_url": image_url, "summary": summary})

            except requests.exceptions.RequestException as e:
                print(f"Error processing image {image_url}: {e}")
                takeaways.append({"image_url": image_url, "summary": "Error processing image"})

    return takeaways