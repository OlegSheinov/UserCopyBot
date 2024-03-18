import logging
import os
import platform
import re

from dotenv import load_dotenv
from openpyxl import Workbook
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from telethon import TelegramClient, events
from telethon.tl.types import PeerChat, PeerUser

from models import Messages, Base

load_dotenv()

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger('pika').setLevel(logging.WARNING)
log = logging.getLogger()

client = TelegramClient(session=os.getenv("SESSION_NAME"), api_id=int(os.getenv('API_ID')),
                        api_hash=os.getenv('API_HASH'))
all_chats = []
my_chat = int(os.getenv('MY_CHANNEL'))
new_tg = os.getenv('NEW_TG')
regex_bid = r'\*\*Ставка\s*до(?:\s*\(.*?\))?:\*\*\s*([\d\s]+(?:\|\s*[A-Za-z]+)?|обсуждаемая)'
regex_tg = r'@\w*'
engine = create_engine("sqlite:///base.db", echo=False)

phone = os.getenv("PHONE")
password = os.getenv("PASS")


@client.on(events.NewMessage(chats=[PeerUser(user_id=654553893), PeerUser(user_id=715845455)], pattern='!excel'))
async def handler(event):
    with Session(engine) as session:
        result = select(Messages)
        wb = Workbook()
        ws = wb.active
        data = [["Channel id", "Channel name", "Message"]]
        for message in session.scalars(result):
            data.append([str(message.channel_id), message.channel_name, message.message])
        for row in data:
            ws.append(row)
        wb.save('message.xlsx')
        await client.send_file(event.chat_id, 'message.xlsx')


@client.on(events.NewMessage(chats=all_chats))
async def my_event_handler(event):
    log.info(f"Сообщение с канала {event.chat_id}. пересылаю в {my_chat}!")
    msg = event.text
    new_msg = msg
    matches = re.findall(regex_bid, msg)
    for match in matches:
        if "\n" in match:
            old_price = match.split(" ")[0]
        else:
            old_price = match.split("|")[0].replace(" ", "")
        if old_price.isdigit():
            new_msg = re.sub(regex_bid, '', msg)
    with Session(engine) as session:
        row = Messages(channel_id=event.chat_id, channel_name=event.chat.title, message=msg)
        session.add_all([row])
        session.commit()
    new_msg = re.sub(regex_tg, new_tg, new_msg)
    await client.send_message(my_chat, new_msg)


async def main():
    log.info("Получаю список каналов.")
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:
            all_chats.append(dialog.id)


if __name__ == "__main__":
    log.info("Запуск...")
    with client.start(phone=lambda: phone, password=lambda: password):
        Base.metadata.create_all(engine)
        client.session.save()
        client.loop.run_until_complete(main())
        log.info("Получен список каналов. Начинаю слушать")
        client.run_until_disconnected()
