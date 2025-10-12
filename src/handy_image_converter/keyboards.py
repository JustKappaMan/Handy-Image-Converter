from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


mime_types_and_keyboards = {
    "image/avif": ReplyKeyboardMarkup(
        [[KeyboardButton("JPEG"), KeyboardButton("PNG"), KeyboardButton("WEBP")]], resize_keyboard=True
    ),
    "image/jpeg": ReplyKeyboardMarkup(
        [[KeyboardButton("AVIF"), KeyboardButton("PNG"), KeyboardButton("WEBP")]], resize_keyboard=True
    ),
    "image/png": ReplyKeyboardMarkup(
        [[KeyboardButton("AVIF"), KeyboardButton("JPEG"), KeyboardButton("WEBP")]], resize_keyboard=True
    ),
    "image/webp": ReplyKeyboardMarkup(
        [[KeyboardButton("AVIF"), KeyboardButton("JPEG"), KeyboardButton("PNG")]], resize_keyboard=True
    ),
}
