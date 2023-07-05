import os
import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO)

if (TOKEN := os.getenv('HANDY_IMAGE_CONVERTER_TOKEN')) is None:
    raise ValueError('Error! Assign your Telegram bot token to HANDY_IMAGE_CONVERTER_TOKEN system variable.')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: Message):
    await message.reply("Hi!\n\nI'm HandyImageConverterBot!\n\nPowered by aiogram.")


@dp.message_handler(content_types=['document'])
async def handle_image_as_file(message: Message):
    if image := message.document:
        match image.mime_type:
            case 'image/avif':
                await message.answer(
                    'Select the output format',
                    reply_markup=ReplyKeyboardMarkup([[KeyboardButton('JPEG'),
                                                       KeyboardButton('PNG'),
                                                       KeyboardButton('WEBP')]],
                                                     resize_keyboard=True)
                )
            case 'image/jpeg':
                await message.answer(
                    'Select the output format',
                    reply_markup=ReplyKeyboardMarkup([[KeyboardButton('AVIF'),
                                                       KeyboardButton('PNG'),
                                                       KeyboardButton('WEBP')]],
                                                     resize_keyboard=True)
                )
            case 'image/png':
                await message.answer(
                    'Select the output format',
                    reply_markup=ReplyKeyboardMarkup([[KeyboardButton('AVIF'),
                                                       KeyboardButton('JPEG'),
                                                       KeyboardButton('WEBP')]],
                                                     resize_keyboard=True)
                )
            case 'image/webp':
                await message.answer(
                    'Select the output format',
                    reply_markup=ReplyKeyboardMarkup([[KeyboardButton('AVIF'),
                                                       KeyboardButton('JPEG'),
                                                       KeyboardButton('PNG')]],
                                                     resize_keyboard=True)
                )
            case _:
                await message.answer(
                    'Error! Unsupported image format!\n\n'
                    'I support only avif/jpeg/png/webp images at the moment.'
                )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
