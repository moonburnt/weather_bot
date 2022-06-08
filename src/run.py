import argparse
from os import environ
from os.path import join
from sys import exit
from dotenv import load_dotenv
import logging

log = logging.getLogger("newsbot")
log.setLevel(logging.INFO)
formatter = logging.Formatter(
    fmt="[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)

ap = argparse.ArgumentParser()
ap.add_argument("--config", help="Path to configuration file. Default - './.env'")
ap.add_argument(
    "--debug",
    action="store_true",
    help="Adds debug messages to log output",
)
args = ap.parse_args()

load_dotenv(dotenv_path=(args.config or join(".", ".env")))

if args.debug:
    log.setLevel(logging.DEBUG)

bot_token = environ.get("WEATHER_BOT_TOKEN", None)
if not bot_token:
    log.critical(
        "You didn't specify bot's token! Either set WEATHER_BOT_TOKEN environment "
        "variable manually, or add it to your .env file.\nAbort"
    )
    exit(1)

from src.tg_bot import make_bot

bot = make_bot(
    token=bot_token,
)
bot.run()
