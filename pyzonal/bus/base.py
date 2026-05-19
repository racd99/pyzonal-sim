"""BUS interface"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

# Frame type is intentionally Any here - each bus subtype defines it
Callback = Callable[[Any], None] # Callable[[types_of_arguments], return_type]

class Bus(ABC):
    name: str

    @abstractmethod
    def send(self, frame: Any) -> None:
        """Publish a frame to all subscribers of its message ID"""

    @abstractmethod
    def subscribe(self, msg_id: int, callback: Callback) -> None:
        """Register callback to receive frames with the given message ID"""

    @abstractmethod
    def tick(self, now_ms: float) -> None:
        """Advance the bus by one simulation step.
        E.g. we can fire periodic messagess with cycle time."""
