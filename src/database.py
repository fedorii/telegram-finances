import sqlite3
from contextlib import contextmanager
import tabulate


class Database:
    def __init__(self, db_path='expenses.db'):
        self.db_path = db_path
        self.create_table()

    @contextmanager
    def cursor_handler(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            conn.commit()
            conn.close()

    def create_table(self):
        with self.cursor_handler() as cursor:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        time TEXT NOT NULL,
                        amount REAL NOT NULL,
                        currency TEXT NOT NULL,
                        category TEXT NOT NULL,
                        description TEXT
                    )
                ''')

    def get_expenses(self):
        with self.cursor_handler() as cursor:
            cursor.execute('SELECT * FROM expenses')
            expenses = cursor.fetchall()
            return expenses
        
    def add_expense(self, expense):
        with self.cursor_handler() as cursor:
            cursor.execute('''
                INSERT INTO expenses (time, amount, currency, category, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (expense['time'], expense['amount'], expense['currency'],
                  expense['category'], expense['description']))

    def remove_expense(self, command):
        with self.cursor_handler() as cursor:
            if command == 'all':
                cursor.execute('DELETE FROM expenses')
            elif command == 'last':
                cursor.execute(f'SELECT COUNT(*) FROM expenses')
                expenses_count = cursor.fetchone()[0]
                if expenses_count:
                    cursor.execute('DELETE FROM expenses WHERE id = (SELECT MAX(id) from expenses)')

    def format_table(self):
        columns = ['id', 'time', 'amount', 'currency', 'category', 'description']
        return tabulate.tabulate(self.get_expenses(), columns, tablefmt='grid')
