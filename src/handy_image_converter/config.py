import os
import pathlib


if (TOKEN := os.getenv("HANDY_IMAGE_CONVERTER_TOKEN")) is None:
    raise ValueError("HANDY_IMAGE_CONVERTER_TOKEN not found!")

IMAGES_DIR = pathlib.Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

SUPPORTED_FORMATS = {"avif", "jpg", "jpeg", "png", "webp"}
