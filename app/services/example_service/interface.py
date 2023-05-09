from abc import abstractmethod
from typing import Protocol

from app.models import ExampleModel


class ExampleInterface(Protocol):
    """Example Model Interface"""

    @abstractmethod
    async def example_method(self, model_data: ExampleModel) -> ExampleModel:
        """Some example method ot interaction with model"""

