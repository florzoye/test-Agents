import asyncio
from data.init_configs import get_config
config = get_config()
telegram_event_queue: asyncio.Queue = asyncio.Queue(maxsize=config.BASE_CONFIG.MAX_CONCURRENT_EXECUTE)