import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

API_URL = "https://platform-api.max.ru"
HEADERS = {
    "Authorization": BOT_TOKEN,
    "Content-Type": "application/json"
}