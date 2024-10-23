import sqlite3


class Database:
    def __init__(self, db_path='expenses.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()


    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT UNIQUE NOT NULL,
                username TEXT,
                language TEXT DEFAULT 'en'
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                time TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) 
            )
        ''')
        self.conn.commit()


    def check_user(self, telegram_id):
        self.cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id))
        return self.cursor.fetchone()

    
    def add_user(self, telegram_id, username=None, language='en'):
        self.cursor.execute('''
            INSERT INTO users (telegram_id, username, language)
            VALUES (?, ?, ?)
        ''', (telegram_id, username, language))


    def add_expense(self, expense):
        user = self.check_user(expense['id'])
        self.cursor.execute('''
            INSERT INTO expenses (user_id, amount, category, description)
            VALUES (?, ?, ?, ?)
        ''', expense['id'], expense['amount'], expense['category'], expense['description'])
        self.conn.commit()


    def remove_expense(self, command):
        if command == 'all':
            self.cursor.execute('DELETE * FROM expenses')
        elif command == 'latest':
            self.cursor.execute('''
                DELETE FROM expenses WHERE id = (SELECT MAX(id) from expenses)
            ''')
        self.conn.commit()


    def get_expenses(self, telegram_id):
        user_id = self.check_user(telegram_id)[0]
        self.cursor.execute('SELECT * FROM expenses WHERE user_id = ?', (user_id))
        expenses = self.cursor.fetchall()
        return expenses
    