import logging
import os
import re

from dotenv import load_dotenv
from telethon import TelegramClient, events

from api.post_vacancy import send_vacancy

load_dotenv()

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger('pika').setLevel(logging.WARNING)
log = logging.getLogger()

client = TelegramClient(session=os.getenv("SESSION_NAME"), api_id=int(os.getenv('API_ID')),
                        api_hash=os.getenv('API_HASH'))
all_chats = []
my_chat = int(os.getenv('MY_CHANNEL'))
new_tg = os.getenv('NEW_TG')
regex_bid = ["рейт", "ставк", "цена", "р/ч", "оплат"]
regex_tg = r'@\w*|\[[^\]]+\]\([^)]+\)'

phone = os.getenv("PHONE")
password = os.getenv("PASS")


@client.on(events.NewMessage(chats=all_chats))
async def my_event_handler(event):
    msg = event.text
    regex_pattern = re.compile('|'.join(regex_bid), re.IGNORECASE)
    if regex_pattern.search(msg):
        log.info(f"Сообщение с канала {event.chat_id} пересылаю в {my_chat}!")
        response = await send_vacancy(msg, str(event.chat_id))
        if response:
            pass


async def main():
    log.info("Получаю список каналов.")
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:
            all_chats.append(dialog.id)


if __name__ == "__main__":
    log.info("Запуск...")
    with client.start(phone=lambda: phone, password=lambda: password):
        client.session.save()
        client.loop.run_until_complete(main())
        log.info("Получен список каналов. Начинаю слушать")
        client.run_until_disconnected()
