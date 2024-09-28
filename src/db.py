import sqlite3
from tabulate import tabulate
from PIL import ImageColor 

from google.oauth2.service_account import Credentials
import gspread

from config import sheet_key


conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT, amount REAL, currency TEXT, category TEXT, description TEXT)
''')
conn.commit()
conn.close()

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_key).sheet1


def hex_to_rgb(hex_color):
    rgb_color = ImageColor.getrgb(hex_color)
    return rgb_color

def update_cell_color(action, category=None, row=None, col=None):
    if action == "remove":
        cell = f"D{row}:F{row}"
        sheet.format(cell, {
            "backgroundColor": {
                "red": 1.0,
                "green": 1.0,
                "blue": 1.0
                }
        })
    elif action == "add":
        cell = gspread.utils.rowcol_to_a1(row, col)
        colors = {
            "no": "#d3d3d3",
            "food": "#f69a3f",
            "transport": "#7fabf6",
            "utilities": "#97d07d",
            "education": "#97d07d",
            "medical": "#cd4747",
            "shopping": "#f1c130",
            "tax": "#b06313",
            "sub": "#3159a2",
            "investments": "#8fe1d2"
        }
        sheet.format(cell, {
            "backgroundColor": {
                "red": hex_to_rgb(colors[category])[0] / 255,
                "green": hex_to_rgb(colors[category])[1] / 255,
                "blue": hex_to_rgb(colors[category])[2] / 255
            }
        })
    elif action == "remove_all":
        sheet.format("D19:F10000", {
            "backgroundColor": {
                "red": 1.0,
                "green": 1.0,
                "blue": 1.0
            }
        })

def add_expense(expense) -> None:
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    if len(expenses) == 0:
        row = 19
    else:
        prev_expense = expenses[-1]
        row = sheet.find(prev_expense[1]).row + 1
    currency_column = {"rub": 4, "tng": 5, "usd": 6}
    expense_column = currency_column[expense["currency"]]
    sheet.update_cell(row, 3, expense["date"])
    sheet.update_cell(row, expense_column, expense["amount"])
    sheet.update_cell(row, 7, expense["description"])
    update_cell_color(action="add", category=expense["category"],
                      row=row, col=expense_column)

    cursor.execute('''
        INSERT INTO expenses (time, amount, currency, category, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (expense["date"], expense["amount"], expense["currency"],
          expense["category"], expense["description"]))
    conn.commit()
    conn.close()

def remove_expense(cmd_type) -> None:
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    if cmd_type == "latest":
        cursor.execute("DELETE FROM expenses WHERE id = (SELECT MAX(id) from expenses)")
        cursor.execute("SELECT * FROM expenses")
        expenses = cursor.fetchall()
        if len(expenses) != 0:
            prev_expense = expenses[-1]
            row = sheet.find(prev_expense[1]).row
            sheet.delete_rows(row)
            update_cell_color(action="remove", row=row)
    elif cmd_type == "all":
        cursor.execute("DELETE FROM expenses")
        sheet.batch_clear(["C19:G10000"])
        update_cell_color(action="remove_all")
    conn.commit()
    conn.close()

def get_expenses() -> list:
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    conn.close()
    return expenses

def format_expenses() -> str:
    data = get_expenses()
    columns = ["ID", "date", "amount", "currency", "category", "description"]
    table = tabulate(data, columns, tablefmt="grid")
    return table
