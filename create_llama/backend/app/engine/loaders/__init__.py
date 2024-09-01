import os
import yaml
import logging
from create_llama.backend.app.engine.loaders.file import CSVLoaderConfig, FileLoaderConfig, get_file_documents
from create_llama.backend.app.engine.loaders.web import WebLoaderConfig, get_web_documents
from create_llama.backend.app.engine.loaders.db import DBLoaderConfig, get_db_documents

logger = logging.getLogger(__name__)


def load_configs():
    with open("config/loaders.yaml") as f:
        configs = yaml.safe_load(f)
    return configs


def get_documents():
    documents = []
    config = load_configs()
    for loader_type, loader_config in config.items():
        logger.info(
            f"Loading documents from loader: {loader_type}, config: {loader_config}"
        )
        match loader_type:
            case "file":
                document = get_file_documents(FileLoaderConfig(**loader_config))
            case "web":
                document = get_web_documents(WebLoaderConfig(**loader_config))
            case "db":
                document = get_db_documents(
                    configs=[DBLoaderConfig(**cfg) for cfg in loader_config]
                )
            case "csv":                
                data_dir = "tmp/csv"
                if not os.path.isdir(data_dir):
                    os.makedirs(data_dir)

                loader_config = CSVLoaderConfig(
                    **loader_config, 
                    data_dir="tmp/csv", 
                    is_called_on_topic=False, 
                    is_macroroundup=True, 
                    is_blog_post=True
                )
                
                document = get_file_documents(config=loader_config)
            case _:
                raise ValueError(f"Invalid loader type: {loader_type}")
        documents.extend(document)

    return documents

def get_csv_documents(data_dir: str):
    documents = []
    config = load_configs()
    for loader_type, loader_config in config.items():
        logger.info(
            f"Loading documents from loader: {loader_type}, config: {loader_config}"
        )
        if loader_type == "csv":
            document = get_file_documents(
                config=CSVLoaderConfig(**loader_config, data_dir=data_dir, is_called_on_topic=True)
            )
            documents.extend(document)

    return documents
