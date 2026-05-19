"""Tests for CANBus and CANFrame."""

import pytest

from pyzonal.bus.can import CANBus
from pyzonal.bus.frames import CANFrame


# --- CANFrame validation ---


def test_canframe_dlc_must_match_payload_length():
    with pytest.raises(ValueError):
        CANFrame(msg_id=0x100, payload=b"\x01\x02", dlc=3)


def test_classic_can_payload_max_is_8_bytes():
    with pytest.raises(ValueError):
        CANFrame(msg_id=0x100, payload=b"\x00" * 9, dlc=9, fd=False)


def test_canfd_allows_up_to_64_bytes():
    frame = CANFrame(msg_id=0x100, payload=b"\x00" * 64, dlc=64, fd=True)
    assert frame.dlc == 64


def test_canfd_rejects_more_than_64_bytes():
    with pytest.raises(ValueError):
        CANFrame(msg_id=0x100, payload=b"\x00" * 65, dlc=65, fd=True)


def test_canframe_msg_id_out_of_range_rejected():
    with pytest.raises(ValueError):
        CANFrame(msg_id=-1, payload=b"", dlc=0)
    with pytest.raises(ValueError):
        CANFrame(msg_id=0x20000000, payload=b"", dlc=0)


def test_canframe_is_immutable():
    frame = CANFrame(msg_id=0x100, payload=b"\x01", dlc=1)
    with pytest.raises(Exception):
        frame.msg_id = 0x200  # type: ignore[misc]


# --- Pub/sub ---


def test_subscribe_then_send_invokes_callback():
    bus = CANBus()
    received: list[CANFrame] = []
    bus.subscribe(0x100, received.append)

    frame = CANFrame(msg_id=0x100, payload=b"\xAA", dlc=1)
    bus.send(frame)

    assert received == [frame]


def test_send_to_unsubscribed_id_is_a_noop():
    bus = CANBus()
    bus.send(CANFrame(msg_id=0x999, payload=b"", dlc=0))
    # No exception, no observable effect — that's the contract.


def test_multiple_subscribers_all_receive_frame():
    bus = CANBus()
    received_a: list[CANFrame] = []
    received_b: list[CANFrame] = []
    bus.subscribe(0x100, received_a.append)
    bus.subscribe(0x100, received_b.append)

    frame = CANFrame(msg_id=0x100, payload=b"\x01", dlc=1)
    bus.send(frame)

    assert received_a == [frame]
    assert received_b == [frame]


def test_subscriber_only_gets_its_msg_id():
    bus = CANBus()
    received: list[CANFrame] = []
    bus.subscribe(0x100, received.append)

    bus.send(CANFrame(msg_id=0x200, payload=b"\x01", dlc=1))
    assert received == []


# --- Periodic messages ---


def test_periodic_fires_immediately_on_first_tick():
    bus = CANBus()
    received: list[CANFrame] = []
    bus.subscribe(0x300, received.append)

    bus.register_periodic(
        msg_id=0x300,
        cycle_ms=100.0,
        frame_factory=lambda now: CANFrame(0x300, b"\x42", 1, timestamp_ms=now),
    )

    bus.tick(now_ms=0.0)
    assert len(received) == 1


def test_periodic_does_not_fire_again_before_cycle_elapsed():
    bus = CANBus()
    received: list[CANFrame] = []
    bus.subscribe(0x300, received.append)
    bus.register_periodic(
        0x300, 100.0, lambda now: CANFrame(0x300, b"\x42", 1, timestamp_ms=now)
    )

    bus.tick(0.0)
    bus.tick(50.0)
    assert len(received) == 1  # only the first tick fired


def test_periodic_fires_on_each_cycle():
    bus = CANBus()
    received: list[CANFrame] = []
    bus.subscribe(0x300, received.append)
    bus.register_periodic(
        0x300, 100.0, lambda now: CANFrame(0x300, b"\x42", 1, timestamp_ms=now)
    )

    for ms in (0.0, 100.0, 200.0, 300.0):
        bus.tick(ms)

    assert len(received) == 4


def test_register_periodic_rejects_zero_or_negative_cycle():
    bus = CANBus()
    with pytest.raises(ValueError):
        bus.register_periodic(0x300, 0.0, lambda now: CANFrame(0x300, b"", 0))
    with pytest.raises(ValueError):
        bus.register_periodic(0x300, -10.0, lambda now: CANFrame(0x300, b"", 0))