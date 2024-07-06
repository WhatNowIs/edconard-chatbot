import logging
from create_llama.backend.app.engine.loaders import get_csv_documents
from llama_index.core.indices import VectorStoreIndex
from app.engine.vectordb import get_vector_store
from llama_index.core.settings import Settings
from llama_index.core import ServiceContext


logger = logging.getLogger("uvicorn")


def get_index():
    logger.info("Connecting vector store...")
    store = get_vector_store()
    # Load the index from the vector store
    # If you are using a vector store that doesn't store text,
    # you must load the index from both the vector store and the document store
    index = VectorStoreIndex.from_vector_store(store)
    logger.info("Finished load index from vector store.")
    return index

def get_topic_index(data_dir: str):
    logger.info("Connecting vector store...")
    documents = get_csv_documents(data_dir)
    # Load the index from the vector store
    # If you are using a vector store that doesn't store text,
    service_context = ServiceContext.from_defaults(
        llm=Settings.llm,
        embed_model=Settings.embed_model,
        node_parser=Settings.node_parser,
    )
    # you must load the index from both the vector store and the document store
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)

    logger.info("Finished load index from vector store.")
    return index
