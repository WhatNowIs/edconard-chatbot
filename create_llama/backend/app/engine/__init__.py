import os
# from typing import List
from llama_index.core.chat_engine import CondensePlusContextChatEngine
# from llama_index.core.base.base_multi_modal_retriever import MultiModalRetriever
from llama_index.core.settings import Settings
from app.engine.index import get_index
# import llama_index
# from llama_index.postprocessor.cohere_rerank.base import CohereRerank
# from llama_index.core.agent import AgentRunner
# from llama_index.core.tools.query_engine import QueryEngineTool
# from llama_index.core.tools.retriever_tool import RetrieverTool

async def get_chat_engine():
    top_k = int(os.getenv("TOP_K", "4"))
    system_prompt = os.getenv("SYSTEM_PROMPT")
    

    index = get_index()
    if index is None:
        raise RuntimeError("Index is not found")
    # retrivever_tool = RetrieverTool.from_defaults(
    #     retriever=index.as_retriever(similarity_top_k=top_k, image_similarity_top_k=top_k),
    # )

    # # # return index.as_retriever(similarity_top_k=top_k, image_similarity_top_k=top_k, use_async=True)

    # return AgentRunner.from_llm(
    #     llm=Settings.llm,
    #     tools=[retrivever_tool],
    #     system_prompt=system_prompt,
    #     verbose=True, 
    # )

    # cohere_rerank = CohereRerank(api_key=os.getenv("COHERE_API_KEY"), top_n=4, model="rerank-multilingual-v3.0")

    # Settings.llm.system_prompt = system_prompt

    # return index.as_retriever(similarity_top_k=top_k, image_similarity_top_k=top_k)
    
    return CondensePlusContextChatEngine.from_defaults(
        retriever=index.as_retriever(similarity_top_k=top_k, image_similarity_top_k=top_k),
        system_prompt=system_prompt,
        llm=Settings.llm,
        verbose=True
        # node_postprocessors=[cohere_rerank]
    )

    # chat_engine = OpenAIAgent.from_tools(
    #     tools=[query_engine_tool], # type: ignore
    #     llm=Settings.llm,
    #     verbose=True,
    #     system_prompt=system_prompt,
    #     callback_manager=Settings.callback_manager,
    #     max_function_calls=3,
    # )
    
    # return chat_engine

    # # else:
    #     # Add the query engine tool to the list of tools