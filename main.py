import logging

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ieee_754 import from_ieee_to_float, from_float_to_ieee, from_hexadecimal_to_ieee


logging.basicConfig(level=logging.INFO)

TOKEN = ''
bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# dp.middleware.setup(LoggingMiddleware())


class Form(StatesGroup):
    ieee_length = State()
    call_state = State()
    number = State()


@dp.message_handler(commands=['start'])
async def start_function(message: types.Message):
    await message.answer(
        f'''
Hello {message.from_user.full_name}.
Here are some commands to help you!
 - /solve - Solve exercise.
 - /cancel - Clear solve memorization.
 - /info - Bot info.
 - /example - Example of solve text format.
        ''')


@dp.message_handler(commands=['info'])
async def start_function(message: types.Message):
    await message.answer(f"Hi {message.from_user.full_name}.\nThere are no info about this bot.")
    await message.answer_photo(
        photo='https://upload.wikimedia.org/wikipedia/commons/9/9e/Ginger_european_cat.jpg',
        caption='But here is a cat.')


@dp.message_handler(commands=['example'])
async def start_function(message: types.Message):
    await message.answer(f'''
Hi {message.from_user.full_name}.
Here are some examples of text format for <b>/solve</b> command.

<b>- For IEEE-754 to float:</b>
\t<code>0|10000000|00000000000000000000000</code>
<b>- For float to IEEE-754:</b>
\t<code>1.5</code>
<b>- For hexadecimal to IEEE-754:</b>
\t<code>0x3F800000</code>
    ''',
    parse_mode='HTML')


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer('Cancelled.')


@dp.message_handler(commands=['solve'])
async def start_function(message: types.Message):
    await Form.ieee_length.set()
    
    markup = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
            InlineKeyboardButton(text='16-bit (half)', callback_data='16'),
            InlineKeyboardButton(text='32-bit (float)', callback_data='32'),
            InlineKeyboardButton(text='64-bit (double)', callback_data='64'),
        )

    await bot.send_message(
        chat_id=message.from_user.id, 
        text=f"{message.from_user.full_name} please select ieee size!", 
        reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data in ['16', '32', '64'], state=Form.ieee_length)
async def process_callback_list(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['ieee_length'] = callback_query.data

    await Form.next()

    markup = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2).add(
            InlineKeyboardButton(text='Float to IEEE-754', callback_data='from_float_to_ieee'),
            InlineKeyboardButton(text='IEEE-754 to Float', callback_data='from_ieee_to_float'),
            InlineKeyboardButton(text='Hexadecimal to IEEE-754', callback_data='from_hexadecimal_to_ieee'),
        )

    await callback_query.message.edit_text(
        text=f"{callback_query.from_user.full_name} please select convertion type!", 
        reply_markup=markup)
        

@dp.callback_query_handler(lambda call: call.data in ['from_ieee_to_float', 'from_float_to_ieee', 'from_hexadecimal_to_ieee'], state=Form.call_state)
async def ieee_type(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['call_state'] = callback_query.data

    await Form.next()

    await callback_query.message.edit_text('Please input a number:')


@dp.message_handler(state=Form.number)
async def boh(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['number'] = message.text
        
            if data['call_state'] == 'from_float_to_ieee':
                ieee, sign, exponent, mantissa, hexadecimal = from_float_to_ieee(data['ieee_length'], data['number'])
                
                await message.reply(
                    f'Number: {data["number"]}\n\nIEEE-754: {ieee}\nHexadecimal: {hexadecimal}\n\nSign: {sign}\nExponent: {exponent}\nMantissa: {mantissa}')
                    
            elif data['call_state'] == 'from_ieee_to_float':
                ieee, num, hexadecimal = from_ieee_to_float(data['ieee_length'], data['number'])
                
                await message.reply(
                    f'Number: {num}\nIEEE-754: {ieee}\nHexadecimal: {hexadecimal}')
                    
            elif data['call_state'] == 'from_hexadecimal_to_ieee':
                ieee, num, hexadecimal = from_hexadecimal_to_ieee(data['ieee_length'], data['number'])
                
                await message.reply(
                    f'Number: {num}\nIEEE-754: {ieee}\nHexadecimal: {hexadecimal}')

    except:
        await bot.send_message(message.from_user.id, 'Somthing wrong, please retry!')

    await state.finish()
            

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)