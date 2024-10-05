from __future__ import annotations
import sqlite3
from typing import List, Dict, Any, Tuple
from contextlib import contextmanager

import tabulate
from google.oauth2.service_account import Credentials
import gspread


__all__ = ["DatabaseManager", "TableFormatter", "SheetManager"]


class DatabaseManager:
    def __init__(self, db_name: str="expenses.db") -> None:
        self.db_name = db_name
        self.create_table()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
        finally:
            conn.close()
    
    def create_table(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL
                )
            ''')
            conn.commit()

    def get_table_data(self) -> List[Tuple]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses")
            return cursor.fetchall()
        
    def insert_new_data(self, new_data: Dict) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (time, amount, currency, category, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (new_data["time"], new_data["amount"], new_data["currency"],
                  new_data["category"], new_data["description"]))
            conn.commit()
        
    def remove_from_db(self, command: str) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if command == "all":
                cursor.execute("DELETE FROM expenses")
            elif command == "latest":
                cursor.execute("DELETE FROM expenses WHERE id = (SELECT MAX(id) from expenses)")
            conn.commit()


class TableFormatter:
    @staticmethod
    def format_table(data: List[Tuple]) -> str:
        columns = ["ID", "time", "amount", "currency", "category", "description"]
        return tabulate.tabulate(data, columns, tablefmt="grid")
    

class SheetManager:
    def __init__(self, sheet_key: str, creds_file: str="credentials.json",
                 scopes_address: str="https://www.googleapis.com/auth/spreadsheets") -> None:
        self.scopes = [scopes_address]
        self.creds = Credentials.from_service_account_file(creds_file, scopes=self.scopes)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_key(sheet_key).sheet1

    def insert_new_data(self, new_data: Dict, db_manager: DatabaseManager) -> None:
        try:
            last_expense_time = self.sheet.get_all_values("C19:C10000")[-1][0]
            row = self.sheet.find(last_expense_time).row + 1
        except IndexError:
            row = 19
        columns = {"time": 3, "currency": {"rub": 4, "tng": 5, "usd": 6}, "description": 7}
        self.sheet.update_cell(row, columns["time"], new_data["time"])
        self.sheet.update_cell(row, columns["currency"][new_data["currency"]], new_data["amount"])
        self.sheet.update_cell(row, columns["description"], new_data["description"])

    def remove_from_sheet(self, command: str) -> None:
        if command == "all":
            self.sheet.batch_clear(["C19:G996"])
        elif command == "latest":
            try:
                last_expense_time = self.sheet.get_all_values("C19:C10000")[-1][0]
                row = self.sheet.find(last_expense_time).row
                self.sheet.batch_clear([f"C{row}:G{row}"])
            except IndexError:
                pass
            