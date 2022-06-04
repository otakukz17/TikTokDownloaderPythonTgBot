import logging
from aiogram.utils.executor import start_webhook
from aiogram import types
from config import bot, dp, WEBHOOK_PATH, WEBHOOK_URL, WEBAPP_PORT, WEBAPP_HOST
from db import database


async def on_startup(dispatcher):
    await database.connect()
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await database.disconnect()
    await bot.delete_webhook()


async def save(user_id, text, first_name):
    await database.execute(f"INSERT INTO messages(telegram_id, text, username) "
                           f"VALUES (:telegram_id, :text, :username)", values={'telegram_id': user_id, 'text': text, 'username': first_name})


async def read():
    results = await database.fetch_all('SELECT text, username '
                                       'FROM messages ')
    return [next(result.values()) for result in results]


@dp.message_handler()
async def echo(message: types.Message):
    await save(message.from_user.id, message.text, message.from_user.first_name)
    messages = await read()
    await message.answer(messages)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
