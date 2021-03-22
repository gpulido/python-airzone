from enum import Enum

class OperationMode(Enum):
    AUTO = 1
    COOLING = 2
    HEATING = 3
    FAN = 4
    DRY = 5

class Speed(Enum):
    AUTO = 0
    SPEED_1 = 1
    SPEED_2 = 2
    SPEED_3 = 3
    SPEED_4 = 4
    SPEED_5 = 5
    SPEED_6 = 6
    SPEED_7 = 7

class Louvres(Enum):
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


class Aido():

    def __init__(self, gateway, machineId):
        self._gateway = gateway
        self._machineId = machineId
        self._machine_state = None

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
        self._write_register(3, OperationMode[operationMode].value)
    
    def get_speed(self):
        if self._machine_state == None:
            return Speed.AUTO
        return Speed(self._machine_state[4])
      
    def set_speed(self, speed):
        self._write_register(4, Speed[speed].value)

    def get_louvres(self):
        if self._machine_state == None:
            return Louvres.AUTO
        return Louvres(self._machine_state[5])

    def set_louvres(self, louvre):
        self._write_register(5, Louvres[louvre].value)
    
    #TODO Errors and warnings



    


    

    