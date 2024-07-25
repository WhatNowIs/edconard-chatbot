import os
from typing import List, Optional
from langchain.callbacks.manager import AsyncCallbackManager 
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from llama_cloud import MessageRole
from src.core.config.postgres import get_db
from src.core.config.redis import get_redis_client
from src.core.models.base import Message
from src.core.services.thread import ThreadService
from src.core.services.user import UserService
from src.utils.logger import get_logger
from llama_index.llms.groq import Groq
from llama_index.core.llms import ChatMessage


MODEL_NAME = "llama-3.1-405b-reasoning"
GROK_API_KEY = "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"

master_prompt_template = """
Given a conversation (between Human and Assistant) and a follow up message from Human, your focus should be to understand the context from the conversation and answer very well a follow up question.
You will be responsible responsible for handling various tasks as well making sure that you keep a conversation between you and human, your taks will include:
    
* Topics and subtopics suggestions,
* Helping human being with a perfect tweet
* Generating title and meta description to enhance SEO
* As well as enhancing the article summary by ensuring it is clear, concise, and grammatically correct.
    
I. For topic classification, your role will be to act as an AI agent responsible for suggesting topics and subtopics given an article headline and summary you will be asked to suggest topics and subtopic (also known as level 0 and level 1 topics) to which a macroeconomic roundup article belongs to. These topics are organized such that each one has its own description and associated subtopics.

Your main job here is classifify or to suggest up 3 or 4 of the most relevant topics and subtopics for an article given its headline and summary.

Please note the following guidelines while processing the document:

1. Always use the tool at your disposal to get access to the already predefined topics. Do not introduce topics or subtopics that are not mentioned in our vector store.
3. In cases where a subtopic is not mentioned, only the topic name should be returned. If both a topic and subtopic are present, return only the subtopic name.
4. The primary topic should most of the time be the subtopic in case the subtopic is not present use the actual topic.
5. Assign weights to help in decision-making: headline weight is 3, and summary weight is 5. This indicates that the summary and headline are more significant than the summary when determining topics and subtopics.
6. Ensure that you return the data in the specified format for human readability.
7. Follow the ranking scheme based on the relevance and the strength of the association between the topic/subtopic and the article itself; consider using cosine similarity score or an alternative methodology/algorithm to recommend, and rank, the most relevant topics.
8. For an article that is related to a specific country, the topics to evaluate should include the country's name, and the primary topic should be the country itself. This rule is applied particularly for China not any other country.

Each level 1 topic belongs to a specific level 0 topic, and each level 0 and level 1 topic has its own description. They are organized in a tree structure format with parent and child topics. Among the selected topics and subtopics, identify one that is most likely to be the primary topic, based on its relevance to the article. The primary topic can be either a level 0 or a level 1 topic.

Important: please make use of the description for both level 1 and level 0 topics to make your decision. The description should help you understand the context of the topic and subtopic and how they relate to the article, always make sure you identify the level 1 topic that belongs to the level 0 topic.

Here are all the predefined topics and subtopics do not return anything which is not listed here:

Comparisons:
    - Age
    - Cross-country
    - Gender
    - Geography (Urban/Rural)
    - Historical
    - Liberal/Conservative
    - No Comparison
    - Other Comparison
    - Race
    - Sector
    - Skill Level

Fiscal Policy:
    - Fiscal Deficits
    - Government Spending
    - Infrastructure
    - Multiplier/Rational Expectations
    - Regulation
    - Taxation

GDP:
    - Business Cycle
    - Financial Markets
    - Growth
    - Housing
    - Inflation
    - Savings Glut/Trade Deficit
    - Trade (not deficits)

Monetary Policy:
    - Banking
    - Financial Crisis
    - M&M

Science:
    - Cosmos
    - Evolution/Heredity
    - Fraudulent Studies
    - Global Warming
    - Other Science

Workforce:
    - Demographics
    - Education
    - Family/Marriage
    - Gender Pay Gap
    - Immigration
    - Inequality
    - Minimum Wage
    - Mobility/Assortive Mating
    - Poverty/Crime
    - Unemployment/Participation
    - Wages/Income
    - Workforce Reorganization/Participation

Productivity:
    - Cronyism
    - Incentives/Risk-Taking
    - Innovation/Research
    - Institutional Capabilities
    - Intangibles
    - Investment
    - Startups
    - Workforce Reorganization/Participation

Energy: []

For the other tasks please use the tools at your disposal to answer questions related to tweet generation, title and meta description generation etc.
"""


