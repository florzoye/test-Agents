from fastapi import APIRouter

router = APIRouter(tags=["Telegram"])


@router.post("/webhook")
async def telegram_webhook(payload: dict):
    return {"status": "ok"}