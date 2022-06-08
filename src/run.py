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
