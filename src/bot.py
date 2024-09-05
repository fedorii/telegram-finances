import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from settings import BOT_TOKEN


dp = Dispatcher()


class ExpenseStates(StatesGroup):
    waiting_for_expense = State()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("""
Welcome to Telegram Finances Bot!
                         
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
    /help - Show this help message
    /settings - Adjust your user settings
""")
    

@dp.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    await message.answer("Please enter your expense in the format: {amount} {category}")
    await state.set_state(ExpenseStates.waiting_for_expense)


@dp.message(StateFilter(ExpenseStates.waiting_for_expense))
async def process_expense(message: Message, state: FSMContext):
    try:
        amount, category = message.text.split(maxsplit=1)
        amount = float(amount)
        await message.answer(f"Expense information added: {amount} in {category}")
        await state.clear()
    except ValueError:
        await message.answer("Invalid format. Please use: {amount} {category}")


async def main(): 
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        print("bot disabled")
