import datetime
from enum import Enum, IntEnum

from airzone.protocol import *
from deprecated import deprecated  # type: ignore


class OperationMode(Enum):
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


class FancoilSpeed(IntEnum):
    AUTOMATIC = 0
    SPEED_1 = 1
    SPEED_2 = 2
    SPEED_3 = 3
    
    @classmethod
    def _missing_(cls, value):
        return FancoilSpeed.AUTOMATIC


class ProtectionTime(Enum):
    TEN_SEC = 0
    FOUR_MIN = 1


class VentilationMode(Enum):
    CONTINUOUS = 0
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
    FORTY_FIVE = 2
    FORTY = 3


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


class Machine():

    def __init__(self, gateway, machineId):
        self._gateway = gateway
        self._machineId = machineId
        self._machine_state = None
        self.sync_clock(True)
        self._zones = {}        
        self._retrieve_machine_state()

        
    @property
    def machine_state(self):
        return self._machine_state

    @machine_state.setter
    def machine_state(self, value):
        self._machine_state = value
        self.update_zones()

    def discover_zones(self):
        zones = self.read_registers(9, 2)
        config_zones1 = true_in_list(list(reversed(bitfield(zones[0]))))
        config_zones2 = [
            v + 8 for v in true_in_list(list(reversed(bitfield(zones[1]))))]
        config_zones = config_zones1 + config_zones2
        self._zones = {i+1: Zone(self, i + 1) for i in config_zones}
    

    def update_zones(self):
        if self._zones == {}:
            self.discover_zones()
        for zone in self._zones.values():
            zone.retrieve_zone_state()

    @property            
    def zones(self):
        return self._zones.values()

    @deprecated('use property')
    def get_zones(self):
        return self.zones

    def read_registers(self, address, numRegisters):
        return self._gateway.read_input_registers(
            self._machineId, address, numRegisters)

    def write_register(self, address, value):
        return self._gateway.write_single_register(
            self._machineId, address, value)

    def _retrieve_machine_state(self, retrieve_zones=True):
        self.machine_state = self.read_registers(0, 21)

    def sync_clock(self, force=False):
        current_clock = self.read_registers(4, 1)
        if current_clock[0] == 0 or force:
            self.set_clock()

    def set_clock(self):
        d = datetime.datetime.now()
        value = date_as_number(d)
        self.write_register(4, value)

    @property
    def operation_mode(self):
        if self._machine_state == None:
            return OperationMode.STOP
        return OperationMode(self._machine_state[0])

    
    @operation_mode.setter
    def operation_mode(self, operationMode):
        self.write_register(0, OperationMode[operationMode].value)
    

    @deprecated('use property')
    def get_operation_mode(self):
        return self.operation_mode


    @deprecated('use property')
    def set_operation_mode(self, operationMode):
        self.operation_mode = operationMode

    @property
    def hotplus_differential_signal(self):
        return state_value(self._machine_state, 2)

    @deprecated('use property')
    def get_hotplus_differential_signal(self):
        return self.hotplus_differential_signal

    @property
    def protection_time(self):
        return state_value(self._machine_state, 3, 0, 0)

    @deprecated('use property')
    def get_protection_time(self):
        return self.protection_time

    def central_relay_state_1(self):
        if self._machine_state == None:
            return bitfield(0)
        return bitfield(self._machine_state[13])

    def __str__(self):
        zs = "\n".join([str(z) for z in self.get_zones()])
        return "Machine with id: " + str(self._machineId) + \
               "Zones: \n" + zs

    @property
    def unique_id(self):
        return f'Innobus_M{self._machineId}_{str(self._gateway)}'


    @deprecated('Use the machine_state property instead')
    def get_machine_state(self):
        return self._machine_state



