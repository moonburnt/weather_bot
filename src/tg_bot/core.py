## WeatherBot - a simple weather bot for telegram.
## Copyright (c) 2022 moonburnt
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see https://www.gnu.org/licenses/gpl-3.0.txt

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import markdown
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle
from datetime import datetime
from sys import exit
from uuid import uuid4
from typing import Optional
from src.fetcher import WeatherFetcher

import logging

log = logging.getLogger(__name__)

__all__ = [
    "WeatherBot",
    "make_bot",
]

# These are used exclusively as kwargs of executor and must accept dispatcher
# instance as their first argument
async def on_startup(dispatcher: Dispatcher):
    bot_info = await dispatcher.bot.get_me()
    log.info(f"Running WeatherBot as @{bot_info.username} ({bot_info.first_name})")


async def on_shutdown(dispatcher: Dispatcher):
    log.info("Shutting down the bot")


class WeatherBot(Bot):
    def __init__(self, token: str, storage=None):
        super().__init__(token=token)

        if storage is None:
            storage = MemoryStorage()

        self.dp = Dispatcher(self, storage=storage)
        self.weather_fetcher = WeatherFetcher(
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0"
        )

        self.known_weather = {}

    def run(self):
        executor.start_polling(
            self.dp,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
        )


def make_bot(token: str) -> WeatherBot:
    bot = WeatherBot(
        token=token,
    )

    @bot.dp.message_handler(commands=["start"])
    async def send_welcome(message: types.Message):
        """Handler used as response to /start command"""

        await message.reply(
            "Hello, I'm a simple weather bot!\n"
            "If you want to get current weather - just type\n/weather {name-of-city}"
            "\n\nFor example:\n/weather Minsk"
        )

    @bot.dp.message_handler(commands=["help"])
    async def send_welcome(message: types.Message):
        """Handler used as response to /help command"""

        await message.reply(
            "If you want to get current weather - just type\n/weather {name-of-city}"
            "\n\nFor example:\n/weather Minsk\n\n"
            "If you have any questions/suggestions - feel free to open an issue "
            "on bot's github:\nhttps://github.com/moonburnt/weather_bot"
        )

    @bot.dp.message_handler(
        lambda message: message.text != "/weather",
        commands=["weather"],
    )
    async def send_weather(message: types.Message):
        """Handler used as response to /weather command"""

        request = message.text.split("/weather")[1]

        txt = await bot.weather_fetcher.get_weather(request)

        await message.reply(txt)

    @bot.dp.inline_handler()
    async def inline_weather(inline_query: InlineQuery):
        text = inline_query.query or None
        title_msg = ""
        content_msg = ""

        if text is None:
            title_msg = "Give me current weather!"
            bot_info = await bot.get_me()
            content_msg = (
                "In order to get current weather in specific location, "
                f"type location name after @{bot_info.username}. \n\n"
                f"For example:\n@{bot_info.username} Minsk"
            )
        else:
            title_msg = f"Weather in {text}"
            content_msg = await bot.weather_fetcher.get_weather(text)

        input_content = InputTextMessageContent(content_msg)

        item = InlineQueryResultArticle(
            # id must be unique for each answer
            id=f"{uuid4()}-{datetime.now()}",
            title=title_msg,
            input_message_content=input_content,
        )

        # await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)
        await bot.answer_inline_query(inline_query.id, results=[item])

    return bot
