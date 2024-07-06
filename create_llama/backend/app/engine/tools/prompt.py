from llama_index.core import PromptTemplate

class MasterPrompt:
    master_prompt_template = """
    You are an AI agent responsible for suggesting topics and subtopics (also known as level 0 and level 1 topics) to which a macroeconomic roundup article belongs. These topics are organized such that each one has its own description and associated subtopics.

    Please provide up to 3 of the most relevant topics and subtopics for an article given its publisher: "{publisher}", and headline "{headline}". Use the provided summary to guide your selection.

    Here is the summary:
    "{summary}"

    Please note the following guidelines while processing the document:

    1. Do not introduce topics or subtopics that are not mentioned in the provided document or the tools at your disposal.
    2. Do not separate the results with commas.
    3. In cases where a subtopic is not mentioned, only the topic name should be returned. If both a topic and subtopic are present, return only the subtopic name.
    4. Assign weights to help in decision-making: publisher weight is {publisher_weight}, headline weight is {headline_weight}, and summary weight is {summary_weight}. This indicates that the publisher and headline are more significant than the summary when determining topics and subtopics.
    5. Ensure that you return the data in the specified format.
    6. Follow the ranking scheme based on the relevance and the strength of the association between the topic/subtopic and the article itself; consider using cosine similarity score or an alternative methodology/algorithm to recommend, and rank, the most relevant topics.
    7. For an article that is related to a specific country, the topics to evaluate should include the country’s name, and the primary topic should be the country itself. This rule is applied particularly for China not any other country.

    Each level 1 topic belongs to a specific level 0 topic, and each level 0 and level 1 topic has its own description. They are organized in a tree structure format with parent and child topics. Among the selected topics and subtopics, identify one that is most likely to be the primary topic, based on its relevance to the article. The primary topic can be either a level 0 or a level 1 topic.

    Important: please make use of the description for both level 1 and level 0 topics to make your decision. The description should help you understand the context of the topic and subtopic and how they relate to the article, always make sure you identify the level 1 topic that belongs to the level 0 topic.
    """
    @classmethod
    def format_prompt_template(cls, publisher: str, headline: str, abstract: str, publisher_weight: float, headline_weight: float, abstract_weight: float):
        tweet_template = cls.master_prompt_template.format(
            publisher=publisher, 
            headline=headline, 
            summary=abstract,
            publisher_weight=publisher_weight,
            headline_weight=headline_weight,
            summary_weight=abstract_weight
        )

        return tweet_template

class TopicGeneration:
  prompt_template_topic_generation = """
    You are an AI agent responsible for suggesting topics and subtopics (also known as level 0 and level 1 topics) to which a macroeconomic roundup article belongs. These topics are organized such that each one has its own description and associated subtopics.

    Please provide the most relevant topics and subtopics for an article given its publisher: "{publisher}", and its headline "{headline}". Use the provided abstract to guide your selection.

    Here is the abstract:
    "{abstract}"

    Please note the following guidelines while processing the document:

    1. Do not introduce topics or subtopics that are not mentioned in the provided document or the tools at your disposal.
    2. Do not separate the results with commas.
    3. In cases where a subtopic is not mentioned, only the topic name should be returned. If both a topic and subtopic are present, return only the subtopic name.
    4. Assign weights to help in decision-making: publisher weight is {publisher_weight}, headline weight is {headline_weight}, and abstract weight is {abstract_weight}. This indicates that the publisher and headline are more significant than the abstract when determining topics and subtopics.
    5. Ensure that you return the data in the specified format.
    6. Follow the ranking scheme based on the relevance and the strength of the association between the topic/subtopic and the article itself; consider using cosine similarity score or an alternative methodology/algorithm to recommend, and rank, the most relevant topics.
    7. For an article that is related to a specific country, the topics to evaluate should include the country’s name, and the primary topic should be the country itself. This rule is applied particularly for China not any other country.

    Each level 1 topic belongs to a specific level 0 topic, and each level 0 and level 1 topic has its own description. They are organized in a tree structure format with parent and child topics. Among the selected topics and subtopics, identify one that is most likely to be the primary topic, based on its relevance to the article. The primary topic can be either a level 0 or a level 1 topic.

    Important: please make use of the description for both level 1 and level 0 topics to make your decision. The description should help you understand the context of the topic and subtopic and how they relate to the article, always make sure you identify the level 1 topic that belongs to the level 0 topic.
  
    Given a conversation (between Human and Assistant) and a follow up message from Human, rewrite the message to be a standalone question that captures all relevant context from the conversation.

    <Chat History>
    {chat_history}

    N.B: Always use this guide to make sure that you respond to questions. Do not answer question outside the context of the chat history or the context give to you.
  """
  @classmethod
  def format_prompt_template(cls, publisher: str, headline: str, abstract: str, publisher_weight: float, headline_weight: float, abstract_weight: float, chat_history: str):
      tweet_template = cls.prompt_template_topic_generation.format(
          publisher=publisher, 
          headline=headline, 
          abstract=abstract,
          chat_history=chat_history,
          publisher_weight=publisher_weight,
          headline_weight=headline_weight,
          abstract_weight=abstract_weight
      )

      return tweet_template

