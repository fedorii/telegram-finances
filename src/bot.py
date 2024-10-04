import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import config
from database import DatabaseManager, TableFormatter, SheetManager


db_manager = DatabaseManager()
sheet_manager = SheetManager(config.sheet_key)
table_formatter = TableFormatter()


class StateMachine(StatesGroup):
    waiting_for_amount = State()


async def command_start(message: Message):
    await message.answer("""
Welcome to Telegram Finances Bot!
Type /add to add new expense.
""")


async def command_help(message: Message):
    await message.answer("""                         
I'm here to help you account your cash expenditures.
Here's a list of the available commands:
    /start - Start the bot and get a welcome message
    /add - Add new expense information
    /remove - Remove an expense information
    /show - Show all expenses
    /help - Show this help message
""")


async def command_currency(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="RUB", callback_data="currency_rub"),
            InlineKeyboardButton(text="TNG", callback_data="currency_tng"),
            InlineKeyboardButton(text="USD", callback_data="currency_usd")
        ]
    ])
    await message.answer("Please choose the currency:", reply_markup=keyboard)


async def command_remove(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="latest", callback_data="remove_latest"),
            InlineKeyboardButton(text="all", callback_data="remove_all")
        ]
    ])
    await message.answer("Please choose the action type:", reply_markup=keyboard)


async def command_show_expenses(message: Message):
    data = db_manager.get_table_data()
    table = table_formatter.format_table(data)
    await message.answer(f"<pre>{table}</pre>", parse_mode="HTML")


async def callback_controller(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("currency_"):
        currency = callback.data.split("_")[1]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="No category", callback_data="category_no"),
            InlineKeyboardButton(text="Food", callback_data="category_food")
        ], [
            InlineKeyboardButton(text="Transport", callback_data="category_food"),
            InlineKeyboardButton(text="Utilities", callback_data="category_utilities")
        ], [
            InlineKeyboardButton(text="Education", callback_data="category_education"),
            InlineKeyboardButton(text="Medical", callback_data="category_medical")
        ], [
            InlineKeyboardButton(text="Shopping", callback_data="category_shopping"),
            InlineKeyboardButton(text="Tax", callback_data="category_tax")
        ], [
            InlineKeyboardButton(text="Sub", callback_data="category_sub"),
            InlineKeyboardButton(text="Investments", callback_data="category_investments")
        ]])
        await state.update_data(currency=currency)
        await callback.message.answer("Please choose the category:", reply_markup=keyboard)
    if callback.data.startswith("remove_"):
        cmd_type = callback.data.split("_")[1]
        db_manager.remove_from_db(cmd_type)
        await callback.message.answer("Information has been removed")
    if callback.data.startswith("category_"):
        category = callback.data.split("_")[1]
        await state.update_data(category=category)
        await callback.message.answer("Please enter the expense in this form: {amount} {description}")
        await state.set_state(StateMachine.waiting_for_amount)
        

async def user_input_controller(message: Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        user_input = message.text.split(maxsplit=1)
        expense = {
            "time": datetime.now().isoformat(),
            "amount": user_input[0],
            "currency": user_data.get("currency"),
            "category": user_data.get("category"),
            "description": " ".join(user_input[1:])
        }
        db_manager.insert_new_data(expense)
        sheet_manager.insert_new_data(expense, db_manager)
        await message.answer(f"Done! Use /add to add new expense")
        await state.clear()
    except ValueError:
        await message.answer("Invalid format. Please use: {amount} {category}")


async def main():
    bot = Bot(config.bot_token)
    dp = Dispatcher()

    dp.message.register(command_start, CommandStart())
    dp.message.register(command_help, Command("help"))
    dp.message.register(command_currency, Command("add"))
    dp.message.register(command_remove, Command("remove"))
    dp.message.register(command_show_expenses, Command("show"))
    dp.callback_query.register(callback_controller)
    dp.message.register(user_input_controller, StateFilter(StateMachine.waiting_for_amount))

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        print("bot disabled")
