
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.schema import NodeWithScore, MetadataMode, QueryBundle
from llama_index.core.base.response.schema import Response
from llama_index.core.prompts import PromptTemplate
from llama_index.core.schema import ImageNode

from typing import Any, List, Optional, Tuple
from llama_index.core.postprocessor.types import BaseNodePostprocessor

class MultimodalQueryEngine(CustomQueryEngine):
    qa_prompt: PromptTemplate
    retriever: BaseRetriever
    multi_modal_llm: OpenAIMultiModal
    node_postprocessors: Optional[List[BaseNodePostprocessor]]

    def __init__(
        self,
        qa_prompt: PromptTemplate,
        retriever: BaseRetriever,
        multi_modal_llm: OpenAIMultiModal,
        node_postprocessors: Optional[List[BaseNodePostprocessor]] = [],
    ):
        super().__init__(
            qa_prompt=qa_prompt,
            retriever=retriever,
            multi_modal_llm=multi_modal_llm,
            node_postprocessors=node_postprocessors
        )

    def custom_query(self, query_str: str):
        # retrieve most relevant nodes
        nodes = self.retriever.retrieve(query_str)

        for postprocessor in self.node_postprocessors:
            nodes = postprocessor.postprocess_nodes(
                nodes, query_bundle=QueryBundle(query_str)
            )


        # create image nodes from the image associated with those nodes
        image_nodes = [
            NodeWithScore(node=ImageNode(image_path=n.node.metadata["image_path"]))
            for n in nodes
        ]

        # create context string from parsed markdown text
        ctx_str = "\n\n".join(
            [r.node.get_content(metadata_mode=MetadataMode.LLM).strip() for r in nodes]
        )

        # prompt for the LLM
        fmt_prompt = self.qa_prompt.format(context_str=ctx_str, query_str=query_str)

        # use the multimodal LLM to interpret images and generate a response to the prompt
        llm_repsonse = self.multi_modal_llm.complete(
            prompt=fmt_prompt,
            image_documents=[image_node.node for image_node in image_nodes],
        )
        return Response(
            response=str(llm_repsonse),
            source_nodes=nodes,
            metadata={"text_nodes": text_nodes, "image_nodes": image_nodes},
        )