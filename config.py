import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DATABASE = os.getenv("DATABASE")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_STATIC_API_KEY = os.getenv("YANDEX_STATIC_API_KEY")
ORDER_PAGES = 10
