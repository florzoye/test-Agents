from abc import ABC, abstractmethod

class MessageSender(ABC):
    @abstractmethod
    async def send_message(
        self, 
        content: str,
        recipient_id: str | None = None, 
        username: str | None = None
    ) -> bool:
        """Отправить сообщение получателю на любой поддерживаемой платформе"""
        ...
    
    @abstractmethod
    async def check_delivery_status(
        self, 
        message_id: str
    ) -> str:
        """Проверить статус доставки сообщения"""
        ...