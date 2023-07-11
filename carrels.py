import requests
import telegram.ext as t
from bs4 import BeautifulSoup
from telegram import Bot

url = 'https://seyhan.library.boun.edu.tr/search~S5?/.b1555861/.b1555861/1,1,1,B/holdings~1555861&FF=&1,0,'

# Chrome user agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',  # noqa: E501
}

telegram_api_token = ''

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
]

all_carrels = []

bot = Bot(telegram_api_token)

updater = t.Updater(telegram_api_token, use_context=True)

disp = updater.dispatcher


def get_carrel_data():
    req = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(req.content, "lxml")
    total_number_of_carrels = len(soup.findAll('tr', attrs={'class': 'bibItemsEntry'}))

    for i in range(0, total_number_of_carrels):
        carrel_no = soup.findAll('tr', attrs={'class': 'bibItemsEntry'})[i].find_all('td')[1].get_text()
        carrel_state = soup.findAll('tr', attrs={'class': 'bibItemsEntry'})[i].find_all('td')[2].get_text()
        carrel_no = carrel_no.replace('\xa0', '')
        carrel_state = carrel_state.replace('\xa0', '')
        # adding colors
        if carrel_no.replace('Carrel ', '') in carrels_without_window:
            carrel_no = "\U0001f7e8 " + carrel_no
        else:
            carrel_no = "\U0001f7e6 " + carrel_no
        all_carrels.append(str(carrel_no) + ' ---> ' + str(carrel_state))


def get_all_data():
    get_carrel_data()
    result = ''
    for i in range(0, len(all_carrels)):
        if 'for vis' in all_carrels[i]:
            continue
        result += '\n' + all_carrels[i]

    all_carrels.clear()
    return result


def get_empty_carrels():
    get_carrel_data()
    result = ''
    for i in range(0, len(all_carrels)):
        if 'for vis' in all_carrels[i] or 'DUE' in all_carrels[i]:
            continue
        result += '\n' + all_carrels[i]
    if result == '':
        all_carrels.clear()
        return ' Hepsi Dolu!'

    else:
        all_carrels.clear()
        return result


def show_carrel_location(update, context):
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=open(r"kat1.jpg", "rb"))  # TODO: where is kat1.jpg?
    bot.send_photo(chat_id=chat_id, photo=open(r"kat2.jpg", "rb"))  # TODO: where is kat2.jpg?


def show_all_carrels(update, context):
    update.message.reply_text(get_all_data())


def show_empty(update, context):
    update.message.reply_text(get_empty_carrels())


def help(update, context):
    update.message.reply_text("Butun carrels icin /start\nSadece boslar icin /bos\nKat planlari icin /kat")


disp.add_handler(t.CommandHandler("hepsi", show_all_carrels))
disp.add_handler(t.CommandHandler("help", help))
disp.add_handler(t.CommandHandler('bos', show_empty))
disp.add_handler(t.CommandHandler('kat', show_carrel_location))


updater.start_polling()
updater.idle()
