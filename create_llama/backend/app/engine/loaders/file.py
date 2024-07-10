import datetime
import os
import logging
from create_llama.backend.app import csv_to_pdf, macro_roundup_preprocessor, process_blog_articles
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
    is_blog_post: bool = False
    is_macroroundup: bool = False

    @validator("data_dir")
    def data_dir_must_exist(cls, v):
        if not os.path.isdir(v):
            raise ValueError(f"Directory '{v}' does not exist")
        return v


def llama_parse_parser():
    if os.getenv("LLAMA_CLOUD_API_KEY") is None:
        raise ValueError(
            "LLAMA_CLOUD_API_KEY environment variable is not set. "
            "Please set it in .env file or in your shell environment then run again!"
        )
    parser = LlamaParse(result_type="markdown", verbose=True, language="en")
    return parser


def get_file_documents(config: FileLoaderConfig | CSVLoaderConfig):
    from llama_index.core.readers import SimpleDirectoryReader

    try:
        if isinstance(config, CSVLoaderConfig):
            if not os.path.isdir("tmp/converted_csv"):
                os.makedirs("tmp/converted_csv")
                                
            if config.is_called_on_topic:
                logger.info(f"Loading predefined topics")
                file_name = f"tmp/converted_csv"
                output_files = csv_to_pdf(config.data_dir, file_name)
                             
                reader = SimpleDirectoryReader(
                    input_files=output_files,
                    filename_as_id=True,
                )
                return reader.load_data()
                
            elif not config.is_called_on_topic and (config.is_blog_post or config.is_macroroundup):
                macro_files = macro_roundup_preprocessor(f"{config.data_dir}/macro_roundup", "data")
                blog_post_files = process_blog_articles(f"{config.data_dir}/blog_post", "data")

                logger.info(f"Macro Roundup files: {macro_files}")
                # logger.info(f"Blog Post files: {blog_post_files}")

                output_files = blog_post_files + macro_files             
                reader = SimpleDirectoryReader(
                    input_files=output_files,
                    filename_as_id=True,
                )
                logger.info(f"Loading {len(output_files)} both Macro Roundup and Blog Post files")
                return reader.load_data()


        reader = SimpleDirectoryReader(
            config.data_dir,
            recursive=True,
            filename_as_id=True,
        )
        if config.use_llama_parse:
            parser = llama_parse_parser()
            reader.file_extractor = {".pdf": parser}
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