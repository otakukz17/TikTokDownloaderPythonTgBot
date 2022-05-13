from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
import shutil
import requests
import json
import os
import re
from bs4 import BeautifulSoup as bs
import time
from datetime import timedelta
from progress_bar import progress, TimeFormatter, humanbytes

bot_token = 'BOT_TOKEN'
workers = 4
api = 'TELEGRAM_API'
hash = 'TELEGRAM_API_HASH'
channel = 'https://t.me/+WK-z97ej_B04NTdi'
BOT_URL = 'mylittlebtcusdbot'
app = Client("BOT_Name", bot_token=bot_token, api_id=api, api_hash=hash, workers=workers)


@app.on_message(filters.command('start'))
def start(client, message):
    kb = [[InlineKeyboardButton('Repo', url='https://github.com/otakukz17/TikTokDownloaderTgBot')]]
    reply_markup = InlineKeyboardMarkup(kb)
    app.send_message(chat_id=message.from_user.id,
                     text=f"Hi, I am **TikTok Downloader Bot**. \nI can download TikTok video without Watermark.\n"
                          f"Just send me link on TikTok Video\n"
                          f"__**Developer :**__ __@otakukz17__\n"
                          "__**Language :**__ __Python__\n"
                          "__**Framework :**__ __🔥 Pyrogram__",
                     reply_markup=reply_markup)


@app.on_message(
    (filters.regex("http://") | filters.regex("https://")) & (filters.regex('tiktok') | filters.regex('douyin')))
def tiktok_dl(client, message):
    a = app.send_message(chat_id=message.chat.id,
                         text='__Downloading File to the Server__')
    link = re.findall(r'\bhttps?://.*[(tiktok|douyin)]\S+', message.text)[0]
    link = link.split("?")[0]

    url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"

    querystring = {"url": link, "hd": "0"}

    headers = {
        "X-RapidAPI-Host": "tiktok-video-no-watermark2.p.rapidapi.com",
        "X-RapidAPI-Key": "ad6fd2a8efmsh0bce23c5408b459p1c8098jsn7300850ffe5f"
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


app.run()
