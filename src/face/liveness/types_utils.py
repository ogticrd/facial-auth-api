from enum import Enum
from pydantic import BaseModel

# Hand Types
class HandSign(BaseModel):
    THUMB: bool
    INDEX: bool
    MIDDLE: bool
    RING: bool
    PINKY: bool

class HandEnum(str, Enum):
    right = 'Right'
    left = 'Left'

class HandSignDetectionResult(BaseModel):
    result: bool
    hand: HandEnum

# Verify Liveness Types  
class LivenessResult(BaseModel):
    is_alive: bool
    alive_ratio: float
    total_blink: int
    blur_average: float
    lbp_average: float

class HandSignResultValues(BaseModel):
    frames: int
    hand: HandEnum
    one_hand: bool
