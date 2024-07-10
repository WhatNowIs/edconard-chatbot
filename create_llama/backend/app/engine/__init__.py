import os
from typing import List
from create_llama.backend.app.engine.tools.prompt import MasterPrompt
from create_llama.backend.app.utils.helpers import Article
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.settings import Settings
from app.engine.tools import ToolFactory
from app.engine.index import get_index, get_topic_index
from llama_index.core.llms import ChatMessage
from src.utils.logger import get_logger
from llama_index.core.agent import AgentRunner
from llama_index.core.tools import RetrieverTool
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.tools.query_engine import QueryEngineTool


def init_topic_engine():
    index = get_topic_index(data_dir="tmp/csv/topics")

    topic_query_engine = index.as_query_engine(similarity_top_k=3)
    topic_retriever = index.as_retriever(top_k=3)
    return (topic_query_engine, topic_retriever)


async def get_chat_engine(chat_mode: bool, data: Article | None = None, chat_history: str | List[ChatMessage] = None):
    # from src.core.dbconfig.postgres import get_db
    top_k = int(os.getenv("TOP_K", "3"))
    system_prompt = os.getenv("SYSTEM_PROMPT")

    index = get_index()
    if index is None:
        raise RuntimeError("Index is not found")

    tools = ToolFactory.from_env()

    # Use the context chat engine if no tools are provided
    if len(tools) == 0:
        get_logger().info(f"chat_mode: {chat_mode}")
        
        if chat_mode:
            get_logger().info(f"We are research and exploration mode {chat_mode}")

            return CondensePlusContextChatEngine.from_defaults(
                retriever=index.as_retriever(top_k=top_k),
                system_prompt=system_prompt,
                llm=Settings.llm
            )
        
        summarization_tool =  QueryEngineTool.from_defaults(
            query_engine=index.as_query_engine(),
            name="article_summary_enhancement_tool",
            description="""\
                Helpful for optimizing the summary of the article, ensuring it is clear, concise, and grammatically correct
            """,
        )

        tweet_generation_tool =  QueryEngineTool.from_defaults(
            query_engine=index.as_query_engine(),
            name="tweet_generation_tool",
            description="""\
                Useful for crafting a perfect tweet could be used by Ed as a factoid in a media appearance: 
                interesting, backed up with facts, with minimal commentary, and no personal references
            """,
        )

        title_and_meta_description_tool =  QueryEngineTool.from_defaults(
            query_engine=index.as_query_engine(),
            name="title_and_meta_description_tool",
            description="""\
                Helpful for generating an article title and its meta description for search engine optimization (SEO)
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

        base_tools = [tweet_generation_tool, topic_suggestion_tool, summarization_tool, title_and_meta_description_tool]

        system_prompt = MasterPrompt.format_prompt_template(
            abstract=data.abstract,
            headline=data.headline,
            abstract_weight=0.6,
            headline_weight=0.2,
        )
        

        return AgentRunner.from_llm(
            llm=Settings.llm,
            tools=base_tools,
            system_prompt=str(system_prompt),
            verbose=True,  # Show agent logs to console
            chat_history=chat_history,
        )

        # return CondensePlusContextChatEngine.from_defaults(
        #     retriever=topic_retriever,
        #     llm=Settings.llm,
        #     chat_history=chat_history,
        #     system_prompt=system_prompt,
        #     condense_prompt=system_prompt
        # )
        
        # return OpenAIAgent.from_tools(
        #     tools=base_tools,
        #     llm=Settings.llm,
        #     system_prompt=str(system_prompt),
        #     verbose=True,
        #     max_function_calls=3,
        #     chat_history=chat_history
        # )

        # CondenseQuestionChatEngine
        
    else:
        # Add the query engine tool to the list of tools
        query_engine_tool = QueryEngineTool.from_defaults(
            query_engine=index.as_query_engine(similarity_top_k=top_k),
        )
        tools.append(query_engine_tool)
        return AgentRunner.from_llm(
            llm=Settings.llm,
            tools=tools,
            system_prompt=system_prompt,
            verbose=True,  # Show agent logs to console
        )
