from enum import IntEnum

from deprecated import deprecated  # type: ignore


class OperationMode(IntEnum):
    AUTO = 1
    COOLING = 2
    HEATING = 3
    FAN = 4
    DRY = 5

    @classmethod
    def _missing_(cls, value):
        return OperationMode.AUTO

class Speed(IntEnum):
    AUTO = 0
    SPEED_1 = 1
    SPEED_2 = 2
    SPEED_3 = 3
    SPEED_4 = 4
    SPEED_5 = 5
    SPEED_6 = 6
    SPEED_7 = 7

    @classmethod
    def _missing_(cls, value):
        return Speed.AUTO

class Louvres(IntEnum):
    POS_0 = 0
    POS_1 = 1
    POS_2 = 2
    POS_3 = 3
    POS_4 = 4
    POS_5 = 5
    POS_6 = 6
    POS_7 = 7
    AUTO = 8
    SWING = 9
    SWIRL = 10

    @classmethod
    def _missing_(cls, value):
        return Louvres.AUTO



class Aido():

    def __init__(self, gateway, machineId, has_louvres = True, speed_as_per = False):
        self._gateway = gateway
        self._machineId = machineId
        self._machine_state = None        
        self._has_louvres = has_louvres
        self._speed_as_per = speed_as_per        

        self._retrieve_machine_state()
    
    def _read_registers(self, address, numRegisters):
        return self._gateway.read_input_registers(
            self._machineId, address, numRegisters)
    
    def _write_register(self, address, value):
        return self._gateway.write_single_register(
            self._machineId, address, value)

    def _retrieve_machine_state(self):
        self._machine_state = self._read_registers(0, 7)
    
    def get_is_machine_on(self):
        if self._machine_state == None:
            return 0
        return self._machine_state[0]
    
    def turn_on(self):
        self._write_register(0, 1)
    
    def turn_off(self):
        self._write_register(0, 0)

    def get_signal_temperature_value(self):
        if self._machine_state == None:
            return -1
        return self._machine_state[1] / 10
    
    def set_signal_temperature_value(self, value):
        if value >= 18 or value <= 30:
            self._write_register(1, int(value * 10))

    def get_local_temperature(self):
        return self._machine_state[2] / 10
    
    def get_operation_mode(self):
        if self._machine_state == None:
            return OperationMode.AUTO
        return OperationMode(self._machine_state[3])

    def set_operation_mode(self, operationMode):
        if not self.get_is_machine_on():
            self.turn_on()
        self._write_register(3, OperationMode[operationMode].value)
    
    def get_speed(self):
        if self._machine_state == None:
            return Speed.AUTO
        value = self._machine_state[4]
        #TODO: review for different machines
        if self._speed_as_per:
            value = value * 4 // 100
        return Speed(value)
      
    def set_speed(self, speed):
        value = Speed[speed].value
        if self._speed_as_per:
            value = value*100 // 4

        self._write_register(4, value)
    
    def get_speed_steps(self):
        if self._speed_as_per:
            return 4
        return 7

    def has_louvres(self):
        return self._has_louvres

    def get_louvres(self):
        if self._machine_state == None:
            return Louvres.AUTO
        return Louvres(self._machine_state[5])

    def set_louvres(self, louvre):
        self._write_register(5, Louvres[louvre].value)
    
    #TODO Errors and warnings

    def __str__(self):
        
        return "Aido with id: " + str(self._machineId) + \
            "On:" +  str(self.get_is_machine_on) + \
            "Operation Mode: " + str(self.get_operation_mode()) + \
            "Signal Temp: " + str(self.get_signal_temperature_value()) + \
            "Local Temp: " + str(self.get_local_temperature()) + \
            "Speed: " + str(self.get_speed()) + \
            "Louvres: " + str(self.get_louvres())
        
    
    def unique_id(self):
        return f'Aido_M{self._machineId}_{str(self._gateway)}'

    
    @property
    def machine_state(self):
        return self._machine_state

    @deprecated('Use the machine_state property instead')    
    def get_machine_state(self):
        return self._machine_state
