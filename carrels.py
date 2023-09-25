from pathlib import Path

import requests
import telegram.ext as t
from bs4 import BeautifulSoup
from telegram import Bot

url = 'https://seyhan.library.boun.edu.tr/search~S5?/.b1555861/.b1555861/1,1,1,B/holdings~1555861&FF=&1,0,'

# Chrome user agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',  # noqa: E501
}

telegram_api_token = ''  # TODO: can be fetched from configs

carrels_without_window = [
    '422 ',
    '421 ',
    '420 ',
    '419 ',
    '313 ',
    '314 ',
    '315 ',
    '316 ',
    '301 ',
    '302 ',
    '303 ',
    '304 ',
    '320 ',
    '328 ',
    '327 ',
    '326 ',
    '325 ',
]  # TODO: can be fetched from configs
color_carrels_without_window = "\U0001f7e8"
carrels_without_window_dict = {  # k for key, v for value.
    k: v for (k, v) in zip(carrels_without_window, [color_carrels_without_window] * len(carrels_without_window))
}

all_carrels: list[str] = []

bot = Bot(telegram_api_token)

updater = t.Updater(telegram_api_token, use_context=True)

disp = updater.dispatcher


def get_carrel_data():
    req = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(req.content, "lxml")
    all_carrels = soup.findAll('tr', attrs={'class': 'bibItemsEntry'})
    total_number_of_carrels = len(all_carrels)

    for i in range(0, total_number_of_carrels):
        carrel_no = all_carrels[i].find_all('td')[1].get_text()
        carrel_state = all_carrels[i].find_all('td')[2].get_text()
        carrel_no = carrel_no.replace('\xa0', '')
        carrel_state = carrel_state.replace('\xa0', '')
        # adding colors
        carrel_color = carrels_without_window_dict.get(carrel_no.replace('Carrel ', ''), "\U0001f7e6")
        # appending carrel info
        all_carrels.append(f"{carrel_color} {carrel_no} ---> {carrel_state}")


def get_all_data() -> str:
    get_carrel_data()
    result: list[str] = []
    for i in range(0, len(all_carrels)):
        if 'for vis' in all_carrels[i]:
            continue
        result.append(all_carrels[i])

    all_data: str = "\n".join(result)
    all_carrels.clear()
    return all_data


def get_empty_carrels() -> str:
    get_carrel_data()
    result: list[str] = []
    for i in range(0, len(all_carrels)):
        if 'for vis' in all_carrels[i] or 'DUE' in all_carrels[i]:
            continue
        result.append(all_carrels[i])

    if not result:
        all_carrels.clear()
        return 'Hepsi Dolu!'
    else:
        empty_data: str = "\n".join(result)
        all_carrels.clear()
        return empty_data


def show_carrel_location(update, context):
    chat_id = update.message.chat_id
    kat1 = Path("kat1.jpg")
    kat2 = Path("kat2.jpg")
    bot.send_photo(chat_id=chat_id, photo=kat1)
    bot.send_photo(chat_id=chat_id, photo=kat2)


def show_all_carrels(update, context):
    all_data = get_all_data()
    update.message.reply_text(all_data)


def show_empty(update, context):
    empty_carrels = get_empty_carrels()
    update.message.reply_text(empty_carrels)


def help(update, context):
    update.message.reply_text("Butun carrels icin /start\nSadece boslar icin /bos\nKat planlari icin /kat")


disp.add_handler(t.CommandHandler("hepsi", show_all_carrels))
disp.add_handler(t.CommandHandler("help", help))
disp.add_handler(t.CommandHandler('bos', show_empty))
disp.add_handler(t.CommandHandler('kat', show_carrel_location))


updater.start_polling()
updater.idle()
