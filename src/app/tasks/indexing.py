import os
import shutil
import logging
from create_llama.backend.app.engine.generate import generate_datasource


logger = logging.getLogger("uvicorn")


def index_all():
    # Just call the generate_datasource from create_llama for now
    generate_datasource()


def reset_index():
    """
    Reset the index by removing the vector store data and STORAGE_DIR then re-indexing the data.
    """

    def reset_index_chroma():
        from chromadb import PersistentClient

        # Todo: Consider using other method to clear the vector store data
        chroma_path = os.getenv("CHROMA_PATH")
        collection_name = os.getenv("CHROMA_COLLECTION", "default")
        collection_img_name = os.getenv("CHROMA_IMG_COLLECTION", "image_collection")
        chroma_client = PersistentClient(path=chroma_path)

        if chroma_client.get_or_create_collection(collection_name):
            logger.info(f"Removing collection {collection_name}")
            chroma_client.delete_collection(collection_name)

        if chroma_client.get_or_create_collection(collection_img_name):
            logger.info(f"Removing collection {collection_img_name}")
            chroma_client.delete_collection(collection_img_name)

    def reset_index_qdrant():
        from create_llama.backend.app.engine.vectordbs.qdrant import get_vector_store

        store, image_store = get_vector_store()
        # Delete previously created store
        store.client.delete_collection(
            store.collection_name,
        )
        image_store.client.delete_collection(
            image_store.collection_name,
        )

        # # Recreate new stores for images and for texts
        store._create_collection(
            collection_name=store.collection_name,
            vector_size=int(os.getenv("EMBEDDING_DIM", 1536)),
        )
        image_store._create_collection(
            collection_name=image_store.collection_name,
            vector_size=int(os.getenv("EMBEDDING_DIM", 1536)),
        )

    vector_store_provider = os.getenv("VECTOR_STORE_PROVIDER", "chroma")
    if vector_store_provider == "chroma":
        reset_index_chroma()
    elif vector_store_provider == "qdrant":
        reset_index_qdrant()
    else:
        raise ValueError(f"Unsupported vector provider: {vector_store_provider}")

    # Remove STORAGE_DIR
    storage_context_dir = os.getenv("STORAGE_DIR")
    logger.info(f"Removing {storage_context_dir}")
    if os.path.exists(storage_context_dir):
        shutil.rmtree(storage_context_dir)

    # Run the indexing
    index_all()
