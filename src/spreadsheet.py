from google.oauth2.service_account import Credentials
import gspread, sqlite3, aiohttp, asyncio

import config


class Sheet:
    def __init__(self, key=config.sheet_key):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(key).sheet1

    async def insert_into_sheet(self, expense):
        loop = asyncio.get_event_loop()

        await loop.run_in_executor(None, self.sheet.update_acell())

    async def remove_from_sheet(self, command):
        pass

    async def update_stats_section(self):
        pass