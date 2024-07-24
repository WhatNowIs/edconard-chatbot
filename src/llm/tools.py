from typing import Dict, Tuple
from pydantic import BaseModel, Field


class DuckDuckGoTool(BaseModel):
    name: str = "duckduckgo.DuckDuckGoSearchToolSpec"
    tool_type: str = "llamahub"
    label: str = "DuckDuckGo"
    description: str = (
        "Search more information about a topic from the query using DuckDuckGo."
    )
    config: Dict = {}
    enabled: bool = False


class WikipediaTool(BaseModel):
    name: str = "wikipedia.WikipediaToolSpec"
    tool_type: str = "llamahub"
    label: str = "Wikipedia"
    description: str = (
        "Use Wikipedia to gather more information about a topic from the query."
    )
    config: Dict = {}
    enabled: bool = False


class TwitterGenerationTool(BaseModel):
    name: str = "twittertool.TwitterGenerationTool"
    tool_type: str = "local"
    label: str = "TwitterGeneration"
    description: str = (
        "Generate a perfect macro economic tweet suggestions based on a macro economic article title, headline and summary."
    )
    config: Dict = {}
    enabled: bool = False

class Tools(BaseModel):
    duckduckgo: DuckDuckGoTool = DuckDuckGoTool()
    wikipedia: WikipediaTool = WikipediaTool()
    twittertool: TwitterGenerationTool = TwitterGenerationTool()

    @classmethod
    def from_config(cls, config: Dict):
        llama_hub_config = config.get("llamahub", {})
        local = config.get("local", {})

        return cls(
            wikipedia=WikipediaTool(
                enabled=llama_hub_config.get("wikipedia.WikipediaToolSpec") is not None,
                **llama_hub_config.get("wikipedia.WikipediaToolSpec", {}),
            ),
            duckduckgo=DuckDuckGoTool(
                enabled=llama_hub_config.get("duckduckgo.DuckDuckGoSearchToolSpec")
                is not None,
                **llama_hub_config.get("duckduckgo.DuckDuckGoSearchToolSpec", {}),
            ),
            twittertool=TwitterGenerationTool(
                enabled=local.get("twittertool.TwitterGenerationTool")
                is not None,
                **local.get("twittertool.TwitterGenerationTool", {}),
            ),
        )
