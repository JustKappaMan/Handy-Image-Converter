import os
import uuid
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

supported_formats = {'avif', 'jpg', 'jpeg', 'png', 'webp'}


class ImageInfo(StatesGroup):
    original_name = State()
    temporary_copy_path = State()
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
        'Just send me any image *as file* ☺️\n\n'
        '👨‍💻 [Author](https://t.me/SuspiciousUser)\n'
        '🤖 [Source code](https://github.com/JustKappaMan/Handy-Image-Converter)',
        parse_mode='Markdown',
        disable_web_page_preview=True
    )


@dp.message_handler(content_types=['photo'])
async def handle_compressed_image(message: Message):
    await message.answer('Please, send images *as files* 🙂', parse_mode='Markdown')


@dp.message_handler(content_types=['document'])
async def handle_uncompressed_image(message: Message, state: FSMContext):
    if image := message.document:
        if image.mime_type in mime_types_and_keyboards:
            name, extension = image.file_name.rsplit('.', 1)
            tmp_copy_path = pathlib.Path('images', f'{uuid.uuid4().hex}.{extension}')
            await image.download(destination_file=tmp_copy_path)
            await state.update_data(original_name=name, temporary_copy_path=tmp_copy_path)

            await ImageInfo.output_format.set()
            await message.answer('Select the output format', reply_markup=mime_types_and_keyboards[image.mime_type])
        else:
            await message.answer(
                'Error! Unsupported image format.\n\n'
                'I support only AVIF/JPEG/PNG/WEBP images at the moment 😔'
            )


@dp.message_handler(state=ImageInfo.output_format)
async def send_image_back(message: Message, state: FSMContext):
    message.text = message.text.lower()

    if message.text in supported_formats:
        image_info = await state.get_data()
        old_path = image_info['temporary_copy_path']
        new_path = old_path.with_suffix(f'.{message.text}')

        if old_path.suffix == new_path.suffix:
            await message.answer('Error! The image is already in this format 🤔', reply_markup=ReplyKeyboardRemove())
            await state.finish()
            return

        with Image.open(old_path) as old_img:
            if old_img.mode != 'RGB':
                old_img = old_img.convert('RGB')
            old_img.save(new_path)

        await message.answer_document(
            InputFile(new_path, filename=f'{image_info["original_name"]}{new_path.suffix}'),
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
