from typing import Any, Optional
from ray.data import Dataset

from PIL import Image

from sycamore.data import Document, ImageElement
from sycamore.llms.openai import OpenAI, OpenAIClientWrapper, OpenAIModels
from sycamore.plan_nodes import Node, Transform
from sycamore.utils.image_utils import base64url
from sycamore.utils.extract_json import extract_json
from sycamore.utils.generate_ray_func import generate_map_function


class OpenAIImageSummarizer:
    model = OpenAIModels.GPT_4_TURBO

    prompt = """You are given an image from a PDF document along with with some snippets of text preceding
            and following the image on the page. Based on this context, please decide whether the image is a
            graph or not. An image is a graph if it is a bar chart or a line graph. If the image is a graph,
            please summarize the axes, including their units, and provide a summary of the results in no more
            than 5 sentences.

            Return the results in the following JSON schema:

            {
              "is_graph": true,
              "x-axis": string,
              "y-axis": string,
              "summary": string
            }

            If the image is not a graph, please summarize the contents of the image in no more than five sentences
            in the following JSON format:

            {
              "is_graph": false,
              "summary": string
            }

            In all cases return only JSON and check your work.
            """

    def __init__(self, openai_model: Optional[OpenAI] = None, client_wrapper: Optional[OpenAIClientWrapper] = None):
        if openai_model is not None:
            self.openai = openai_model
        else:
            self.openai = OpenAI(model_name=self.model, client_wrapper=client_wrapper)

    def summarize_image(
        self, image: Image.Image, preceding_context: Optional[str] = None, following_context: Optional[str] = None
    ):
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": self.prompt},
        ]

        if preceding_context is not None:
            messages.append({"role": "user", "content": "The text preceding the image is {}".format(preceding_context)})

        messages.append({"role": "user", "content": [{"type": "image_url", "image_url": {"url": base64url(image)}}]})

        if following_context is not None:
            messages.append({"role": "user", "content": "The text preceding the image is {}".format(following_context)})

        prompt_kwargs = {"messages": messages}

        raw_answer = self.openai.generate(prompt_kwargs=prompt_kwargs, llm_kwargs={})
        return extract_json(raw_answer.content)

    def summarize_all_images(self, doc: Document) -> Document:
        for i, element in enumerate(doc.elements):
            if not isinstance(element, ImageElement):
                continue

            preceding_context = None
            if i > 0:
                preceding_element = doc.elements[i - 1]
                if preceding_element.type in {"Section-header", "Caption", "Text"}:
                    preceding_context = preceding_element.text_representation

            following_context = None
            if i < len(doc.elements) - 1:
                preceding_element = doc.elements[i + 1]
                if preceding_element.type in {"Caption", "Text"}:  # Don't want titles following the image.
                    following_context = preceding_element.text_representation

            image = element.as_image()

            if image is None:
                continue

            json_summary = self.summarize_image(image, preceding_context, following_context)

            element.properties["summary"] = json_summary
            element.text_representation = json_summary["summary"]
        return doc


class SummarizeImages(Transform):
    def __init__(self, child: Node, summarizer=OpenAIImageSummarizer(), **resource_args):
        super().__init__(child, **resource_args)
        self.summarizer = summarizer

    def execute(self) -> Dataset:
        input_dataset = self.child().execute()
        dataset = input_dataset.map(generate_map_function(self.summarizer.summarize_all_images))
        return dataset
