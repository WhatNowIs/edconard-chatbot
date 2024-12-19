import os

from qdrant_client import AsyncQdrantClient, QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore


def get_vector_store():
    collection_name = os.getenv("QDRANT_COLLECTION")
    # img_collection_name = os.getenv("QDRANT_IMG_COLLECTION")
    # get qdrant url and api key
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")

    # if not collection_name or not img_collection_name:
    #     raise ValueError(
    #         "Please set QDRANT_COLLECTION, QDRANT_IMG_COLLECTION"
    #         " to your environment variables or config them in the .env file"
    #     )
    
    aclient = AsyncQdrantClient(        
        url=url,
        api_key=api_key,        
    )
    
    client = QdrantClient(        
        url=url,
        api_key=api_key,
    )
    # create 2 stores, one for texts and another one for images
    default_store = QdrantVectorStore(
        client=client,
        aclient=aclient,
        collection_name=collection_name,
        max_retries=3
    )
    
    # image_store = QdrantVectorStore(
    #     client=client,
    #     aclient=aclient,
    #     # collection_name=img_collection_name,
    #     max_retries=3
    # )

    return default_store
