import uuid

from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, Message, ReplyKeyboardRemove
from PIL import Image

from handy_image_converter.config import IMAGES_DIR, SUPPORTED_FORMATS
from handy_image_converter.keyboards import mime_types_and_keyboards
from handy_image_converter.loader import dp
from handy_image_converter.states import ImageInfo


@dp.message_handler(commands=["start"])
async def send_welcome(message: Message) -> None:
    await message.answer(
        "Hi! I'm [HandyImageConverterBot](https://t.me/HandyImageConverterBot).\n\nJust send me any image *as file* ☺️",
        parse_mode="Markdown",
    )


@dp.message_handler(commands=["help"])
async def send_help(message: Message) -> None:
    await message.answer(
        "Just send me any image *as file* ☺️\n\n"
        "👨‍💻 [Author](https://t.me/SuspiciousUser)\n"
        "🤖 [Source code](https://github.com/JustKappaMan/Handy-Image-Converter)",
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


@dp.message_handler(content_types=["photo"])
async def handle_compressed_image(message: Message) -> None:
    await message.answer("Please, send images *as files* 🙂", parse_mode="Markdown")


@dp.message_handler(content_types=["document"])
async def handle_uncompressed_image(message: Message, state: FSMContext) -> None:
    if image := message.document:
        if image.mime_type in mime_types_and_keyboards:
            name, extension = image.file_name.rsplit(".", 1)
            tmp_copy_path = IMAGES_DIR / f"{uuid.uuid4().hex}.{extension}"
            await image.download(destination_file=tmp_copy_path)
            await state.update_data(original_name=name, temporary_copy_path=tmp_copy_path)

            await ImageInfo.output_format.set()
            await message.answer("Select the output format", reply_markup=mime_types_and_keyboards[image.mime_type])
        else:
            await message.answer(
                "Error! Unsupported image format.\n\nI support only AVIF/JPEG/PNG/WEBP images at the moment 😔",
            )


@dp.message_handler(state=ImageInfo.output_format)
async def send_image_back(message: Message, state: FSMContext) -> None:
    if (fmt := message.text.lower()) in SUPPORTED_FORMATS:
        image_info = await state.get_data()
        old_path = image_info["temporary_copy_path"]
        new_path = old_path.with_suffix(f".{fmt}")

        if old_path.suffix == new_path.suffix:
            await message.answer("Error! The image is already in this format 🤔", reply_markup=ReplyKeyboardRemove())
            await state.finish()
            return

        with Image.open(old_path) as f:
            img = f.convert("RGB") if f.mode != "RGB" else f
            img.save(new_path)

        await message.answer_document(
            InputFile(new_path, filename=f"{image_info['original_name']}{new_path.suffix}"),
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Error! Unsupported image format.\n\nI support only AVIF/JPEG/PNG/WEBP images at the moment 😔",
            reply_markup=ReplyKeyboardRemove(),
        )

    await state.finish()
