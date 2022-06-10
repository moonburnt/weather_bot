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

from aiohttp import ClientSession
from typing import Optional
from bs4 import BeautifulSoup as soup
import logging

log = logging.getLogger(__name__)

class WeatherFetcher:
    def __init__(self, user_agent: Optional[str] = None):
        self.session = ClientSession()
        if user_agent is not None:
            self.session.headers["user-agent"] = user_agent

    async def normalize_location(self, request: str) -> Optional[str]:
        """Convert request string to a proper location name.
        In case request is invalid - returns None.
        """

        txt = ""

        async with self.session.get(
            f"https://www.geonames.org/search.html?q={request}"
        ) as answ:
            if answ.status == 200:
                txt = await answ.text()
            else:
                return

        try:
            sauce = soup(txt, "html.parser")
            first_match = sauce.select_one("tr:nth-of-type(3)")
            name_column = first_match.select_one("td:nth-of-type(2)")
            answer = name_column.a.text
        except Exception as e:
            log.warning(f"Unable to normalize a location {request}: {e}")
        else:
            return answer

    async def get_weather(self, request: str) -> str:
        """Get weather for requested location from API"""

        request = await self.normalize_location(request)

        if request is None:
            return "Invalid location, please try something else"

        txt = ""

        async with self.session.get(
            f"https://www.wttr.in/{request}?format=4"
        ) as answ:
            if answ.status == 200:
                txt = await answ.text()
            elif answ.status == 404:
                txt = "Unknown location, please try again"
            else:
                txt = "An error occured, please try different search"
                log.warning(f"Weather api returned {answ.status}")

        return txt
