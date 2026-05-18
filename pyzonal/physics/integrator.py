"""Physics step. Updates VehicleState by `dt` seconds.

This is a deliberately simple longitudinal model:
 - Driver pedal inputs map to motor torque and brake force
 - The gear selector gates direction and whether torque is delivered at all
 - Net force = drive force - brake force - rolling resistance - aero drag
 - Newton's 2nd law: a = F / m
 - Speed and position integrate from acceleration

Sign convention: positive = forward, negative = reverse.

Gear behavioir:
 - PARK:    no drive torque, vehicle is stationary
 - REVERSE: accelerator produces negative torque, vehicle moves backward
 - NEUTRAL: no drive torque, vehicle can still rolling - coasting
 - DRIVE:   accelerator produces positive torque, vehicle moves forward.

 No tire dynamics, no lateral motion...
"""

from pyzonal.physics.vehicle_state import Gear, VehicleState

# Vehicle parameters
MASS_KG = 3000.0
WHEEL_RADIUS_M = 0.4
GEAR_RATIO = 9.0                 # motor:wheel
MAX_MOTOR_TORQUE_NM = 800.0
MAX_BRAKE_FORCE_N = 25_000.0
ROLLING_RESISTANCE_COEF = 0.012
AERO_DRAG_COEF = 0.5             # 0.5 * rho * Cd * A
GRAVITY_MPS2 = 9.81

# Reverse gear intentionally torque limited for safety realism.
REVERSE_TORQUE_LIMIT_FRAC = 0.5

KMH_PER_MPS = 3.6 # Conversion

def _drive_torque_for_gear(state: VehicleState) -> float: 
    """
    Compute commanded motor torque from accelerator and gear selector.

    Returns signed torque: positive = forward, negative = reverse, 0 = no drive
    """

    pedal = state.acceleratior_pct

    if state.gear is Gear.DRIVE:
        return pedal * MAX_MOTOR_TORQUE_NM
    if state.gear is Gear.REVERSE:
        return -pedal * MAX_MOTOR_TORQUE_NM * REVERSE_TORQUE_LIMIT_FRAC
    return 0.0 # PARK and NEUTRAL no torque

def step(state: VehicleState, dt_s: float) -> None:
    if dt_s <= 0:
        raise ValueError("dt_s must be positive")

    speed_mps = state.speed_kmh / KMH_PER_MPS

    # PARK
    if state.gear is Gear.PARK:
        state.speed_kmh = 0.0
        state.accel_mps2 = 0.0
        state.motor_torque_nm = 0.0
        state.time_ms += dt_s * 1000.0
        return

    # Drive force
    motor_torque = _drive_torque_for_gear(state)
    state.motor_torque_nm = motor_torque
    drive_force_n = motor_torque * GEAR_RATIO / WHEEL_RADIUS_M

    # Brake force
    brake_magnitude_n = state.brake_pct * MAX_BRAKE_FORCE_N
    if speed_mps > 0:
        brake_force_n = -brake_magnitude_n
    elif speed_mps < 0:
        brake_force_n = +brake_magnitude_n
    else:
        brake_force_n = 0.0

    # Resistive forces, zero when speed is 0
    if speed_mps > 0:
        rolling_n = -ROLLING_RESISTANCE_COEF * MASS_KG * GRAVITY_MPS2
        aero_n = -AERO_DRAG_COEF * speed_mps * speed_mps
    elif speed_mps < 0:
        rolling_n = +ROLLING_RESISTANCE_COEF * MASS_KG * GRAVITY_MPS2
        aero_n = +AERO_DRAG_COEF * speed_mps * speed_mps
    else:
        rolling_n = 0.0
        aero_n = 0.0

    # Net force (sum of all forces) and acceleration
    net_force_n = drive_force_n + brake_force_n + rolling_n + aero_n
    accel_mps2 = net_force_n / MASS_KG

    new_speed_mps = speed_mps + accel_mps2 * dt_s # Euler integration

    # Brake/resistance must not flip the sign of motion so we are clamping at zero,
    # we are checking motor_torque so we are sure that there is no accelerator pedal pressed
    if speed_mps > 0 and new_speed_mps < 0 and motor_torque <= 0:
        new_speed_mps = 0.0
        accel_mps2 = 0.0
    elif speed_mps < 0 and new_speed_mps > 0 and motor_torque >= 0:
        new_speed_mps = 0.0
        accel_mps2 = 0.0

    state.accel_mps2 = accel_mps2
    state.speed_kmh = new_speed_mps * KMH_PER_MPS
    state.position_m += new_speed_mps * dt_s
    state.time_ms += dt_s * 1000.0
