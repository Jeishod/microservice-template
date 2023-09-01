from abc import abstractmethod
from typing import (
    Callable,
    Optional,
    Protocol,
)

from pydantic import BaseModel


class Broker(Protocol):
    """Queue listener and processing messages"""

    @abstractmethod
    async def start(self) -> None:
        """Start listening processing"""

    @abstractmethod
    async def stop(self) -> None:
        """Close connection and correct finish"""

    @abstractmethod
    async def produce(self, topic: str, message: BaseModel, key: str | None = None) -> None:
        """Produce message into broker"""

    # fmt: off
    @classmethod
    @abstractmethod
    def listen(
        cls,
        topic: str,
        key: Optional[str] = None,
        messages_count: int = 1,
        interval_period_sec: float = 1.0,
    ) -> Callable:
        """Function decorator to push prepared objects from broker"""
