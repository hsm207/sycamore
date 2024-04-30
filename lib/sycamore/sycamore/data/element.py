from collections import UserDict
from typing import Any, Optional

from sycamore.data import BoundingBox
from sycamore.data import Table


class Element(UserDict):
    """
    It is often useful to process different parts of a document separately. For example, you might want to process
    tables differently than text paragraphs, and typically small chunks of text are embedded separately for vector
    search. In Sycamore, these chunks are called elements. Like documents, elements contain a text or binary
    representations and collection of properties that can be set by the user or by built-in transforms.
    """

    def __init__(self, element=None, /, **kwargs):
        super().__init__(element, **kwargs)
        if "properties" not in self.data:
            self.data["properties"] = {}

    @property
    def type(self) -> Optional[str]:
        return self.data.get("type")

    @type.setter
    def type(self, value: str) -> None:
        self.data["type"] = value

    @property
    def text_representation(self) -> Optional[str]:
        return self.data.get("text_representation")

    @text_representation.setter
    def text_representation(self, value: str) -> None:
        self.data["text_representation"] = value

    @property
    def binary_representation(self) -> Optional[bytes]:
        return self.data.get("binary_representation")

    @binary_representation.setter
    def binary_representation(self, value: str) -> None:
        self.data["binary_representation"] = value

    @property
    def bbox(self) -> Optional[BoundingBox]:
        bbox = self.data.get("bbox")
        if bbox is None:
            return None
        elif isinstance(bbox, BoundingBox):
            return bbox
        else:
            return BoundingBox(*self.data["bbox"])

    @bbox.setter
    def bbox(self, bbox: BoundingBox) -> None:
        self.data["bbox"] = bbox.coordinates

    @property
    def properties(self) -> dict[str, Any]:
        return self.data["properties"]

    @properties.setter
    def properties(self, properties: dict[str, Any]):
        self.data["properties"] = properties

    @properties.deleter
    def properties(self) -> None:
        self.data["properties"] = {}


class TableElement(Element):
    def __init__(
        self,
        element=None,
        title: Optional[str] = None,
        columns: Optional[list[str]] = None,
        rows: Optional[list[Any]] = None,
        table: Optional[Table] = None,
        tokens: Optional[list[dict[str, Any]]] = None,
        **kwargs,
    ):
        super().__init__(element, **kwargs)
        self.data["type"] = "table"
        self.data["properties"]["title"] = title
        self.data["properties"]["columns"] = columns
        self.data["properties"]["rows"] = rows
        self.data["table"] = table
        self.data["tokens"] = tokens

    @property
    def rows(self) -> Optional[list[Any]]:
        return self.data["properties"]["rows"]

    @rows.setter
    def rows(self, rows: Optional[list[Any]] = None) -> None:
        self.data["properties"]["rows"] = rows

    @property
    def columns(self) -> Optional[list[str]]:
        return self.data["properties"]["columns"]

    @columns.setter
    def columns(self, columns: Optional[list[str]] = None) -> None:
        self.data["properties"]["columns"] = columns

    @property
    def table(self) -> Optional[Table]:
        return self.data["table"]

    @table.setter
    def table(self, value: Table) -> None:
        self.data["table"] = value

    @property
    def tokens(self) -> Optional[list[dict[str, Any]]]:
        return self.data["tokens"]

    @tokens.setter
    def tokens(self, tokens: list[dict[str, Any]]) -> None:
        self.data["tokens"] = tokens


def create_element(**kwargs) -> Element:
    if "type" in kwargs and kwargs["type"].lower() == "table":
        return TableElement(**kwargs)
    else:
        return Element(**kwargs)
