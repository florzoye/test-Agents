import asyncio
from data.configs import base_config
telegram_event_queue: asyncio.Queue = asyncio.Queue(maxsize=base_config.MAX_CONCURRENT_EXECUTE)