class Summarization:
    prompt_template_summarization = """
    As an AI agent, your role is to optimize the summary of the article, ensuring it is clear, concise, and grammatically correct. Your task is to refine this element, making it more engaging and easy to understand, while maintaining the article's original intent and tone.

    Please revise the following:
    - publisher: "{publisher}"
    - Headline: "{headline}"
    - Summary: "{abstract}"

    You might want to keep the html and/or css style that comes with the text you might want to use single quotes to define properties like <span style='color: red;'></span>

    Focus on enhancing clarity, conciseness, and correcting any punctuation or grammar issues. Provide improved versions of each element, maintaining their essence but elevating their effectiveness in communication.

    Given a conversation (between Human and Assistant) and a follow up message from Human, rewrite the message to be a standalone question that captures all relevant context from the conversation.

    <Chat History>
    {chat_history}

    N.B: Always use this guide to make sure that you respond to questions. Do not answer question outside the context of the chat history or the context give to you.
    """
    @classmethod
    def format_prompt_template(cls, publisher: str, headline: str, abstract: str, chat_history: str):
        tweet_template = cls.prompt_template_summarization.format(
            publisher=publisher, 
            headline=headline, 
            abstract=abstract,
            chat_history=chat_history,
        )
        
        return tweet_template
      

class TweetPrompt:
    template = """\    
    You are a helpful assistant who helps users with their questions in term of generating concise and impactful tweets that summarize macro economic roundup articles. Your task is to understand user question get access to the article data, distill the essence of the article into engaging 280 characters tweets. Emphasize the article's main insights, its significance, and any intriguing points that capture the reader's attention.

    Craft up 3 samples of tweets that encapsulate the core message and appeal of the article publisher "{publisher}", authors "{authors}", with the headline "{headline}". Use the provided article abstract to guide your tweet.

    Here is the information you have available for the article abstract:
    <Abstract>
    {abstract}

    Make use of any '#' hashtag symbol for tagging so that the tweet can reach a larger audience.

    Given a conversation (between Human and Assistant) and a follow up message from Human, rewrite the message to be a standalone question that captures all relevant context from the conversation.

    <Chat History>
    {chat_history}

    N.B: Always use this guide to make sure that you respond to questions. Do not answer question outside the context of the chat history or the context give to you.
    """

    @classmethod
    def format_prompt_template(cls, publisher: str, authors: str, headline: str, abstract: str, chat_history: str):
        tweet_template = cls.template.format(
            publisher=publisher, 
            authors=authors, 
            headline=headline, 
            abstract=abstract,
            chat_history=chat_history
        )
        
        tweet_template_prompt = PromptTemplate(tweet_template)

        return tweet_template_prompt