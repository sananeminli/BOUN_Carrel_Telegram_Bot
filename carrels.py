import logging
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from telegram import ForceReply
from telegram import Update
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

url = 'https://seyhan.library.boun.edu.tr/search~S5?/.b1555861/.b1555861/1,1,1,B/holdings~1555861&FF=&1,0,'

# Chrome user agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',  # noqa: E501
}

telegram_api_token = ''  # TODO: can be fetched from configs

carrels_without_window = [
    '422',
    '421',
    '420',
    '419',
    '313',
    '314',
    '315',
    '316',
    '301',
    '302',
    '303',
    '304',
    '320',
    '328',
    '327',
    '326',
    '325',
]  # TODO: can be fetched from configs
color_carrels_without_window = "\U0001f7e8"
color_carrels_with_window = "\U0001f7e6"
carrels_without_window_dict = {  # k for key, v for value.
    k: v for (k, v) in zip(carrels_without_window, [color_carrels_without_window] * len(carrels_without_window))
}

all_carrels: list[str] = []


def get_carrel_data():
    global all_carrels
    all_carrels.clear()
    req = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(req.content, "lxml")
    all_bib_items = soup.findAll('tr', attrs={'class': 'bibItemsEntry'})
    total_number_of_carrels = len(all_bib_items)

    for i in range(0, total_number_of_carrels):
        carrel_no = all_bib_items[i].find_all('td')[1].get_text()
        carrel_state = all_bib_items[i].find_all('td')[2].get_text()
        carrel_no = carrel_no.replace('\xa0', '').strip()
        carrel_state = carrel_state.replace('\xa0', '')
        # adding colors
        carrel_color = carrels_without_window_dict.get(carrel_no.replace('Carrel ', ''), color_carrels_with_window)
        # appending carrel info
        all_carrels.append(f"{carrel_color} {carrel_no} ---> {carrel_state}")


def get_all_data() -> str:
    global all_carrels
    get_carrel_data()
    result: list[str] = list()
    for i in range(0, len(all_carrels)):
        if 'for vis' in all_carrels[i]:
            continue
        result.append(all_carrels[i])

    all_data: str = "\n".join(result)
    return all_data


def get_empty_carrels() -> str:
    global all_carrels
    get_carrel_data()
    result: list[str] = list()
    for i in range(0, len(all_carrels)):
        if 'for vis' in all_carrels[i] or 'DUE' in all_carrels[i]:
            continue
        result.append(all_carrels[i])

    if not result:
        return 'Hepsi Dolu!'
    else:
        empty_data: str = "\n".join(result)
        return empty_data


# Define a few command handlers. These usually take the two arguments update and context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Welcome {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def show_carrel_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kat1 = Path("kat1.jpg")
    kat2 = Path("kat2.jpg")
    await update.message.reply_photo(photo=kat1)
    await update.message.reply_photo(photo=kat2)


async def show_all_carrels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_data = get_all_data()
    if all_data:
        await update.message.reply_text(all_data)
    else:
        logger.warning("No carrel data found")


async def show_empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    empty_carrels = get_empty_carrels()
    if empty_carrels:
        await update.message.reply_text(empty_carrels)
    else:
        logger.warning("No empty carrel data found")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Butun carrels icin /start\nSadece boslar icin /bos\nKat planlari icin /kat")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_api_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("hepsi", show_all_carrels))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("bos", show_empty))
    application.add_handler(CommandHandler("kat", show_carrel_location))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":  # pragma: no cover
    main()
