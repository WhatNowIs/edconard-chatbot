import os
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.settings import Settings
from create_llama.backend.app.engine.index import get_index

async def get_chat_engine():
    top_k = int(os.getenv("TOP_K", "4"))
    system_prompt = os.getenv("SYSTEM_PROMPT")
    

    index = get_index()
    if index is None:
        raise RuntimeError("Index is not found")
    
    return CondensePlusContextChatEngine.from_defaults(
        retriever=index.as_retriever(similarity_top_k=top_k),
        system_prompt=system_prompt,
        llm=Settings.llm,
        verbose=True
    )