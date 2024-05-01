import base64
from io import BytesIO
from typing import Optional

from PIL import Image

from sycamore.data import BoundingBox

DEFAULT_PADDING = 10


def crop_to_bbox(image: Image.Image, bbox: BoundingBox, padding=DEFAULT_PADDING) -> Image.Image:
    width, height = image.size

    crop_box = (
        bbox.x1 * width - padding,
        bbox.y1 * height - padding,
        bbox.x2 * width + padding,
        bbox.y2 * height + padding,
    )

    cropped_image = image.crop(crop_box)
    return cropped_image


def image_to_bytes(image: Image.Image, format: Optional[str] = None) -> bytes:
    if format is None:
        return image.tobytes()

    iobuf = BytesIO()
    image.save(iobuf, format=format)
    return iobuf.getvalue()


def base64url(image: Image.Image) -> str:
    encoded_image = image_to_bytes(image, "PNG")
    return f"data:image/png/;base64,{base64.b64encode(encoded_image).decode('utf-8')}"
