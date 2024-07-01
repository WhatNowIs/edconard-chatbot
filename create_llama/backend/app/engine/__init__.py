import os
from create_llama.backend.app.engine.tools.prompt import TweetPrompt, TopicGeneration, Summarization
from create_llama.backend.app.utils.enums import SupportedChatMode
from create_llama.backend.app.utils.helpers import Article
from llama_index.core.chat_engine import CondensePlusContextChatEngine, CondenseQuestionChatEngine
from llama_index.core.settings import Settings
from app.engine.tools import ToolFactory
from app.engine.index import get_index
from src.core.config.postgres import get_db
from src.core.config.redis import get_redis_client
from src.core.services.user import UserService
from src.utils.logger import get_logger

async def get_current_chat_mode(user_id: str | None):
    if user_id is not None:
        db = get_db()
        user_service = UserService(db)
        redis_client = await get_redis_client()
        chat_mode = await user_service.get_chat_mode(user_id, redis_client)

        return chat_mode
    return None

async def get_chat_engine(user_id: str | None = None, data: Article | None = None, chat_history: str | None = ""):
    # from src.core.dbconfig.postgres import get_db
    top_k = int(os.getenv("TOP_K", "3"))
    system_prompt = os.getenv("SYSTEM_PROMPT")

    index = get_index()
    if index is None:
        raise RuntimeError("Index is not found")

    tools = ToolFactory.from_env()

    # Use the context chat engine if no tools are provided
    if len(tools) == 0:
        chat_mode = await get_current_chat_mode(user_id)
        chat_history = ''
        if chat_mode is not None and chat_mode == SupportedChatMode.MACRO_ROUNDUP_ARTICLE_TWEET_GENERATION.value:
            # CondenseQuestionChatEngine
            get_logger().info(f"We are in tweet mode: {data}")
            return  CondenseQuestionChatEngine.from_defaults(
                query_engine=index.as_query_engine(),
                llm=Settings.llm,
                condense_prompt=TweetPrompt.format_prompt_template(
                    abstract=data.abstract,
                    authors=data.authors,
                    headline=data.headline,
                    publisher=data.publisher,
                    chat_history=chat_history
                ) if data is not None else None
            )
        elif chat_mode is not None and chat_mode == SupportedChatMode.MACRO_ROUNDUP_ARTICLE_SUMMARY_OPTIMIZATION.value:
            # CondenseQuestionChatEngine
            get_logger().info(f"We are in article summarization mode: {data}")
            return  CondenseQuestionChatEngine.from_defaults(
                query_engine=index.as_query_engine(),
                llm=Settings.llm,
                condense_prompt=Summarization.format_prompt_template(
                    abstract=data.abstract,
                    headline=data.headline,
                    publisher=data.publisher,
                    chat_history=chat_history
                ) if data is not None else None
            )
        elif chat_mode is not None and chat_mode == SupportedChatMode.MACRO_ROUNDUP_ARTICLE_TOPIC_GENERATION.value:
            # CondenseQuestionChatEngine
            get_logger().info(f"We are in topic generation mode: {data}")
            return  CondensePlusContextChatEngine.from_defaults(
                retriever=index.as_retriever(top_k=top_k),
                system_prompt=TopicGeneration.format_prompt_template(
                    abstract=data.abstract,
                    headline=data.headline,
                    publisher=data.publisher,
                    chat_history=chat_history,
                    abstract_weight=0.6,
                    headline_weight=0.2,
                    publisher_weight=0.2
                ) if data is not None else system_prompt,
                llm=Settings.llm,
            )
        # CondenseQuestionChatEngine
        get_logger().info(f"We are not in tweet or topic generation mode {chat_mode} - {data}")

        return CondensePlusContextChatEngine.from_defaults(
            retriever=index.as_retriever(top_k=top_k),
            system_prompt=system_prompt,
            llm=Settings.llm
        )
        
    else:
        from llama_index.core.agent import AgentRunner
        from llama_index.core.tools.query_engine import QueryEngineTool

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
