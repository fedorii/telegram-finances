import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import bot_token
import db


dp = Dispatcher()


class ExpenseStates(StatesGroup):
    waiting_command = State()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("""
Welcome to Telegram Finances Bot!\n
To add new expense information, use /add command.
First enter the amount of the expense and
then a space for the category of expense. 
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
async def cmd_add(message: Message, state: FSMContext):
    await message.answer("Please enter your expense in the format: {amount} {category}")
    await state.update_data(action="add")
    await state.set_state(ExpenseStates.waiting_command)

@dp.message(Command("remove"))
async def cmd_remove(message: Message, state: FSMContext):
    await message.answer("Please choose the command type: /byid, /latest, /all")
    await state.update_data(action="remove")
    await state.set_state(ExpenseStates.waiting_command)

@dp.message(Command("show"))
async def cmd_remove(message: Message):
    await message.answer(str(db.get_all_expenses()))

@dp.message(StateFilter(ExpenseStates.waiting_command))
async def process_expense(message: Message, state: FSMContext):
    user_data = await state.get_data()
    action = user_data.get("action")
    match action:
        case "add":
            try:
                amount, category = message.text.split(maxsplit=1)
                amount = float(amount)
                time = datetime.now().isoformat()
                db.add_expense(time, amount, category)
                await message.answer(f"Expense information added: {amount} in {category}")
                await state.clear()
            except ValueError:
                await message.answer("Invalid format. Please use: {amount} {category}")
        case "remove":
            db.remove_expense(message.text)
            await message.answer("Information has been removed")
    await state.clear()


async def main(): 
    bot = Bot(bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        print("bot disabled")
