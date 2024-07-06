import datetime
import os
import logging
from create_llama.backend.app import csv_to_pdf, csv_blog_to_pdf
from llama_parse import LlamaParse
from pydantic import BaseModel, validator

logger = logging.getLogger(__name__)

class FileLoaderConfig(BaseModel):
    data_dir: str = "data"
    use_llama_parse: bool = False

    @validator("data_dir")
    def data_dir_must_exist(cls, v):
        if not os.path.isdir(v):
            raise ValueError(f"Directory '{v}' does not exist")
        return v

class CSVLoaderConfig(BaseModel):
    data_dir: str = "tmp/csv/topic"
    use_llama_parse: bool = False
    is_called_on_topic: bool = False

    @validator("data_dir")
    def data_dir_must_exist(cls, v):
        if not os.path.isdir(v):
            raise ValueError(f"Directory '{v}' does not exist")
        return v

def get_file_documents(config: FileLoaderConfig | CSVLoaderConfig):
    from llama_index.core.readers import SimpleDirectoryReader

    try:

        if isinstance(config, CSVLoaderConfig):
            if not os.path.isdir("tmp/converted_csv"):
                os.makedirs("tmp/converted_csv")
                
            file_name = f"{'tmp/converted_csv/' if config.is_called_on_topic else 'data/'}converted_csv_data{str(datetime.datetime.now().timestamp())}.pdf"

            success_message = csv_to_pdf(config.data_dir, file_name) if config.is_called_on_topic else csv_blog_to_pdf(config.data_dir, file_name)

            if success_message is not None:                
                reader = SimpleDirectoryReader(
                    input_files=[file_name],
                    filename_as_id=True,
                )
                return reader.load_data()
            return []

        reader = SimpleDirectoryReader(
            config.data_dir,
            recursive=True,
            filename_as_id=True,
        )
        if config.use_llama_parse:
            parser = llama_parse_parser()
            reader.file_extractor = {".pdf": parser, ".csv": csv_parser}
        else:
            reader.file_extractor = {".csv": csv_parser}
        return reader.load_data()
    except ValueError as e:
        import sys, traceback

        # Catch the error if the data dir is empty
        # and return as empty document list
        _, _, exc_traceback = sys.exc_info()
        function_name = traceback.extract_tb(exc_traceback)[-1].name
        if function_name == "_add_files":
            logger.warning(
                f"Failed to load file documents, error message: {e} . Return as empty document list."
            )
            return []
        else:
            # Raise the error if it is not the case of empty data dir
            raise e