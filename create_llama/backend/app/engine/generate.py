import re
from create_llama.backend.app.engine.index import get_topic_index
from dotenv import load_dotenv
from src.core.services.gcp import store_spreadsheet

load_dotenv()

import os
import logging
from llama_index.core.settings import Settings
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage import StorageContext
from create_llama.backend.app.settings import init_settings
from create_llama.backend.app.engine.loaders import get_documents
from create_llama.backend.app.engine.vectordb import get_vector_store


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

STORAGE_DIR = os.getenv("STORAGE_DIR", "storage")

def get_doc_store():

    # If the storage directory is there, load the document store from it.
    # If not, set up an in-memory document store since we can't load from a directory that doesn't exist.
    if os.path.exists(STORAGE_DIR):
        return SimpleDocumentStore.from_persist_dir(STORAGE_DIR)
    else:
        return SimpleDocumentStore()


def run_pipeline(docstore, vector_store, documents):
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(
                chunk_size=Settings.chunk_size,
                chunk_overlap=Settings.chunk_overlap,
            ),
            Settings.embed_model,
        ],
        docstore=docstore,
        docstore_strategy="upserts_and_delete",
        vector_store=vector_store,
    )

    # Run the ingestion pipeline and store the results
    nodes = pipeline.run(show_progress=True, documents=documents)

    return nodes


def persist_storage(docstore, vector_store):
    storage_context = StorageContext.from_defaults(
        docstore=docstore,
        vector_store=vector_store,
    )
    storage_context.persist(STORAGE_DIR)


def generate_datasource():
    init_settings()

    logger.info("Getting speadsheet which contains topics and subtopics data")
    topics_speadsheet_url = "https://docs.google.com/spreadsheets/d/1hW-vUFcWBM40MZpbSwqLsWVgtel0Z2Aj-3hffNX3VXc/edit"
    match = re.search(r'spreadsheets/d/([a-zA-Z0-9-_]+)/edit', topics_speadsheet_url)

    spreadsheet_id = match.group(1)

    store_spreadsheet(spreadsheet_id)

    logger.info("Generate index for the provided data")

    # Get the stores and documents or create new ones
    documents = get_documents()
    docstore = get_doc_store()
    vector_store = get_vector_store()


    # Run the ingestion pipeline
    _ = run_pipeline(docstore, vector_store, documents)

    # Build the index and persist storage
    persist_storage(docstore, vector_store)

    logger.info("Finished generating the index")



if __name__ == "__main__":
    generate_datasource()
