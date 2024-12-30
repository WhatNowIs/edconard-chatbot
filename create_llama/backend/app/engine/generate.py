import os
import logging
from typing import List, Generator
from dotenv import load_dotenv
from llama_index.core.schema import Document
from llama_index.core.settings import Settings
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage import StorageContext
from create_llama.backend.app.engine.loaders import get_documents
from create_llama.backend.app.engine.vectordb import get_vector_store
import gc

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

STORAGE_DIR = os.getenv("STORAGE_DIR", "storage")
# Reduced batch size to prevent memory issues
MAX_BATCH_SIZE = 1000
# Number of nodes to process before forcing garbage collection
GC_THRESHOLD = 5000

def get_doc_store():
    if os.path.exists(STORAGE_DIR):
        return SimpleDocumentStore.from_persist_dir(STORAGE_DIR)
    else:
        return SimpleDocumentStore()

def batch_documents(documents: List[Document], batch_size: int) -> Generator[List[Document], None, None]:
    """Split documents into smaller batches and yield them one at a time."""
    for i in range(0, len(documents), batch_size):
        yield documents[i:i + batch_size]

def create_pipeline(docstore, vector_store) -> IngestionPipeline:
    """Create an ingestion pipeline with memory-efficient settings."""
    return IngestionPipeline(
        transformations=[
            SentenceSplitter(
                chunk_size=Settings.chunk_size,
                chunk_overlap=Settings.chunk_overlap,
            ),
            Settings.embed_model,
        ],
        docstore=docstore,
        docstore_strategy="upserts",
        vector_store=vector_store,
    )

def process_batch(pipeline: IngestionPipeline, doc_batch: List[Document], batch_num: int, total_batches: int) -> List:
    """Process a single batch of documents with error handling and logging."""
    try:
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(doc_batch)} documents)")
        batch_nodes = pipeline.run(show_progress=True, documents=doc_batch)
        return batch_nodes
    except Exception as e:
        logger.error(f"Error processing batch {batch_num}: {str(e)}")
        # Log more details about the failing batch
        logger.error(f"Batch size: {len(doc_batch)}")
        logger.error(f"First document metadata: {doc_batch[0].metadata if doc_batch else 'No documents'}")
        raise

def run_pipeline(docstore, vector_store, documents: List[Document]) -> List:
    """Run the pipeline with improved memory management."""
    pipeline = create_pipeline(docstore, vector_store)
    all_nodes = []
    node_count = 0
    document_batches = list(batch_documents(documents, MAX_BATCH_SIZE))
    total_batches = len(document_batches)

    for i, doc_batch in enumerate(document_batches, 1):
        batch_nodes = process_batch(pipeline, doc_batch, i, total_batches)
        all_nodes.extend(batch_nodes)
        node_count += len(batch_nodes)

        # Periodically persist and cleanup memory
        if node_count >= GC_THRESHOLD:
            persist_storage(docstore, vector_store)
            gc.collect()  # Force garbage collection
            node_count = 0
            logger.info("Performed interim storage persistence and memory cleanup")

    return all_nodes

def persist_storage(docstore, vector_store):
    """Persist storage with error handling."""
    try:
        storage_context = StorageContext.from_defaults(
            docstore=docstore,
            vector_store=vector_store,
        )
        storage_context.persist(STORAGE_DIR)
        logger.info("Successfully persisted storage")
    except Exception as e:
        logger.error(f"Error persisting storage: {str(e)}")
        raise

def generate_datasource():
    """Main function to generate the datasource with memory optimization."""
    logger.info("Starting index generation for provided data")
    
    try:
        documents = get_documents()
        logger.info(f"Loaded {len(documents)} documents")
        
        docstore = get_doc_store()
        vector_store = get_vector_store()

        nodes = run_pipeline(docstore, vector_store, documents)
        persist_storage(docstore, vector_store)

        logger.info(f"Successfully generated index with {len(nodes)} nodes")
        return nodes
    except MemoryError:
        logger.error("Memory error encountered. Try reducing MAX_BATCH_SIZE or increasing system memory")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_datasource: {str(e)}")
        raise
    finally:
        gc.collect()  # Final cleanup

if __name__ == "__main__":
    generate_datasource()