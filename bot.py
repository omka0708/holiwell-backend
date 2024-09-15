import asyncio
import logging
import os

import requests
import shortuuid
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.types import Message

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))

dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = '💬 Отправьте любой текст для регистрации в Holiwell'
    await bot.send_message(chat_id=message.from_user.id, text=text)


@dp.message()
async def echo(message: Message):
    password = shortuuid.ShortUUID().random(length=6)
    response = requests.post(
        f"http://{os.getenv('HOLIWELL_APP_HOST')}:{os.getenv('HOLIWELL_APP_PORT')}"
        f"/auth/register", json={
            'password': password,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'tg_id': message.from_user.id
        }
    )
    if response.status_code == 201:
        text = (f"✅ Вы успешно зарегистрировались\!"
                f"\n\nВаш логин: ```{message.from_user.id}```"
                f"\nВаш пароль: ```{password}```"
                f"\n\n_\(нажмите, чтобы скопировать\)_")
    elif response.status_code == 400:
        text = "❕ Вы уже зарегистрированы"
    else:
        text = "❌ Произошла ошибка"
    result = response.json()
    await bot.send_message(chat_id=message.from_user.id, text=text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
