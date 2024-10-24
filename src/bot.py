from aiogram import Bot, Dispatcher
from aiogram.types import (Message, InlineKeyboardMarkup,
    InlineKeyboardButton, CallbackQuery)
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import asyncio
from datetime import datetime
from functools import wraps

import config, database, spreadsheet


db = database.Database()
sheet = spreadsheet.SheetManager()
class StateMachine(StatesGroup):
    waiting_for_amount = State()


def access_required(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user = {'id': message.from_user.id, 'username': message.from_user.username}
        if user['id'] == int(config.user_id) and user['username'] == config.username:
            return await func(message, *args, **kwargs)
        else:
            await message.answer('Access to the bot is denied')
    return wrapper


@access_required
async def command_start(message: Message):
    await message.answer('''
Welcome to Telegram Finances Bot!
Type /add to add new expense.
''')


@access_required
async def command_help(message: Message):
    await message.answer('''                         
I'm here to help you account your cash expenditures.
Here's a list of the available commands:
    /start - Start the bot and get a welcome message
    /add - Add new expense information
    /remove - Remove an expense information
    /show - Show all expenses
    /help - Show this help message
''')


@access_required
async def command_add(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='rub', callback_data='currency_rub'),
            InlineKeyboardButton(text='tng', callback_data='currency_tng'),
            InlineKeyboardButton(text='usd', callback_data='currency_usd'),
        ]
    ])
    await message.answer('Choose the currency:', reply_markup=keyboard)


@access_required
async def command_remove(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='last expense', callback_data='remove_last'),
            InlineKeyboardButton(text='all expenses', callback_data='remove_all'),
        ]
    ])
    await message.answer('What do you want to remove?', reply_markup=keyboard)


@access_required
async def command_see(message: Message):
    table = db.format_table()
    await message.answer(f"<pre>{table}</pre>", parse_mode="HTML")


async def callback_controller(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('currency_'):
        currency = callback.data.split('_')[1]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='No category', callback_data='category_no category'),
            InlineKeyboardButton(text='Food', callback_data='category_food'),
        ], [
            InlineKeyboardButton(text='Transport', callback_data='category_transport'),
            InlineKeyboardButton(text='Utilities', callback_data='category_utilities'),
        ], [
            InlineKeyboardButton(text='Education', callback_data='category_education'),
            InlineKeyboardButton(text='Medical', callback_data='category_medical'),
        ], [
            InlineKeyboardButton(text='Shopping', callback_data='category_shopping'),
            InlineKeyboardButton(text='Tax', callback_data='category_tax'),
        ], [
            InlineKeyboardButton(text='Sub', callback_data='category_sub'),
            InlineKeyboardButton(text='Investments', callback_data='category_investments'),
        ]])
        await state.update_data(currency=currency)
        await callback.message.answer('Please choose the category:', reply_markup=keyboard)
    if callback.data.startswith('category_'):
        category = callback.data.split('_')[1]
        await state.update_data(category=category)
        await callback.message.answer('Please enter the expense in this form: {amount} {description}')
        await state.set_state(StateMachine.waiting_for_amount)
    if callback.data.startswith('remove_'):
        command = callback.data.split('_')[1]
        db.remove_expense(command)
        sheet.remove_from_sheet(command)
        await callback.message.answer('Information has been removed')


async def entry_amount(message: Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        user_input = message.text.split(maxsplit=1)
        expense = {
            'time': datetime.now().isoformat(),
            'amount': user_input[0],
            'currency': user_data.get('currency'),
            'category': user_data.get('category'),
            'description': ' '.join(user_input[1:])
        }
        db.add_expense(expense)
        sheet.insert_into_sheet(expense)
        await message.answer('Done! Use /add to enter new expense')
        await state.clear()
    except ValueError:
        await message.answer('Invalid format. Please try again: {amount} {description}')


async def main():
    bot = Bot(config.bot_token)
    dp = Dispatcher()

    dp.message.register(command_start, CommandStart())
    dp.message.register(command_help, Command('help'))
    dp.message.register(command_add, Command('add'))
    dp.message.register(command_remove, Command('remove'))
    dp.message.register(command_see, Command('see'))
    dp.callback_query.register(callback_controller)
    dp.message.register(entry_amount, StateFilter(StateMachine.waiting_for_amount))
    
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('bot disabled')