class Zone():

    def __init__(self, machine, zone_id):
        self._machine = machine
        self._zone_id = zone_id    
        self.base_zone = zone_id * 256
        self._zone_state = None
        self.retrieve_zone_state()

    def write_register(self, address, value):
        return self._machine.write_register(self.base_zone + address, value)

    def write_bit_value(self, address, bit, value):
        new_value = change_bit_value(self._zone_state, address, bit, value)
        self.write_register(address, new_value)

    def __str__(self):
        return "Zone with id: " + str(self._zone_id) + \
               " ZoneMode: " + str(self.get_zone_mode()) + \
               " Tacto On: " + str(self.is_tacto_on()) + \
               " Hold On: " + str(self.is_zone_hold())

    @property
    def zone_state(self):
        return self._zone_state
    
    @zone_state.setter
    def zone_state(self, value):
        self._zone_state = value

    def retrieve_zone_state(self):
        self.zone_state = self._machine.read_registers(self.base_zone, 13)

    # OPERATION ZONE MODE
    def is_sleep_on(self):
        return bit_value(self._zone_state, 0, 0)

    def turnon_sleep(self):
        self.write_bit_value(0, 0, 1)

    def turnoff_sleep(self):
        self.write_bit_value(0, 0, 0)

    def is_automatic_mode(self):
        return bit_value(self._zone_state, 0, 1)

    def turnon_automatic_mode(self):
        self.write_bit_value(0, 1, 1)

    def turnoff_automatic_mode(self):
        self.write_bit_value(0, 1, 0)

    def get_zone_mode(self):
        temp = state_value(self._zone_state, 0, 0, 1)
        return ZoneMode(temp)

    def set_zone_mode(self, zoneMode):
        zm = ZoneMode[zoneMode]
        if zm == ZoneMode.MANUAL:
            self.turnoff_automatic_mode()
            self.turnoff_sleep()
        elif zm == ZoneMode.MANUAL_SLEEP:
            self.turnoff_automatic_mode()
            self.turnon_sleep()
        elif zm == ZoneMode.AUTOMATIC:
            self.turnon_automatic_mode()
            self.turnoff_sleep()
        elif zm == ZoneMode.AUTOMATIC_SLEEP:
            self.turnon_automatic_mode()
            self.turnon_sleep()

        # temp = change_range_bit_value(self._zone_state, 0, 0, 2, ZoneMode[zoneMode].value)
        # self.write_register(0, temp)

    def is_tacto_on(self):
        return bit_value(self._zone_state, 0, 2)

    def turnon_tacto(self):
        self.write_bit_value(0, 2, 1)

    def turnoff_tacto(self):
        self.write_bit_value(0, 2, 0)

    def is_zone_hold(self):
        return bit_value(self._zone_state, 0, 3)

    def turnon_hold(self):
        self.write_bit_value(0, 3, 1)

    def turnoff_hold(self):
        self.write_bit_value(0, 3, 0)

    def get_speed_selection(self):
        temp = state_value(self._zone_state, 0, 4, 5)
        return FancoilSpeed(temp)

    def set_speed_selection(self, fancoilSpeed):
        temp = change_range_bit_value(self._zone_state, 0, 4, 5, FancoilSpeed[fancoilSpeed].value)
        self.write_register(0, temp)

    ####

    @property
    def min_temp(self):
        if self._zone_state == None:
            return -1
        return self._zone_state[1] / 10 
    
    @min_temp.setter
    def min_temp(self, value):
        if value >= 18 or value <= 22:
            self.write_register(1, value * 10)
    
    
    @deprecated('Use min_temp')
    def get_min_signal_value(self):
        return self.min_temp        
    
    @deprecated('Use min_temp')
    def set_min_signal_value(self, value):
        self.min_temp = value

    @property
    def max_temp(self):
        if self._zone_state == None:
            return -1
        return self._zone_state[2] / 10

    @max_temp.setter
    def max_temp(self, value):
        if value >= 25 or value <= 30:
            self.write_register(2, value * 10)      

    @deprecated('Use max_temp')
    def get_max_signal_value(self):
        return self.max_temp

 

    @deprecated('Use max_temp')
    def set_max_signal_value(self, value):
        self.max_temp = value        

    @property
    def signal_temperature_value(self):
        if self.zone_state == None:
            return -1
        return self.zone_state[3] / 10
    
    @signal_temperature_value.setter
    def signal_temperature_value(self, value):
        if value >= 18 or value <= 30:
            self.write_register(3, int(value * 10))   

    @deprecated('use property')
    def get_signal_temperature_value(self):
        return self.signal_temperature_value


    @deprecated('use property')
    def set_signal_temperature_value(self, value):
        self.signal_temperature_value = value
        

    # ZONE CONFIGURATION

    def is_master_zone(self):
        return bit_value(self._zone_state, 4, 0)

    def get_grid_mode(self):
        temp = bit_value(self._zone_state, 4, 1)
        return GridMode(temp)

    def is_AA_enabled(self):
        return bit_value(self._zone_state, 4, 2)

    def is_Floor_enabled(self):
        return bit_value(self._zone_state, 4, 3)

    def get_grid_angle_hot(self):
        temp = state_value(self._zone_state, 4, 5, 6)
        return GridAngle(temp)

    def get_grid_angle_cold(self):
        temp = state_value(self._zone_state, 4, 7, 8)
        return GridAngle(temp)

    def get_is_minimun_air_enabled(self):
        temp = bit_value(self._zone_state, 4, 9)
        return temp

    def get_probe_type(self):
        temp = state_value(self._zone_state, 4, 10, 11)
        return ProbeType(temp)

    def get_presence(self):
        temp = state_value(self._zone_state, 4, 12, 13)
        return RelayConfig(temp)

    def get_window(self):
        temp = state_value(self._zone_state, 4, 14, 15)
        return RelayConfig(temp)

    ######

    def get_grid_opened_time(self):
        return state_value(self._zone_state, 5) * 10

    def get_tacto_address(self):
        return state_value(self._zone_state, 6)

    def get_master_tacto_address(self):
        return state_value(self._zone_state, 7)

    def get_remote_probe_temperature(self):
        return self._zone_state[8] / 10

    # Zone state register
    def is_zone_grid_opened(self):
        return bit_value(self._zone_state, 9, 0)

    def is_grid_motor_active(self):
        return bit_value(self._zone_state, 9, 1)

    def is_grid_motor_requested(self):
        return bit_value(self._zone_state, 9, 2)

    def is_floor_active(self):
        return bit_value(self._zone_state, 9, 5)

    def get_local_module_fancoil(self):
        temp = bit_value(self._zone_state, 9, 6)
        return LocalFancoilType(temp)

    def is_requesting_air(self):
        return bit_value(self._zone_state, 9, 7)

    def is_occupied(self):
        return bit_value(self._zone_state, 9, 8)

    def is_window_opened(self):
        return bit_value(self._zone_state, 9, 9)

    def get_fancoil_speed(self):
        temp = state_value(self._zone_state, 9, 10, 11)
        return FancoilSpeed(temp)

    def get_proportional_aperture(self):
        return state_value(self._zone_state, 9, 12, 13)

    def is_tacto_connected_cz(self):
        return bit_value(self._zone_state, 9, 14)

    ###

    @property
    def local_temperature(self):
        return self._zone_state[10] / 10

    @deprecated('use property')
    def get_local_temperature(self):
        return self._zone_state[10] / 10

    @property
    def dif_current_temp(self):
        return self.signal_temperature_value - self.local_temperature
    
    @deprecated('use property')
    def get_dif_current_temp(self):
        return self.dif_current_temp

    @property
    def unique_id(self):
        return f'{str(self._machine)}_Z{self._zone_id}'