async def grok_tweet_chain(
    input: str,
    user_id: str,
    thread_id: str
):

    """
    Useful for handling any question related to tweet generation and optimization based on the article data like headline, authors, publisher, and summary

    Args:
        - stream_handler: is an object that handle the chat stream.
        - chat_history: This is a string of previous messages in the chat, this is used to give context to the LLM on how to answer the incoming question.
        - input: This is an input question which the ai agent is supposed to answer.
        - article: This an object which contains the article's information such as headline, publisher, authors and the summary of the article
    """   
    
    redis = await get_redis_client()
    db = get_db()
    user_service = UserService(db)
    messages_tmp: List[Message] = await user_service.get_chat_history(user_id = user_id, redis_client = redis)
    article = await user_service.get_article(user_id = user_id, redis_client = redis)
    
    llm = Groq(model=MODEL_NAME, api_key=GROK_API_KEY, is_chat_model=True)

    article_data = f"""
    Headline = "{article.headline}"
    Summary = "{article.abstract}"
    Author(s) = "{article.authors}"
    Publication = "{article.publisher}"
    """

    start_prompt = f"""
    Your task is to help user with their question in generating a perfect tweet based on the article with the following headline, publisher, author(s) and article summary:\n

    {article_data}
    """

    end_prompt = f"""\n
    Instructions:
    * Ensure the tweet does not exceed 254 characters.
    * Always include the source, mentioning the authors and/or the publication.
    * Use abbreviations where necessary to stay within the 254 character limit. For example, use '%' instead of percent, 'mm' instead of million.
    * Use hashtags and @ symbols to increase engagement.

    Style and Tone:
    * Professional: Maintain a professional and informative tone.
    * Engaging: Write in an engaging manner to capture the audience’s interest.
    * Concise: Be clear and to the point.
    * Authoritative: Convey authority and credibility.

    Additional Guidelines:
    * Avoid using adjectives like 'massive', 'huge', 'totally', 'very'.
    * Rarely, if ever, use the word 'got'.
    * Rarely, if ever, use the word 'indeed'.
    """

    master_prompt = f"""    
    {start_prompt}

    {end_prompt}
    This is a conversation between a human and an assistant some messages might be out of context of your main task, always make sure you are able to get track of what you are supposed to do, Follow the instuctions given below:\n
    """

    chat_history = [ChatMessage(content=message.content, role=MessageRole.USER if str(message.role) == "user" else MessageRole.ASSISTANT) for message in messages_tmp]

    messages = [
        ChatMessage(
            role="system", content=master_prompt
        ),
    ]
    messages.extend(chat_history)
    messages.append(        
        ChatMessage(
            role="user", content=input
        ),
    )

    response = llm.astream_chat(messages)
    
    return response


