import logging
import os
import re
import shutil
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
import requests

from aiogram.utils.executor import start_webhook
from aiogram import types
from config import bot, dp, WEBHOOK_PATH, WEBHOOK_URL, WEBAPP_PORT, WEBAPP_HOST, BOT_URL, API_HOST, API_KEY, app
from db import database
from progress_bar import progress


async def on_startup(dispatcher):
    await database.connect()
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await database.disconnect()
    await bot.delete_webhook()


async def save(user_id, text, first_name):
    await database.execute(f"INSERT INTO messages(telegram_id, text, username) "
                           f"VALUES (:telegram_id, :text, :username)",
                           values={'telegram_id': user_id, 'text': text, 'username': first_name})


async def read():
    results = await database.fetch_all('SELECT text, username '
                                       'FROM messages;')
    return [next(result.values()) for result in results]


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.reply(text=f"Hi, I am **TikTok Downloader Bot**. \nI can download TikTok video without Watermark.\n"
                             f"Just send me link on TikTok Video\n"
                             f"__**Developer :**__ __@otakukz17__\n"
                             "__**Language :**__ __Python__\n"
                             "__**Framework :**__ __Aiogram",
                        parse_mode='Markdown')


@app.on_message(
    (filters.regex("http://") | filters.regex("https://")) & (filters.regex('tiktok') | filters.regex('douyin')))
def tiktok_dl(client, message):
    a = app.send_message(chat_id=message.chat.id,
                         text='__Downloading File to the Server__')
    link = re.findall(r'\bhttps?://.*[(tiktok|douyin)]\S+', message.text)[0]
    link = link.split("?")[0]

    url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/vid/index"

    querystring = {"url": link}

    headers = {
        "X-RapidAPI-Host": {API_HOST},
        "X-RapidAPI-Key": {API_KEY}
    }

    response = requests.get(url, headers=headers, params=querystring).json()['data']['play']
    directory = str(round(time.time()))
    filename = str(int(time.time())) + '.mp4'
    size = int(requests.head(response).headers['Content-length'])
    total_size = "{:.2f}".format(int(size) / 1048576)
    try:
        os.mkdir(directory)
    except:
        pass
    with requests.get(response, timeout=(50, 10000), stream=True) as r:
        r.raise_for_status()
        with open(f'./{directory}/{filename}', 'wb') as f:
            chunk_size = 1048576
            dl = 0
            show = 1
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                dl = dl + chunk_size
                percent = round(dl * 100 / size)
                if percent > 100:
                    percent = 100
                if show == 1:
                    try:
                        a.edit(f'__**URL :**__ __{message.text}__\n'
                               f'__**Total Size :**__ __{total_size} MB__\n'
                               f'__**Download :**__ __{percent}%__\n')
                    except:
                        pass
                    if percent == 100:
                        show = 0
        a.edit(f'__Downloaded to the server!\n'
               f'Uploading to Telegram Now __')
        start = time.time()
        title = filename
        app.send_document(chat_id=message.chat.id,
                          document=f"./{directory}/{filename}",
                          caption=f"**File: ** __{filename}__\n"
                                  f"**Size :** __{total_size} MB__ \n\n"
                                  f"__Uploaded by @{BOT_URL}__",
                          file_name=f"{directory}",
                          progress=progress,
                          progress_args=(a, start, title))
        a.delete()
        try:
            shutil.rmtree(directory)
        except:
            pass

# @dp.message_handler(regexp='tiktok')
# async def tiktok_dl(message: types.Message):
#     a = await message.answer(text='__Downloading File to the Server__')
#     link = await re.findall(r'\bhttps?://.*[(tiktok|douyin)]\S+', message.text)[0]
#     link = await link.split("?")[0]
#
    # url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/vid/index"
    #
    # querystring = {"url": link}
    #
    # headers = {
    #     "X-RapidAPI-Host": {API_HOST},
    #     "X-RapidAPI-Key": {API_KEY}
    # }
#
#     response = await requests.request("GET", url, headers=headers, params=querystring)
#     directory = str(round(time.time()))
#     filename = str(int(time.time())) + '.mp4'
#     size = int(requests.head(response).headers['Content-length'])
#     total_size = "{:.2f}".format(int(size) / 1048576)
#     try:
#         os.mkdir(directory)
#     except:
#         pass
#     with requests.get(response, timeout=(50, 10000), stream=True) as r:
#         r.raise_for_status()
#         with open(f'./{directory}/{filename}', 'wb') as f:
#             chunk_size = 1048576
#             dl = 0
#             show = 1
#             for chunk in r.iter_content(chunk_size=chunk_size):
#                 f.write(chunk)
#                 dl = dl + chunk_size
#                 percent = round(dl * 100 / size)
#                 if percent > 100:
#                     percent = 100
#                 if show == 1:
#                     try:
#                         await a.edit_text(f'__**URL :**__ __{message.text}__\n'
#                                           f'__**Total Size :**__ __{total_size} MB__\n'
#                                           f'__**Download :**__ __{percent}%__\n')
#                     except:
#                         pass
#                     if percent == 100:
#                         show = 0
#         await a.edit_text(f'__Downloaded to the server!\n'
#                           f'Uploading to Telegram Now __')
#         start = time.time()
#         title = filename
#         await message.reply_document(document=f"./{directory}/{filename}",
#                                      caption=f"**File: ** __{filename}__\n"
#                                              f"**Size :** __{total_size} MB__ \n\n"
#                                              f"__Uploaded by @{BOT_URL}__",
#                                      file_name=f"{directory}",
#                                      progress=progress,
#                                      progress_args=(a, start, title))
#         await a.delete()
#         try:
#             shutil.rmtree(directory)
#         except:
#             pass


# @dp.message_handler()
# async def echo(message: types.Message):
#     await save(message.from_user.id, message.text, message.from_user.first_name)
#     messages = await read()
#     await message.answer(messages)


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
