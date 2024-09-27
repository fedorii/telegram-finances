import gspread
from google.oauth2.service_account import Credentials

from config import sheet_key
import db


scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_key).sheet1


def update_sheet(date, amount, currency, category, description):
    data = db.get_expenses()
    if len(data) == 0:
        sheet.update_cell(17, 3, date)
        sheet.update_cell(17, 7, description)
        if currency == "rub":
            sheet.update_cell(17, 4, amount)
        if currency == "tng":
            sheet.update_cell(17, 5, amount)
        if currency == "usd":
            sheet.update_cell(17, 6, amount)
    else:  
        prev_data = data[-1] 
        sheet.update_cell(sheet.find(prev_data[1]).row + 1, 3, date)
        sheet.update_cell(sheet.find(prev_data[1]).row + 1, 7, description)
        if currency == "rub":
            sheet.update_cell(sheet.find(prev_data[1]).row + 1, 4, amount)
        if currency == "tng":
            sheet.update_cell(sheet.find(prev_data[1]).row + 1, 5, amount)
        if currency == "usd":
            sheet.update_cell(sheet.find(prev_data[1]).row + 1, 6, amount)
