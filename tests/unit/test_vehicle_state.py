from pyzonal.physics.vehicle_state import VehicleState, Gear
import pytest

@pytest.fixture
def state() -> VehicleState:
    return VehicleState()

def test_default_state_is_stationary_and_full_battery(state: VehicleState) -> None:
    assert state.speed_kmh == 0.0
    assert state.accel_mps2 == 0.0
    assert state.position_m == 0.0
    assert state.soc_pct == 100.0
    assert state.time_ms == 0.0

def test_default_inputs_are_zero(state: VehicleState) -> None:
    assert state.accelerator_pct == 0.0
    assert state.brake_pct == 0.0

def test_default_gear_is_park(state: VehicleState) -> None:
    assert state.gear is Gear.PARK

def test_state_is_mutable(state: VehicleState) -> None:
    state.speed_kmh = 50.0
    state.accelerator_pct = 0.5
    state.gear = Gear.DRIVE
    assert state.speed_kmh == 50.0
    assert state.accelerator_pct == 0.5
    assert state.gear is Gear.DRIVE

def test_reset_restores_defaults(state: VehicleState) -> None:
    state.speed_kmh = 80.0
    state.soc_pct = 30.0
    state.position_m = 1234.0
    state.time_ms = 9999.0
    state.gear = Gear.DRIVE

    assert state.speed_kmh == 80.0
    assert state.soc_pct == 30.0
    assert state.position_m == 1234.0
    assert state.time_ms == 9999.0
    assert state.gear is Gear.DRIVE

    state.reset()

    assert state.speed_kmh == 0.0
    assert state.soc_pct == 100.0
    assert state.position_m == 0.0
    assert state.time_ms == 0.0
    assert state.gear is Gear.PARK    

def test_two_default_instances_are_equal() -> None:
    assert VehicleState() == VehicleState()

def test_gear_enum_values_are_prnd() -> None:
    assert Gear.PARK.value == "P"
    assert Gear.REVERSE.value == "R"
    assert Gear.NEUTRAL.value == "N"
    assert Gear.DRIVE.value == "D"