import os
import json
import requests
from fastapi import FastAPI, Request
from openpyxl import load_workbook

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

API = "https://platform-api.max.ru"

HEADERS = {
    "Authorization": BOT_TOKEN,
    "Content-Type": "application/json"
}

app = FastAPI()


def send_message(chat_id, text, keyboard=None):

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard:
        payload["inline_keyboard"] = keyboard

    requests.post(
        f"{API}/messages",
        headers=HEADERS,
        json=payload
    )


def load_clubs():

    wb = load_workbook("joined_clubs.xlsx")
    sheet = wb.active

    clubs = []

    for row in sheet.iter_rows(min_row=2, values_only=True):

        clubs.append({
            "direction": row[0],
            "name": row[1],
            "age": row[2],
            "address": row[3],
            "teacher": row[4],
            "link": row[5]
        })

    return clubs


def load_masterclasses():

    if not os.path.exists("masterclasses.json"):
        return []

    with open("masterclasses.json", "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/")
def health():
    return {"status": "bot running"}


@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    if "message" in data:

        message = data["message"]

        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "/start":

            keyboard = [
                [{"text": "🎨 Кружки", "callback_data": "clubs"}],
                [{"text": "🧩 Мастер-классы", "callback_data": "masters"}],
                [{"text": "✉ Поддержка", "callback_data": "support"}]
            ]

            send_message(
                chat_id,
                "Привет! Я бот центра Виктор 🎨\n\nВыберите раздел:",
                keyboard
            )

        else:

            send_message(
                chat_id,
                "Напишите /start чтобы открыть меню."
            )

    if "callback_query" in data:

        callback = data["callback_query"]

        chat_id = callback["message"]["chat"]["id"]
        data_cb = callback["data"]

        if data_cb == "clubs":

            clubs = load_clubs()

            text = "🎨 Наши кружки:\n\n"

            for c in clubs[:10]:
                text += f"{c['name']} ({c['age']})\n"

            send_message(chat_id, text)

        if data_cb == "masters":

            masters = load_masterclasses()

            if not masters:
                send_message(chat_id, "Пока нет мастер-классов.")
                return {"ok": True}

            text = "🧩 Мастер-классы:\n\n"

            for m in masters:
                text += f"{m['title']} — {m['date']}\n"

            send_message(chat_id, text)

        if data_cb == "support":

            send_message(
                chat_id,
                "Напишите сообщение, и администратор получит его."
            )

    return {"ok": True}
