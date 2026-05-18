from dataclasses import dataclass
from enum import Enum

class Gear(Enum):
    PARK = "P"
    REVERSE = "R"
    NEUTRAL = "N"
    DRIVE = "D"

@dataclass
class VehicleState:
    # Motion
    speed_kmh: float = 0.0
    accel_mps2: float = 0.0
    position_m: float = 0.0

    # Driver inputs (0.0 to 1.0)
    accelerator_pct: float = 0.0
    brake_pct: float = 0.0

    # Gear
    gear: Gear = Gear.PARK

    # Powertrain
    motor_torque_nm: float = 0.0

    # High voltage battery
    soc_pct: float = 100.0 # State of charge
    pack_voltage_v: float = 400.0
    pack_current_v: float = 0.0 # postitive = discharge, negative = regen

    # Time since boot
    time_ms: float = 0.0

    def reset(self) -> None:
        """Reset to defaults"""
        defaults = VehicleState()
        for f in self.__dataclass_fields__:
            setattr(self, f, getattr(defaults,f))