import logging
from airzone.protocol import *
import datetime
import time


class Machine():

    def __init__(self, gateway, machineId, discover_zones = True):
        self._gateway = gateway
        self._machineId = machineId
        self._machine_state = None
        self.sync_clock()
        self._zones = []
        if discover_zones:
            self.discover_zones()
        self.retrieve_machine_status()

    def get_zones(self):
        return self._zones

    def retrieve_machine_status(self):
        self._machine_state = self._gateway.read_input_registers(
            self._machineId, 0, 21)
        for zone in self._zones:
            zone.retrieve_zone_status()

    def sync_clock(self, force=False):
        current_clock = self._gateway.read_input_registers(
            self._machineId, 4, 1)
        if current_clock[0] == 0 or force:
            self.set_clock()

    def set_clock(self):
        d = datetime.datetime.now()
        value = date_as_number(d)
        self._gateway.write_single_register(self._machineId, 4, value)

    def discover_zones(self):
        zones = self._gateway.read_input_registers(self._machineId, 9, 2)
        config_zones1 = true_in_list(list(reversed(bitfield(zones[0]))))
        config_zones2 = [
            v + 8 for v in true_in_list(list(reversed(bitfield(zones[1]))))]
        config_zones = config_zones1 + config_zones2
        self._zones = [Zone(self, i + 1) for i in config_zones]

    def get_operation_mode(self):
        temp = state_value(self._machine_state, 0, 0, 8)
        return MachineOperationMode(temp)

    def get_fancoil_speed(self):
        temp = state_value(self._machine_state, 0, 9, 10)
        return FancoilSpeed(temp)

    def get_hotplus_differential_signal(self):
        return state_value(self._machine_state, 2)

    def get_protection_time(self):
        return state_value(self._machine_state, 3, 0, 0)

    def central_relay_state_1(self):
        return bitfield(self._machine_state[13])

    # @property
    # def machine_operation_mode(self):
    #     return self._machine_operation_mode

    # @machine_operation_mode.setter
    # def machine_operation_mode(self, operation_mode):
    #     self._gateway.write_single_register(self._machineId, "00H", operation_mode.value)


class Zone():

    def __init__(self, machine, zoneId):
        self._machine = machine
        self.zoneId = zoneId
        self._zone_state = None
        self.base_zone = zoneId * 256
        self.retrieve_zone_status()
    
    def __str__(self):
        return "Zone with id: " + str(self.zoneId)

    def retrieve_zone_status(self):
        self._zone_state = self._machine._gateway.read_input_registers(
            self._machine._machineId, self.base_zone, 13)

    # OPERATION ZONE MODE
    def get_sleep_mode(self):
        temp = bit_value(self._zone_state, 0, 0)
        return OnOff(temp)

    def get_zone_programing_mode(self):
        temp = bit_value(self._zone_state, 0, 1)
        return OnOff(temp)

    def get_tacto_on(self):
        temp = bit_value(self._zone_state, 0, 2)
        return OnOff(temp)

    def get_zone_hold(self):
        temp = bit_value(self._zone_state, 0, 3)
        return OnOff(temp)

    def get_speed_selection(self):
        temp = state_value(self._zone_state, 0, 4, 5)
        return FancoilSpeed(temp)

    def get_zone_on_off(self):
        temp = bit_value(self._zone_state, 0, 6)
        return OnOff(temp)

    def get_zone_mode(self):
        temp = state_value(self._zone_state, 0, 8, 10)
        print("zone_mode " + str(temp))
        return ZoneMode(temp)

    ####

    def get_min_signal_value(self):
        return state_value(self._zone_state, 1) / 10

    def get_max_signal_value(self):
        return state_value(self._zone_state, 2) / 10

    def get_signal_temperature_value(self):
        return state_value(self._zone_state, 3) / 10

    # ZONE CONFIGURATION

    def get_is_master_zone(self):
        temp = bit_value(self._zone_state, 4, 0)
        return temp == 1

    def get_grid_mode(self):
        temp = bit_value(self._zone_state, 4, 1)
        return GridMode(temp)

    def get_is_AA_enabled(self):
        temp = bit_value(self._zone_state, 4, 2)
        return temp == 1

    def get_is_Floor_enabled(self):
        temp = bit_value(self._zone_state, 4, 3)
        return temp == 1

    def get_grid_angle_hot(self):
        temp = state_value(self._zone_state, 4, 5, 6)
        return GridAngle(temp)

    def get_grid_angle_cold(self):
        temp = state_value(self._zone_state, 4, 7, 8)
        return GridAngle(temp)

    def get_is_minimun_air_enabled(self):
        temp = bit_value(self._zone_state, 4, 9)
        return temp == 1

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
        return state_value(self._zone_state, 8) / 10

    # Zone state register
    def get_is_zone_grid_opened(self):
        temp = bit_value(self._zone_state, 9, 0)
        return temp == 1

    def get_is_grid_motor_active(self):
        temp = bit_value(self._zone_state, 9, 1)
        return temp == 1

    def get_is_grid_motor_requested(self):
        temp = bit_value(self._zone_state, 9, 2)
        return temp == 1

    def get_is_floor_active(self):
        temp = bit_value(self._zone_state, 9, 5)
        return temp == 1

    def get_local_module_fancoil(self):
        temp = bit_value(self._zone_state, 9, 6)
        return LocalFancoilType(temp)

    def get_is_requesting_air(self):
        temp = bit_value(self._zone_state, 9, 7)
        return temp == 1

    def get_is_occuped(self):
        temp = bit_value(self._zone_state, 9, 8)
        return temp == 1

    def get_is_window_opened(self):
        temp = bit_value(self._zone_state, 9, 9)
        return temp == 1

    def get_fancoil_speed(self):
        temp = state_value(self._zone_state, 9, 10, 11)
        return FancoilSpeed(temp)

    def get_proportional_aperture(self):
        return state_value(self._zone_state, 9, 12, 13)

    def get_is_tacto_connected_cz(self):
        temp = bit_value(self._zone_state, 9, 14)
        return temp == 1
    ###

    def get_local_temperature(self):
        return state_value(self._zone_state, 10) / 10
