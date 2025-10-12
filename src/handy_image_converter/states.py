from aiogram.dispatcher.filters.state import State, StatesGroup


class ImageInfo(StatesGroup):
    original_name = State()
    temporary_copy_path = State()
    output_format = State()
