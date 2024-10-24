from google.oauth2.service_account import Credentials
import gspread, asyncio
import config, database


class SheetManager:
    def __init__(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(config.creds_file_path, scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(config.sheet_key).sheet1
        self.db = database.Database()

    async def insert_into_sheet(self, expense):
        loop = asyncio.get_event_loop()
        all_insertions = await loop.run_in_executor(None, self.sheet.get_values, 'C19:C997')
        cols = { 'time': 3, 'currency': {'rub': 4, 'tng': 5, 'usd': 6}, 'description': 7 }
        try:
            last_insertion_time = all_insertions[-1][0]
            row = await loop.run_in_executor(None, self.sheet.find, last_insertion_time)
            row = row.row + 1
        except IndexError:
            row = 19
        await loop.run_in_executor(None, self.sheet.update_cell, row, cols['time'], expense['time'])
        await loop.run_in_executor(None, self.sheet.update_cell, row, cols['currency'][expense['currency']], expense['amount'])
        await loop.run_in_executor(None, self.sheet.update_cell, row, cols['description'], expense['description'])

    async def remove_from_sheet(self, command):
        loop = asyncio.get_event_loop()
        if command == 'all':
            await loop.run_in_executor(None, self.sheet.batch_clear, ['C19:G996'])
        elif command == 'last':
            all_insertions = await loop.run_in_executor(None, self.sheet.get_values, 'C19:G997')
            try:
                last_insertion_time = all_insertions[-1][0]
                row = await loop.run_in_executor(None, self.sheet.find, last_insertion_time)
                row = row.row
            except IndexError:
                row = 19
            await loop.run_in_executor(None, self.sheet.batch_clear, [f'C{row}:G{row}'])