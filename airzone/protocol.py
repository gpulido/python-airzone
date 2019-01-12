from airzone.utils import *
import logging
from enum import Enum
from array import array

class MachineOperationMode(Enum):
    STOP = 0
    COLD = 1
    HOT = 2
    AIR = 3
    HOT_AIR = 4
    HOTPLUS = 258

class ZoneMode(Enum):
    MANUAL = 0
    MANUAL_SLEEP = 1
    AUTOMATIC = 2
    AUTOMATIC_SLEEP = 3

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
    All_NONE = 0
    PROPORTIONAL = 1


class GridAngle(Enum):
    NINETY = 0
    FIFTY = 1
    FOURTY_FIVE = 2
    FOURTY = 3


class ProbeType(Enum):
    NO_PROBE = 0
    REMOTE = 1
    FLOOR = 2


class RelayConfig(Enum):
    OFF = 0
    USUALLY_OPEN = 1
    USUALLY_CLOSE = 2


class LocalFancoilType(Enum):
    GRID = 0
    FANCOIL = 1

def state_value(state, address, init = 0, end = 15):
    '''
    init and end are included on the desired slice
    '''
    binary = format(state[address], '016b')
    r_init = len(binary)-1-init
    r_end = len(binary)-1-end 
    kBitSubStr = binary[r_end : r_init+1]
    return int(kBitSubStr, 2)

def bit_value(state, address, bit):
    #return state_value(state, address, bit, bit)
    temp = format(state[address], '016b')
    return int(temp[len(temp)-1-bit])

def change_range_bit_value(state, address, init_bit, num_bit, value):
    if num_bit <= 0:
        return state[address]
    temp2 = list(format(state[address], '016b'))
    idx = len(temp2)-init_bit-num_bit
    idx2 = len(temp2)-init_bit
    temp = list(format(value, '0'+str(num_bit)+ 'b'))
    temp2[idx:idx2] = temp
    return int("".join(temp2), 2)


def change_bit_value(state, address, bit, value):
    if value:
        ch = '1'
    else:
        ch = '0'
    temp = list(format(state[address], '016b'))
    idx = len(temp)-1-bit
    temp[idx] = ch
    return int("".join(temp), 2)

def date_as_number(date):
    l = bitfield(date.weekday() + 1)
    l = pad_left_list(l, 3, 0)
    h = bitfield(date.hour)
    h = pad_left_list(h, 5, 0)
    m = bitfield(date.minute)
    m = pad_left_list(m, 6, 0)
    value = shifting(m + h + l)
    return value 