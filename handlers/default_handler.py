from aiogram import types
from config import dp
from aiogram.dispatcher.filters import Text

@dp.message_handler(content_types=types.ContentTypes.ANY, state="*")
async def all_other_messages(message: types.Message):
    if message.content_type == "text":
        await message.reply("Ничего не понимаю!")
        await message.answer("Если вы запутались или что-то стало не понятно, то отправьте слово 'СТАРТ'")

    else:
        await message.reply("Этот бот принимает только текстовые сообщения!")