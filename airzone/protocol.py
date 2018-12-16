from airzone.utils import *
import logging
from enum import Enum


class OnOff(Enum):
    OFF = 0,
    ON = 1


class MachineOperationMode(Enum):
    STOP = 0,
    COLD = 1,
    HOT = 2,
    AIR = 3,
    HOTPLUS = 258


class ZoneMode(Enum):
    STOP = 0,
    COLD = 1,
    HOT_AIR = 2,
    AIR = 3,
    FLOOT_HOT = 4,
    HOTPLUS = 5


class FancoilSpeed(Enum):
    AUTOMATIC = 0
    SPEED_1 = 1
    SPEED_2 = 2
    SPEED_3 = 3


class ProtectionTime(Enum):
    TEN_SEC = 0
    FOUR_MIN = 1


class VentilationMode(Enum):
    CONTINOUS = 0
    AUTOMATIC = 1


class LastGridCloseMode(Enum):
    TIMER = 0
    NO_TIMER = 1


class GridMode(Enum):
    All_NONE = 0,
    PROPORTIONAL = 1


class GridAngle(Enum):
    NINETY = 0,
    FIFTY = 1,
    FOURTY_FIVE = 2,
    FOURTY = 3


class ProbeType(Enum):
    NO_PROBE = 0,
    REMOTE = 1,
    FLOOR = 2


class RelayConfig(Enum):
    OFF = 0,
    USUALLY_OPEN = 1,
    USUALLY_CLOSE = 2


class LocalFancoilType(Enum):
    GRID = 0,
    FANCOIL = 1,
    
def state_value(state, address, init = 0, end = 15):
    return shifting(pad_right_list(bitfield(state[address]),16,0)[init:end+1])

def bit_value(state, address, bit):
    return shifting(pad_right_list(bitfield(state[address]),16,0)[bit])

def date_as_number(date):
    l = bitfield(date.weekday() + 1)
    l = pad_left_list(l, 3, 0)
    h = bitfield(date.hour)
    h = pad_left_list(h, 5, 0)
    m = bitfield(date.minute)
    m = pad_left_list(m, 6, 0)
    value = shifting(m + h + l)
    return value 