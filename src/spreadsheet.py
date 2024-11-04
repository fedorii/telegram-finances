from google.oauth2.service_account import Credentials
import gspread
import config, database


class SheetManager:
    def __init__(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(config.creds_file_path, scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(config.sheet_key).sheet1
        self.db = database.Database()

    def insert_into_sheet(self, expense):
        all_insertions = self.sheet.get_values('C19:C997')
        cols = { 'time': 3, 'currency': {'rub': 4, 'tng': 5, 'usd': 6}, 'description': 7 }
        try:
            last_insertion_time = all_insertions[-1][0]
            row = self.sheet.find(last_insertion_time).row + 1
        except IndexError:
            row = 19
        self.sheet.update_cell(row, cols['time'], expense['time'])
        self.sheet.update_cell(row, cols['currency'][expense['currency']], expense['amount'])
        self.sheet.update_cell(row, cols['description'], expense['description'])
        self.sheet.format(self.sheet.cell(row, cols['currency']).address,
                          {'backgroundColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0} })
        self.update_stats_section('add', expense)

    def remove_from_sheet(self, command):
        if command == 'all':
            self.sheet.batch_clear(['C19:G996'])
            self.update_stats_section(command)
        elif command == 'last':
            all_insertions = self.sheet.get_values('C19:G997')
            try:
                last_insertion_time = all_insertions[-1][0]
                last_insertion = self.sheet.find(last_insertion_time) 
                row = last_insertion.row
            except IndexError:
                row = 19
            expense = self.sheet.get_values(f'D{row}:F{row}')
            expense = [i[0] for i in expense if len(i) == 1]
            self.sheet.batch_clear([f'C{row}:G{row}'])
            self.update_stats_section(command, expense[0])

    def update_stats_section(self, command, expense=None):
        rows = {'no category': 6, 'food': 7, 'transport': 8,
                'utilities': 9, 'education': 10, 'medical': 11,
                'shopping': 12, 'tax': 13, 'sub': 14, 'investments': 15}
        cols = {'rub': 4, 'tng': 5, 'usd': 6, 'usd_tot': 7}
        if command == 'all':
            self.sheet.batch_clear(['D6:G16'])
        elif command in ['add', 'last']:
            if command == 'add':    
                row = rows[expense['category']]
                col = cols[expense['currency']]
                cell_value = self.sheet.cell(row, col).value
                cell_value = 0 if cell_value == None else int(cell_value)
                self.sheet.update_cell(row, col, cell_value + int(expense['amount']))
            elif command == 'last':
                self.sheet.update_cell(row, col, cell_value - int(expense))
