import os
import pathlib

if (TOKEN := os.getenv("HANDY_IMAGE_CONVERTER_TOKEN")) is None:
    msg = "HANDY_IMAGE_CONVERTER_TOKEN not found!"
    raise ValueError(msg)

IMAGES_DIR = pathlib.Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

SUPPORTED_FORMATS = {"avif", "jpg", "jpeg", "png", "webp"}