async def grok_title_and_meta_chain(
    input: str,
    user_id: str,
    thread_id: str,
):

    """
    Useful for handling a conversation to help user craft a perfect SEO title and SEO meta description based on the article data like headline, authors, publisher, and summary
    
    Args:
        - stream_handler: is an object that handle the chat stream.
        - chat_history: This is a string of previous messages in the chat, this is used to give context to the LLM on how to answer the incoming question.
        - input: This is an input question which the ai agent is supposed to answer.
        - article: This an object which contains the article's information such as headline, publisher, authors and the summary of the article
    """
    
    redis = await get_redis_client()
    db = get_db()
    user_service = UserService(db)
    messages_tmp: List[Message] = await user_service.get_chat_history(user_id = user_id, redis_client = redis)
    article = await user_service.get_article(user_id = user_id, redis_client = redis)
    
    
    llm = Groq(model=MODEL_NAME, api_key=GROK_API_KEY, is_chat_model=True)

    get_logger().info(f"Here are article data: {article}")

    article_data = f"""
    Headline = "{article.headline}"
    Summary = "{article.abstract}"
    Author(s) = "{article.authors}"
    Publication = "{article.publisher}"
    """

    start_prompt = f"""
    You are a helpful assistant. Your task is to help user with their questions such that they are able to generate a perfect SEO-optimized title and meta descriptions that enhance visibility in search engine results pages (SERPs), \
    improve click-through rates (CTR), and drive more organic traffic to the website for a macro-economica related article.

    Please answer the question for an article with the following headline, publisher, author(s) and article summary:\n

    {article_data}

    Use the below guideline to help you generate an optimized SEO title and meta description
    """

    end_prompt = f"""\n
    General Guidelines:
    * For SEO Title:
        - Write titles that are both informative and engaging to encourage clicks.
        - Use keywords naturally and avoid overloading the title with too many keywords, which can be seen as spammy by search engines.
        
    * For SEO Meta descriptions:
        - Summarize the content clearly and concisely, ensuring the description is easy to read and understand.
        - Ensure the meta description accurately reflects the article content provided to you to avoid high bounce rates from users who feel misled.

    Instructions:
    * For SEO Title:
        - Ensure the title is between 50-60 characters to avoid truncation in SERPs.
        - Include primary keywords at the beginning of the title
        - The title must accurately reflect the article content provided to you.
        - Focus on the main topic of the article and identify the primary keywords related to this topic.
        - Place the most important keywords towards the beginning of the title.
        - Ensure the title is easy to read and understand, avoiding complex structures or jargon.
        - Craft the title to be engaging and enticing, prompting users to click through to the article.
        - Ensure the title accurately represents the content of the article to set the right expectations for readers.

    * For SEO Meta descriptions:
        - Ensure the meta description is between 150-160 characters to prevent truncation in SERPs.
        - Include primary keywords naturally within the description.
        - The meta description must accurately reflect the article content provided to you.
        - Focus on the main topic of the article and identify the primary keywords related to this topic.
        - Integrate the primary keywords naturally within the description.
        - Ensure the meta description is easy to read and flows naturally.
        - Craft the description to be engaging and enticing, prompting users to click through to the article.
        - Ensure the meta description accurately represents the content of the article to set the right expectations for readers.

    Output Format:
        * Title: the text for the SEO Title here.
        * Meta Description: the text for SEO Meta description here.
    """

    master_prompt = f"""
    {start_prompt}

    {end_prompt}
    This is a conversation between a human and an assistant some messages might be out of context of your main task, always make sure you are able to get track of what you are supposed to do, Follow the instuctions given below:\n
    """

    chat_history = [ChatMessage(content=message.content, role=MessageRole.USER if str(message.role) == "user" else MessageRole.ASSISTANT) for message in messages_tmp]

    messages = [
        ChatMessage(
            role="system", content=master_prompt
        ),
    ]
    messages.extend(chat_history)
    messages.append(        
        ChatMessage(
            role="user", content=input
        ),
    )

    response = llm.astream_chat(messages)
    
    return response

# async def tweet_chain(
#     input: str,
#     user_id: str,
#     chat_history: Optional[str],
# ) -> LLMChain:

#     """
#     Useful for handling any question related to tweet generation and optimization based on the article data like headline, authors, publisher, and summary

#     Args:
#         - stream_handler: is an object that handle the chat stream.
#         - chat_history: This is a string of previous messages in the chat, this is used to give context to the LLM on how to answer the incoming question.
#         - input: This is an input question which the ai agent is supposed to answer.
#         - article: This an object which contains the article's information such as headline, publisher, authors and the summary of the article
#     """   
#     stream_manager = AsyncCallbackManager([])
    
#     redis = await get_redis_client()
#     db = get_db()
#     user_service = UserService(db)

#     article = await user_service.get_article(user_id = user_id, redis_client = redis)

#     llm = ChatOpenAI(
#         temperature = 0.6,
#         model = os.getenv("MODEL", "gpt-4o"),
#         verbose = True,
#         streaming = True,
#         callback_manager = stream_manager,
#     )  # type: ignore    

#     article_data = f"""
#     Headline = "{article.headline}"
#     Summary = "{article.abstract}"
#     Author(s) = "{article.authors}"
#     Publication = "{article.publisher}"
#     """

#     start_prompt = f"""
#     Your task is to help user with their question in generating a perfect tweet based on the article with the following headline, publisher, author(s) and article summary:\n

#     {article_data}
#     """

#     end_prompt = f"""\n
#     Instructions:
#     * Ensure the tweet does not exceed 254 characters.
#     * Always include the source, mentioning the authors and/or the publication.
#     * Use abbreviations where necessary to stay within the 254 character limit. For example, use '%' instead of percent, 'mm' instead of million.
#     * Use hashtags and @ symbols to increase engagement.

#     Style and Tone:
#     * Professional: Maintain a professional and informative tone.
#     * Engaging: Write in an engaging manner to capture the audience’s interest.
#     * Concise: Be clear and to the point.
#     * Authoritative: Convey authority and credibility.

#     Additional Guidelines:
#     * Avoid using adjectives like 'massive', 'huge', 'totally', 'very'.
#     * Rarely, if ever, use the word 'got'.
#     * Rarely, if ever, use the word 'indeed'.
#     """

#     master_prompt = f"""    
#     {start_prompt}

#     {end_prompt}
#     This is a conversation between a human and an assistant some messages might be out of context of your main task, always make sure you are able to get track of what you are supposed to do, Follow the instuctions given below:\n
#     """

#     template = master_prompt + """
    
#     {chat_history}

