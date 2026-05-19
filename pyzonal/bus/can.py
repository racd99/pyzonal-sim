"""CAN/CAN-FD bus implementation

Model description: Every subscriber to a given msg_id receives every frame published with that ID.
Cycle time tracking.
"""

from collections.abc import Callable
from pyzonal.bus.base import Bus, Callback
from pyzonal.bus.frames import CANFrame

FrameFactory = Callable[[float], CANFrame]

class CANBus(Bus):
    def __init__(self, name = "CAN") -> None:
        self.name = name
        self._subscribers: dict[int, list[Callback]] = {}
        self._periodics: dict[int, _Periodic] = {}

    def subscribe(self, msg_id: int, callback: Callback) -> None:
        self._subscribers.setdefault(msg_id, []).append(callback)

    def send(self, frame: CANFrame) -> None:
        for cb in self._subscribers.get(frame.msg_id, ()):
            cb(frame)

    def register_periodic(self, msg_id: int, cycle_ms: float, frame_factory: FrameFactory) -> None:
        if cycle_ms <= 0:
            raise ValueError(f"cycle_ms must be positive, got {cycle_ms}")
        self._periodics[msg_id] = _Periodic(
            cycle_ms=cycle_ms,
            frame_factory=frame_factory,
            last_fired_ms=None
        )

    def tick(self, now_ms: float) -> None:
        for periodic in self._periodics.values():
            if periodic.is_due(now_ms):
                frame = periodic.frame_factory(now_ms)
                self.send(frame)
                periodic.last_fired_ms = now_ms

class _Periodic:
        """Internal bookkeeping for a periodic message"""
        def __init__(self, cycle_ms: float, frame_factory: FrameFactory, last_fired_ms: float | None) -> None:
            self.cycle_ms = cycle_ms
            self.frame_factory = frame_factory
            self.last_fired_ms = last_fired_ms

        def is_due(self, now_ms: float) -> bool:
            if self.last_fired_ms is None:
                return True  # never fired — fire on first tick
            return now_ms - self.last_fired_ms >= self.cycle_ms
