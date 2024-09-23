import sqlite3


def add_expense(time, amount, category, currency):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (time, amount, category, currency)
        VALUES (?, ?, ?, ?)
    ''', (time, amount, category, currency))
    conn.commit()
    conn.close()

def remove_expense(cmd_type):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    if cmd_type == "latest":
        cursor.execute("DELETE FROM expenses WHERE id = (SELECT MAX(id) from expenses)")
    if cmd_type == "all":
        cursor.execute("DELETE FROM expenses")
    conn.commit()
    conn.close()

def get_all_expenses() -> list:
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, time, amount, category, currency FROM expenses")
    expenses = cursor.fetchall()
    conn.close()
    return expenses


conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT, amount REAL, category TEXT, currency TEXT)
''')
conn.commit()
conn.close()
