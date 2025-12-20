import aiosqlite

async def database():
    connect = await aiosqlite.connect('data.db')
    return connect
    
async def create_table(connect):
    cursor = await connect.cursor()
    await cursor.execute('CREATE TABLE IF NOT EXISTS DATA (user TEXT, prompt TEXT, response TEXT)')
    await connect.commit()
    await cursor.close()
    
# save all messages to database
async def save_message(connect, user_id, prompt, response):
    cursor = await connect.cursor()
    await cursor.execute('INSERT INTO DATA (user, prompt, response) VALUES (?, ?, ?)', (user_id,
                                                                                        prompt, 
                                                                                        response))
    await cursor.close()
    return await connect.commit()

# function
async def require_message_data(connect, user_id):
    cursor = await connect.cursor()
    await cursor.execute('SELECT * FROM DATA WHERE user = ?', (user_id,))
    user_id = await cursor.fetchone()
    await cursor.close()
    return user_id
