import asyncio
import json
import logging

import aiohttp
from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import CommandStart
from redis.asyncio import Redis

from settings import BOT_TOKEN, KEY_NAME, REDIS_HOST, REDIS_PORT

bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher()

async def get_dollar_rate():
    #async with Redis(host=REDIS_HOST, port=REDIS_PORT) as redis_client:
    #    value = await redis_client.get(KEY_NAME)
    #    if value is not None:
    #        return f"{float(value)} рублей"

    async with aiohttp.ClientSession() as session:
        response = await session.get('https://www.cbr-xml-daily.ru/latest.js')
        if response.status == 200:
            text = await response.text()
            data = json.loads(text)
            dollar_rate = 1/data['rates']['USD']
            #await redis_client.set(KEY_NAME,dollar_rate,60)
            return f"{dollar_rate} рублей"
        return None


@dispatcher.message(CommandStart())
async def on_start(message: types.Message):
    await message.answer(text="Добрый день. Как вас зовут?")


@dispatcher.message()
async def echo_message(message: types.Message):
    dollar_rate = await get_dollar_rate()
    if dollar_rate is None:
        dollar_rate = 'Не удалось определить!'
    if message.text:
        await message.answer(text=f"Рад знакомству, {message.text}! Курс доллара сегодня {dollar_rate}")
    else:
        await message.answer(text=f"Курс доллара сегодня {dollar_rate}")


async def main():
    logging.basicConfig(level=logging.INFO)
    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())