#     Answer this question {input}:
#     """

#     prompt = PromptTemplate(
#         input_variables=["input", "chat_history"], template=template
#     )

#     tweet_generation_chain = prompt | llm | StrOutputParser()

#     response = await tweet_generation_chain.ainvoke({
#         "input": input, 
#         "chat_history": chat_history,
#     })

#     return response



# async def title_and_meta_chain(
#     input: str,
#     user_id: str,
#     chat_history: Optional[str],
# ) -> LLMChain:

#     """
#     Useful for handling a conversation to help user craft a perfect SEO title and SEO meta description based on the article data like headline, authors, publisher, and summary
    
#     Args:
#         - stream_handler: is an object that handle the chat stream.
#         - chat_history: This is a string of previous messages in the chat, this is used to give context to the LLM on how to answer the incoming question.
#         - input: This is an input question which the ai agent is supposed to answer.
#         - article: This an object which contains the article's information such as headline, publisher, authors and the summary of the article
#     """
#     stream_manager = AsyncCallbackManager([])
    
#     redis = await get_redis_client()
#     db = get_db()
#     user_service = UserService(db)

#     article = await user_service.get_article(user_id = user_id, redis_client = redis)

#     llm = ChatOpenAI(
#         temperature = 0.6,
#         model = os.getenv("MODEL", "gpt-4o"),
#         verbose = True,
#         streaming = True,
#         callback_manager = stream_manager,
#     )  # type: ignore

#     get_logger().info(f"Here are article data: {article}")

#     article_data = f"""
#     Headline = "{article.headline}"
#     Summary = "{article.abstract}"
#     Author(s) = "{article.authors}"
#     Publication = "{article.publisher}"
#     """

#     start_prompt = f"""
#     You are a helpful assistant. Your task is to help user with their questions such that they are able to generate a perfect SEO-optimized title and meta descriptions that enhance visibility in search engine results pages (SERPs), \
#     improve click-through rates (CTR), and drive more organic traffic to the website for a macro-economica related article.

#     Please answer the question for an article with the following headline, publisher, author(s) and article summary:\n

#     {article_data}

#     Use the below guideline to help you generate an optimized SEO title and meta description
#     """

#     end_prompt = f"""\n
#     General Guidelines:
#     * For SEO Title:
#         - Write titles that are both informative and engaging to encourage clicks.
#         - Use keywords naturally and avoid overloading the title with too many keywords, which can be seen as spammy by search engines.
        
#     * For SEO Meta descriptions:
#         - Summarize the content clearly and concisely, ensuring the description is easy to read and understand.
#         - Ensure the meta description accurately reflects the article content provided to you to avoid high bounce rates from users who feel misled.

#     Instructions:
#     * For SEO Title:
#         - Ensure the title is between 50-60 characters to avoid truncation in SERPs.
#         - Include primary keywords at the beginning of the title
#         - The title must accurately reflect the article content provided to you.
#         - Focus on the main topic of the article and identify the primary keywords related to this topic.
#         - Place the most important keywords towards the beginning of the title.
#         - Ensure the title is easy to read and understand, avoiding complex structures or jargon.
#         - Craft the title to be engaging and enticing, prompting users to click through to the article.
#         - Ensure the title accurately represents the content of the article to set the right expectations for readers.

#     * For SEO Meta descriptions:
#         - Ensure the meta description is between 150-160 characters to prevent truncation in SERPs.
#         - Include primary keywords naturally within the description.
#         - The meta description must accurately reflect the article content provided to you.
#         - Focus on the main topic of the article and identify the primary keywords related to this topic.
#         - Integrate the primary keywords naturally within the description.
#         - Ensure the meta description is easy to read and flows naturally.
#         - Craft the description to be engaging and enticing, prompting users to click through to the article.
#         - Ensure the meta description accurately represents the content of the article to set the right expectations for readers.

#     Output Format:
#         * Title: the text for the SEO Title here.
#         * Meta Description: the text for SEO Meta description here.
#     """

#     master_prompt = f"""
#     {start_prompt}

#     {end_prompt}
#     This is a conversation between a human and an assistant some messages might be out of context of your main task, always make sure you are able to get track of what you are supposed to do, Follow the instuctions given below:\n
#     """

#     template = master_prompt + """
    
#     {chat_history}

#     Answer this question {input}:
#     """

#     prompt = PromptTemplate(
#         input_variables=["input", "chat_history"], template=template
#     )

#     title_and_meta_generation_chain = prompt | llm | StrOutputParser()

#     response = await title_and_meta_generation_chain.ainvoke({
#         "input": input, 
#         "chat_history": chat_history,
#     })

#     return response