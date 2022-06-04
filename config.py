import os
from aiogram.dispatcher import Dispatcher
from aiogram import Bot
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent


TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
BOT_URL = os.getenv('BOT_URL')
API_HOST = os.getenv('API_HOST')
API_KEY = os.getenv('API_KEY')

workers = 4
api = os.getenv('API_ID')
hash = os.getenv('API_HASH')

app = Client("BOT_Name", bot_token=TOKEN, api_id=api, api_hash=hash, workers=workers)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)
DB_URL = os.getenv('DATABASE_URL')
