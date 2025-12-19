from fastapi import FastAPI
from src.app.routers import telegram

app = FastAPI(title="Telegram Webhook")

app.include_router(telegram.router)

