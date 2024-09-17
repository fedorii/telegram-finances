import sqlite3


def add_expense(time, amount, category):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (time, amount, category)
        VALUES (?, ?, ?)
    ''', (time, amount, category))
    conn.commit()
    conn.close()

def remove_expense(command, expense_id=None):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    match command:
        case "/byid":
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id))
        case "/latest":
            cursor.execute("DELETE FROM expenses WHERE id = (SELECT MAX(id) from expenses)")
        case "/all":
            cursor.execute("DELETE FROM expenses")
        case _:
            raise ValueError("Unknown command")
    conn.commit()
    conn.close()

def get_all_expenses() -> list:
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, time, amount, category FROM expenses")
    expenses = cursor.fetchall()
    conn.close()
    return expenses


conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT, amount REAL, category TEXT)
''')
conn.commit()
conn.close()
