from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import markdown
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle
from aiohttp import client_exceptions, ClientSession
from asyncio import gather
from sys import exit
from uuid import uuid4
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

        self.fetcher_session = ClientSession()
        self.fetcher_session.headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0"

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

    @bot.dp.message_handler(commands=["help", "start"])
    async def send_welcome(message: types.Message):
        """Handler used as response to /help and "start" commands"""

        await message.reply(
            "Hello, I'm a simple weather bot!\n"
            "If you want to ask for a weather - just type /weather {name-of-city}\n"
            "For example:\nweather Minsk"
        )

    async def get_weather(request:str) -> str:
        """Get weather for requested location from API"""

        txt = ""

        async with bot.fetcher_session.get(
            f"https://www.wttr.in/{request}?format=4"
        ) as answ:
            match answ.status:
                case 200:
                    txt = await answ.text()
                case 404:
                    txt = "Unknown location, please try again"
                case _:
                    txt = "An error occured, please try different search"
                    log.warning(f"Weather api returned {answ.status_code}")

        return txt

    @bot.dp.message_handler(
        lambda message: message.text != "/weather",
        commands=["weather"],
    )
    async def send_weather(message: types.Message):
        """Handler used as response to /weather command"""

        request = message.text.split("/weather")[1]

        txt = await get_weather(request)

        await message.reply(txt)

    @bot.dp.inline_handler()
    async def inline_weather(inline_query: InlineQuery):
        text = inline_query.query or "КАЗАХСТАН"
        content = await get_weather(text)
        input_content = InputTextMessageContent(content)

        item = InlineQueryResultArticle(
            # id must be unique for each answer
            id = str(uuid4()),
            title=f"Weather in {text}",
            input_message_content = input_content,
        )

        # await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)
        await bot.answer_inline_query(inline_query.id, results=[item])


    return bot
