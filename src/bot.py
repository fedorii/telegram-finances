from aiogram import Bot, Dispatcher
from aiogram.types import (Message, InlineKeyboardMarkup,
    InlineKeyboardButton, CallbackQuery)
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import asyncio
from datetime import datetime

import config
import database


db = database.Database()


class StateMachine(StatesGroup):
    waiting_for_amount = State()


async def check_user(message: Message):
    user = {
        'id': message.from_user.id,
        'username': message.from_user.username,
        'language': message.from_user.language_code
    }
    if not db.check_user(user['id']):
        db.add_user(
            telegram_id=user['id'],
            username=user['username'],
            language=user['language']
        )


async def command_start(message: Message):
    await message.answer('''
Welcome to Telegram Finances Bot!
Type /add to add new expense.
''')


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
    

async def command_add(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='rub', callback_data='currency_rub'),
            InlineKeyboardButton(text='tng', callback_data='currency_tng'),
            InlineKeyboardButton(text='usd', callback_data='currency_usd'),
        ]
    ])
    await message.answer('Choose the currency:', reply_markup=keyboard)


async def command_remove(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='last expense', callback_data='rm_last'),
            InlineKeyboardButton(text='all expenses', callback_data='rm_all'),
        ]
    ])
    await message.answer('What do you want to remove?', reply_markup=keyboard)


async def command_see():
    pass


async def callback_controller(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith('currency'):
        currency = callback.data.split('_')[1]
        await state.update_data(currency=currency)
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
        await callback.message.answer('Please choose the category:', reply_markup=keyboard)
    if callback.data.startswith('category'):
        category = callback.data.split('_')[1]
        await state.update_data(category=category)
        await callback.message.answer('Please enter the expense in this form: {amount} {description}')
        await state.set_state(StateMachine.waiting_for_amount)
    if callback.data.startswith('remove'):
        command = callback.data.split('_')[1]
        db.remove_expense(command)
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
    dp.message.register(callback_controller, dp.callback_query())
    dp.message.register(entry_amount, StateFilter(StateMachine.waiting_for_amount))

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())