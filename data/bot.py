import asyncio
import logging
import aiosqlite

# IMPORTANT : To record your chat history,
# you need to create a file called example data.db (or whatever name you like) 

from tokens import api_key, openai_api_key
from openai import OpenAI
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
logging.basicConfig(level=logging.INFO, format="%(message)s")

# register the important data
log = logging.info

dp = Dispatcher()
bot = Bot(token=api_key)
model = 'model' # here you can select any model llm
client = OpenAI(api_key=openai_api_key)

class setState(StatesGroup):
    image_handler = State()
    
class Data():
    def __init__(self, connect='', cursor=''):
        self.connect = connect
        self.cursor = cursor
        
    async def db(self):
        self.connect = await aiosqlite.connect('data.db')
        self.cursor = await self.connect.cursor()
        
    async def create_table(self):
        await self.db()
        await self.cursor.execute('CREATE TABLE IF NOT EXISTS DATA (user TEXT, prompt TEXT, response TEXT)')
        await self.connect.commit()
        
    # save all messages to database
    async def save_message(self, user_id, prompt, response):
        await self.cursor.execute('INSERT INTO DATA (user, prompt, response) VALUES (?, ?, ?)', (user_id,
                                                                                                 prompt, 
                                                                                                 response))
        return await self.connect.commit()

    # function
    async def require_message_data(self, user_id):
        await self.db()
        await self.cursor.execute('SELECT * FROM DATA WHERE user = ?', (user_id,))
        return await self.cursor.fetchone()
        
# started bot command
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer('Hey! My name is Sophia! You ready speaking for me?'
                         'If you have speaking for me, send - /create_chat!')
    
# create chat command with history (chats)
@dp.message(Command("create_chat"))
async def create_handler(message: types.Message):
        user_id = message.from_user.id
        
        try:
            require = await dat.require_message_data(user_id)
            if require is None:
                await dat.cursor.execute('INSERT OR IGNORE INTO DATA (user, prompt, response) VALUES (?, ?, ?)', (user_id, 
                                                                                                                  'prompt', 
                                                                                                                  'response'))
                await message.reply("Successfully chat created!")
                await dat.save_message(user_id, 'prompt', 'response')
                return
            else:
                await message.reply("The chat has already been created, continue!!")
        except aiosqlite.Error as e:
            log(f'Error added message to database! - {e}')

# here we speaking to bot, and he responds to any of our commands
@dp.message()
async def openai_handler(message: types.Message):
        user_id = message.from_user.id
        require = await dat.require_message_data(user_id)
        
        try:
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
                await dat.save_message(user_id, 
                                       'prompt', 
                                       'response')
        except aiosqlite.Error as e:
            log(f'Error - {e}')

# bot listening to all requests
async def main():
    try:
        await dat.create_table()
        await dp.start_polling(bot)
    except KeyboardInterrupt as x:
        log(f'This code is completed! - {x}')
    finally:
        connect.close()
    
dat = Data()
if __name__ == "__main__":
    asyncio.run(main())
