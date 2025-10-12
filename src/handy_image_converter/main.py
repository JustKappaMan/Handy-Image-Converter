import logging

from aiogram import executor

from handy_image_converter import handlers
from handy_image_converter.loader import dp


def main():
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
