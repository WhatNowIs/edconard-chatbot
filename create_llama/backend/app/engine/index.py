import logging
# from llama_index.core.settings import Settings
from create_llama.backend.app.engine.vectordb import get_vector_store
from llama_index.core.indices import VectorStoreIndex


logger = logging.getLogger("uvicorn")


def get_index():
    logger.info("Connecting vector store...")
    store = get_vector_store()
    # Load the index from the vector store
    # you must load the index from both the vector store and the document store
    index = VectorStoreIndex.from_vector_store(
        vector_store=store, 
        # image_vector_store=image_store, 
        # embed_model=Settings.embed_model
    )
    logger.info("Finished load index from vector store.")
    return index