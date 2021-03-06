import logging
from airzone.protocol import *
import datetime
import time


class Machine():

    def __init__(self, gateway, machineId, discover_zones=True):
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

    def read_registers(self, address, numRegisters):
        return self._gateway.read_input_registers(
            self._machineId, address, numRegisters)

    def write_register(self, address, value):
        return self._gateway.write_single_register(
            self._machineId, address, value)

    def retrieve_machine_status(self, retrieve_zones = True):
        self._machine_state = self.read_registers(0, 21)
        if retrieve_zones:
            for zone in self._zones:
                zone.retrieve_zone_status()

    def sync_clock(self, force=False):
        current_clock = self.read_registers(4, 1)
        if current_clock[0] == 0 or force:
            self.set_clock()

    def set_clock(self):
        d = datetime.datetime.now()
        value = date_as_number(d)
        self.write_register(4, value)

    def discover_zones(self):
        zones = self.read_registers(9, 2)
        config_zones1 = true_in_list(list(reversed(bitfield(zones[0]))))
        config_zones2 = [
            v + 8 for v in true_in_list(list(reversed(bitfield(zones[1]))))]
        config_zones = config_zones1 + config_zones2
        self._zones = [Zone(self, i + 1) for i in config_zones]

    def get_operation_mode(self):
        return MachineOperationMode(self._machine_state[0])
    
    def set_operation_mode(self, machineOperationMode):
        self.write_register(0, MachineOperationMode[machineOperationMode].value)

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

    def read_registers(self, numRegisters):
        return self._machine._gateway.read_input_registers(
            self._machine._machineId, self.base_zone, 13)

    def write_register(self, address, value):
        return self._machine.write_register(self.base_zone + address, value)
    
    def write_bit_value(self, address, bit, value):
        new_value = change_bit_value(self._zone_state, address, bit, value)
        #self._zone_state[address] = new_value
        self.write_register(address, new_value)

    def __str__(self):
        return "Zone with id: " + str(self.zoneId) + \
                " ZoneMode: " + str(self.get_zone_mode()) + \
                " Tacto On: " + str(self.is_tacto_on()) + \
                " Hold On: " + str(self.is_zone_hold())

    def retrieve_zone_status(self):
        self._zone_state = self._machine._gateway.read_input_registers(
            self._machine._machineId, self.base_zone, 13)

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

    def get_min_signal_value(self):
        return self._zone_state[1] / 10

    def set_min_signal_value(self, value):
        if value >= 18 or value <= 22:
            self.write_register(1, value * 10)

    def get_max_signal_value(self):
        return self._zone_state[2] / 10

    def set_max_signal_value(self, value):
        if value >= 25 or value <= 30:
            self.write_register(2, value * 10)

    def get_signal_temperature_value(self):
        return self._zone_state[3] / 10

    def set_signal_temperature_value(self, value):
        if value >= 18 or value <= 30:
            self.write_register(3, int(value * 10))

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

    def get_local_temperature(self):
        return self._zone_state[10] / 10

    def get_dif_current_temp(self):
        return self.get_signal_temperature_value() - self.get_local_temperature() 
