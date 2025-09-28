from aiogram import executor

from handy_image_converter.main import dp


executor.start_polling(dp, skip_updates=True)
