
from pyzonal.physics.integrator import step
from pyzonal.physics.vehicle_state import Gear, VehicleState

# PARK BEHAVIOUR

def test_park_blocks_acceleration_even_with_full_pedal():
    state = VehicleState()
    state.gear = Gear.PARK
    state.accelerator_pct = 1.0

    step(state, dt_s=0.1)

    assert state.speed_kmh == 0.0
    assert state.motor_torque_nm == 0.0

def test_park_holds_a_moving_vehicle_stationary_immediately():
    # Testing as edge case when car is somehow set set to PARK gear while moving
    state = VehicleState()
    state.speed_kmh = 50.0
    state.gear = Gear.PARK

    step (state, dt_s=0.1)

    assert state.speed_kmh == 0.0