from dataclasses import dataclass

@dataclass(frozen=True)
class CANFrame:
    """
    CAN:    dlc<=8, fd=False,
    CAN-FD: dlc up to 64, fd=True, brs optional
    
    Attributes:
    msg_id:         11-bit standard or 29-bit extended indentifier
    payload:        raw bytes, length = dlc
    dlc:            data length code
    fd:             True if CAN-FD
    brs:            bit rate switch for FD only
    timestamp_ms:   simulated time when frame emitted
    """

    msg_id: int
    payload: bytes
    dlc: int
    fd: bool = False
    brs: bool = False
    timestamp_ms: float = 0.0

    def __post_init__(self) -> None:
        if self.dlc != len(self.payload):
            raise ValueError(
                f"dlc={self.dlc} does not match payload length {len(self.payload)}"
            )
        if self.fd and self.dlc > 64:
            raise ValueError(f"CAN-FD payload max is 64 bytes, got {self.dlc}")
        if not self.fd and self.dlc > 8:
            raise ValueError(f"CAN payload max is 8 bytes, got {self.dlc}")
        if self.msg_id < 0 or self.msg_id > 0x1FFFFFFF:
            raise ValueError(f"Message ID is out of range: {self.msg_id:#x}") # #-will add 0x
        
        
