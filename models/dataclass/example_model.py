from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)


@dataclass
class ExampleModel:
    """Example model structure"""

    attribute: str
    example_non_initiated_list: list[dict]
    example_initiated_list: list[bytes] = field(default_factory=list)

    @staticmethod
    def example_static_method(arg: type) -> ExampleModel | None:
        """
        An example of a static method that returns an instance of its class
        :param arg(type): meaningful description of the argument
        """
        return None

    def example_method(self) -> int:
        """Method description example"""
        return 1
