import logging
import os
import re
import shutil
import time
import requests
from aiogram.utils.executor import start_webhook
from aiogram import types
from config import bot, dp, WEBHOOK_PATH, WEBHOOK_URL, WEBAPP_PORT, WEBAPP_HOST, BOT_URL, API_HOST, API_KEY
from db import database


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
    await save(message.from_user.id, message.text, message.from_user.first_name)
    await message.reply(text=f"Hi, I am **TikTok Downloader Bot** \nI can download TikTok video without Watermark\n"
                             f"Just send me link on TikTok Video\n"
                             f"__**Developer :**__ __@otakukz17__\n"
                             "__**Language :**__ __Python__\n"
                             "__**Framework :**__ __Aiogram__",
                        parse_mode='MarkdownV2')


@dp.message_handler(regexp='tiktok')
async def tiktok_dl(message: types.Message):
    await save(message.from_user.id, message.text, message.from_user.first_name)
    a = await message.answer(text='__Downloading File to the Server__')
    link = re.findall(r'\bhttps?://.*[(tiktok|douyin)]\S+', message.text)[0]
    link = link.split("?")[0]

    url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/vid/index"

    querystring = {"url": link}

    headers = {
        "X-RapidAPI-Host": f'{API_HOST}',
        "X-RapidAPI-Key": f'{API_KEY}'
    }

    response = requests.request("GET", url, headers=headers, params=querystring).json()['video'][0]
    print(response)
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
                        await a.edit_text(text='__**URL :**__ __{message.text}__\n'
                                               f'__**Total Size :**__ __{total_size} MB__\n'
                                               f'__**Download :**__ __{percent}%__\n',
                                          parse_mode='Markdown')
                    except:
                        pass
                    if percent == 100:
                        show = 0
        await a.edit_text(text=f'__Downloaded to the server__\n'
                               f'__Uploading to Telegram Now__',
                          parse_mode='Markdown')
        await bot.send_document(message.chat.id, open(f'./{directory}/{filename}', 'rb'),
                                caption=f"**File: ** __{filename}__\n"
                                        f"**Size :** __{total_size} MB__ \n\n"
                                        f"__Uploaded by {BOT_URL}__",
                                parse_mode='Markdown')
        await a.delete()
        try:
            shutil.rmtree(directory)
        except:
            pass


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
