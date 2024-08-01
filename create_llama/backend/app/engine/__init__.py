import os
from typing import List
from create_llama.backend.app.engine.tools.chains import cri_title_and_meta_chain, cri_tweet_chain, master_prompt_template
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.settings import Settings
from app.engine.index import get_index, get_topic_index
from llama_index.core.llms import ChatMessage
from src.utils.logger import get_logger
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.core.tools import FunctionTool

from pydantic import BaseModel

class FnSchema(BaseModel):
    user_id: str
    input: str

def init_topic_engine():
    index = get_topic_index(data_dir="tmp/csv/topics")

    topic_query_engine = index.as_query_engine(similarity_top_k=3)
    topic_retriever = index.as_retriever(top_k=3)
    return (topic_query_engine, topic_retriever)


async def get_chat_engine(in_research_or_exploration_modality: bool, user_id: str, question: str, thread_id: str, chat_history: str | List[ChatMessage] | None = None):
    # from src.core.dbconfig.postgres import get_db
    top_k = int(os.getenv("TOP_K", "3"))
    system_prompt = os.getenv("SYSTEM_PROMPT")

    index = get_index()
    if index is None:
        raise RuntimeError("Index is not found")

    # tools = ToolFactory.from_env()

    # Use the context chat engine if no tools are provided
    # if len(tools) == 0:
    get_logger().info(f"chat_mode: {in_research_or_exploration_modality}")
    
    if in_research_or_exploration_modality:
        get_logger().info(f"We are research and exploration mode {in_research_or_exploration_modality}")

        return CondensePlusContextChatEngine.from_defaults(
            retriever=index.as_retriever(top_k=top_k),
            system_prompt=system_prompt,
            llm=Settings.llm
        )
    else:
    
        get_logger().info(f"We are not research and exploration mode {in_research_or_exploration_modality}")

        fn_schema_instance = FnSchema(
            thread_id = thread_id,
            user_id = user_id,
            input = question,
        )

        tweet_generation_tool =  FunctionTool.from_defaults(
            fn = cri_tweet_chain,
            async_fn = cri_tweet_chain,
            name = "tweet_generation_tool",
            fn_schema = fn_schema_instance,
            description = """\
                Useful for answering anything related to crafting a perfect tweet that could be used by Edward Conard as a factoid in a media appearance: 
                interesting, backed up with facts, with minimal commentary, and no personal references
            """,
        )

        title_and_meta_description_tool =  FunctionTool.from_defaults(
            fn = cri_title_and_meta_chain,
            async_fn = cri_title_and_meta_chain, 
            fn_schema = fn_schema_instance,            
            name = "title_and_meta_description_tool",
            description = """\
                Helpful for answering anything related to SEO title and SEO meta description that enhance visibility in search engine results pages (SERPs), \
                improve click-through rates (CTR), and drive more organic traffic to the website for a macro-economic related article.
            """,
        )

        topic_query_engine, _ = init_topic_engine()

        topic_suggestion_tool = QueryEngineTool.from_defaults(
            query_engine=topic_query_engine,
            name="topic_generation_tool",
            description="""\
                Helpful for suggesting a class or topics and/or sub-topic for a particular article
            """,
        )

        base_tools = [tweet_generation_tool, title_and_meta_description_tool, topic_suggestion_tool]        

        return OpenAIAgent.from_llm(
            llm=Settings.llm,
            tools=base_tools,
            system_prompt=master_prompt_template,
            verbose=True,  # Show agent logs to console
            chat_history=chat_history,
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
