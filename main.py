import os
import logging
import pathlib

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, InputFile, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from PIL import Image
# noinspection PyUnresolvedReferences
import pillow_avif

logging.basicConfig(level=logging.INFO)

if (TOKEN := os.getenv('HANDY_IMAGE_CONVERTER_TOKEN')) is None:
    raise ValueError('Error! Assign your Telegram bot token to HANDY_IMAGE_CONVERTER_TOKEN system variable.')

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

mime_types_and_keyboards = {
    'image/avif': ReplyKeyboardMarkup([[KeyboardButton('JPEG'), KeyboardButton('PNG'), KeyboardButton('WEBP')]],
                                      resize_keyboard=True),
    'image/jpeg': ReplyKeyboardMarkup([[KeyboardButton('AVIF'), KeyboardButton('PNG'), KeyboardButton('WEBP')]],
                                      resize_keyboard=True),
    'image/png': ReplyKeyboardMarkup([[KeyboardButton('AVIF'), KeyboardButton('JPEG'), KeyboardButton('WEBP')]],
                                     resize_keyboard=True),
    'image/webp': ReplyKeyboardMarkup([[KeyboardButton('AVIF'), KeyboardButton('JPEG'), KeyboardButton('PNG')]],
                                      resize_keyboard=True)
}

supported_formats = {'avif', 'jpeg', 'png', 'webp'}


class ImageInfo(StatesGroup):
    file_path = State()
    output_format = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    await message.answer(
        'Hi! I\'m [HandyImageConverterBot](https://t.me/HandyImageConverterBot).\n\n'
        'Just send me any image *as file* ☺️',
        parse_mode='Markdown'
    )


@dp.message_handler(commands=['help'])
async def send_help(message: Message):
    await message.answer(
        '👨‍💻 [Author](https://t.me/SuspiciousUser)\n'
        '🤖 [Source code](https://github.com/JustKappaMan/Handy-Image-Converter)',
        parse_mode='Markdown',
        disable_web_page_preview=True
    )


@dp.message_handler(content_types=['document'])
async def handle_image_as_file(message: Message, state: FSMContext):
    if image := message.document:
        if image.mime_type in mime_types_and_keyboards:
            if (file_path := pathlib.Path(image.file_name.lower())).suffix == '.jpg':
                file_path = file_path.with_suffix('.jpeg')

            await image.download(destination_file=file_path)
            await state.update_data(file_path=file_path)

            await ImageInfo.output_format.set()
            await message.answer('Select the output format', reply_markup=mime_types_and_keyboards[image.mime_type])
        else:
            await message.answer(
                'Error! Unsupported image format.\n\n'
                'I support only AVIF/JPEG/PNG/WEBP images at the moment 😔'
            )


@dp.message_handler(state=ImageInfo.output_format)
async def send_image_as_file(message: Message, state: FSMContext):
    message.text = message.text.lower()

    if message.text in supported_formats:
        old_img_path = (await state.get_data())['file_path']
        new_img_path = old_img_path.with_suffix(f'.{message.text}')

        if old_img_path.suffix == new_img_path.suffix:
            await message.answer('Error! The image is already in this format 🤔', reply_markup=ReplyKeyboardRemove())
            await state.finish()
            return

        with Image.open(old_img_path) as old_img:
            if old_img.mode != 'RGB':
                old_img = old_img.convert('RGB')
            old_img.save(new_img_path)

        await message.answer_document(
            InputFile(new_img_path, filename=new_img_path.name),
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            'Error! Unsupported image format.\n\n'
            'I support only AVIF/JPEG/PNG/WEBP images at the moment 😔',
            reply_markup=ReplyKeyboardRemove()
        )

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
