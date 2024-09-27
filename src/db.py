import sqlite3
from tabulate import tabulate


conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT, amount REAL, currency TEXT, category TEXT, description TEXT)
''')
conn.commit()
conn.close()


def add_expense(time, amount, currency, category, description) -> None:
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (time, amount, currency, category, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (time, amount, currency, category, description))
    conn.commit()
    conn.close()

def remove_expense(cmd_type) -> None:
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    if cmd_type == "latest":
        cursor.execute("DELETE FROM expenses WHERE id = (SELECT MAX(id) from expenses)")
    if cmd_type == "all":
        cursor.execute("DELETE FROM expenses")
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
