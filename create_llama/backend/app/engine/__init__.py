import os
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.settings import Settings
from create_llama.backend.app.engine.index import get_index, get_topic_index
from llama_index.core.agent import AgentRunner
from llama_index.core.tools.query_engine import QueryEngineTool

from pydantic import BaseModel

class FnSchema(BaseModel):
    user_id: str
    input: str

def init_topic_engine():
    index = get_topic_index(data_dir="tmp/csv/topics")

    topic_query_engine = index.as_query_engine(similarity_top_k=3)
    topic_retriever = index.as_retriever(top_k=3)
    return (topic_query_engine, topic_retriever)


async def get_chat_engine():
    # from src.core.dbconfig.postgres import get_db
    top_k = int(os.getenv("TOP_K", "6"))
    system_prompt = os.getenv("SYSTEM_PROMPT")

    index = get_index()
    if index is None:
        raise RuntimeError("Index is not found")
    
    # if in_research_or_exploration_modality:
    return CondensePlusContextChatEngine.from_defaults(
        retriever=index.as_query_engine(similarity_top_k=top_k),
        system_prompt=system_prompt,
        llm=Settings.llm
    )
    # else:
    #     # Add the query engine tool to the list of tools
    #     query_engine_tool = QueryEngineTool.from_defaults(
    #         query_engine=index.as_query_engine(similarity_top_k=top_k),
    #     )
    #     tools.append(query_engine_tool)
    #     return AgentRunner.from_llm(
    #         llm=Settings.llm,
    #         tools=tools,
    #         system_prompt=system_prompt,
    #         verbose=True,  # Show agent logs to console
    #     )
