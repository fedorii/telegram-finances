import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import db
from config import bot_token
import spreadsheets


dp = Dispatcher()


class StateMachine(StatesGroup):
    waiting_for_amount = State()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("""
Welcome to Telegram Finances Bot!
Type /add to add new expense.
""")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("""                         
I'm here to help you account your cash expenditures.
Here's a list of the available commands:
    /start - Start the bot and get a welcome message
    /add - Add new expense information
    /remove - Remove an expense information
    /show - Show all expenses
    /help - Show this help message
""")

@dp.message(Command("add"))
async def cmd_currency(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="RUB", callback_data="currency_rub"),
            InlineKeyboardButton(text="TNG", callback_data="currency_tng"),
            InlineKeyboardButton(text="USD", callback_data="currency_usd")
        ]
    ])
    await message.answer("Please choose the currency:", reply_markup=keyboard)

@dp.message(Command("remove"))
async def cmd_remove(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="latest", callback_data="remove_latest"),
            InlineKeyboardButton(text="all", callback_data="remove_all")
        ]
    ])
    await message.answer("Please choose the action type:", reply_markup=keyboard)

@dp.message(Command("show"))
async def cmd_show_expenses(message: Message):
    table = db.format_expenses()
    await message.answer(f"<pre>{table}</pre>", parse_mode="HTML")

@dp.callback_query()
async def callback_controller(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("currency_"):
        currency = callback.data.split("_")[1]
        await state.update_data(currency=currency)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Food", callback_data="category_food"),
            InlineKeyboardButton(text="Transport", callback_data="category_food")
        ], [
            InlineKeyboardButton(text="Utilities", callback_data="category_utilities"),
            InlineKeyboardButton(text="Education", callback_data="category_education")
        ], [
            InlineKeyboardButton(text="Medical", callback_data="category_medical"),
            InlineKeyboardButton(text="Shopping", callback_data="category_shopping")
        ], [
            InlineKeyboardButton(text="Tax", callback_data="category_tax"),
            InlineKeyboardButton(text="Sub", callback_data="category_sub")]])
        await callback.message.answer("Please choose the category:", reply_markup=keyboard)
    
    if callback.data.startswith("category_"):
        category = callback.data.split("_")[1]
        await state.update_data(category=category)
        await callback.message.answer("Please enter the expense in this form: {amount} {description}")
        await state.set_state(StateMachine.waiting_for_amount)

    if callback.data.startswith("remove_"):
        cmd_type = callback.data.split("_")[1]
        db.remove_expense(cmd_type)
        # if cmd_type == "latest":                  # Implement removing 
        #     spreadsheets.remove_update_sheet()    # action in Google Sheets
        await callback.message.answer("Information has been removed")

@dp.message(StateFilter(StateMachine.waiting_for_amount))
async def process_amount(message: Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        user_input = message.text.split(maxsplit=1)
        amount, description = user_input[0], " ".join(user_input[1:])
        amount = float(amount)
        time = datetime.now().isoformat()
        currency = user_data.get("currency")
        category = user_data.get("category")

        spreadsheets.update_sheet(time, amount, currency, category, description)
        db.add_expense(time, amount, currency, category, description)
        
        await message.answer(f"Done! Use /add to add new expense")
        await state.clear()
    except ValueError:
        await message.answer("Invalid format. Please use: {amount} {category}")


async def main(): 
    bot = Bot(bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        print("bot disabled")
