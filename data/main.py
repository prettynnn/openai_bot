import asyncio
import logging
import aiosqlite

# IMPORTANT : To record your chat history,
# you need to create a file called example data.db (or whatever name you like) 

from tokens import api_key, open_key
from openai import OpenAI
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from memoru import database, create_table, require_message_data, save_message
logging.basicConfig(level=logging.INFO, format="%(message)s")

# register the important data
log = logging.info

dp = Dispatcher()
bot = Bot(token=api_key)
model = 'gpt-5-mini-2025-08-07' # here you can select any model llm
model_pictures = 'gpt-image-1-mini'
client = OpenAI(api_key=open_key)

class setState(StatesGroup):
    image_handler = State()
        
# started bot command
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer('Hey! My name is Sophia! You ready speaking for me?'
                         'If you have speaking for me, send - /create_chat!')
    
# create chat command with history (chats)
@dp.message(Command("create_chat"))
async def create_handler(message: types.Message):
    connect = await database()
    user_id = message.from_user.id
    
    try:
        require = await require_message_data(connect, user_id)
        if require is None:
            await message.reply("Successfully chat created!")
            await save_message(connect, user_id, 'prompt', 'response')
            return
        else:
            await message.reply("The chat has already been created, continue!!")
    except aiosqlite.Error as e:
        log(f'Error added message to database! - {e}')

# here we speaking to bot, and he responds to any of our commands
@dp.message()
async def openai_handler(message: types.Message):
    connect = await database()
    user_id = message.from_user.id
    
    try:
        require = await require_message_data(connect, user_id)
        if require is None:
            await message.reply('You are should create chat: /create_chat')
            return
        
        user_message = message.text
        prompt = user_message
        text = client.responses.create(model=model,
                                        input=prompt,
                                        stream=False)
        response = text.output_text
        if len(response) > 4096:
            for i in range(0, len(response), 4096):
                await message.answer(response[i:i+4096])
        else:
            await message.reply(response)
            await save_message(connect, 
                               user_id, 
                               'prompt', 
                               'response')
    except aiosqlite.Error as e:
        log(f'Error - {e}')

# bot listening to all requests
async def main():
    connect = await database()
    create = await create_table(connect)
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt as x:
        log(f'This code is completed! - {x}')
    finally:
        connect.close()

if __name__ == "__main__":
    asyncio.run(main())
