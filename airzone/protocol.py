import logging
from threading import Lock

from airzone.utils import *
from pymodbus.client.sync import ModbusTcpClient as ModbusClient  # type: ignore


def state_value(state, address, init=0, end=15):
    """
    init and end are included on the desired slice
    """
    if state is None:
        return 0
    binary = format(state[address], '016b')
    r_init = len(binary)-1-init
    r_end = len(binary)-1-end
    kBitSubStr = binary[r_end: r_init+1]
    return int(kBitSubStr, 2)


def bit_value(state, address, bit):
    if state is None:
        return 0
    # return state_value(state, address, bit, bit)
    temp = format(state[address], '016b')
    return int(temp[len(temp)-1-bit])


def change_range_bit_value(state, address, init_bit, num_bit, value):
    if num_bit <= 0:
        return state[address]
    temp2 = list(format(state[address], '016b'))
    idx = len(temp2)-init_bit-num_bit
    idx2 = len(temp2)-init_bit
    temp = list(format(value, '0'+str(num_bit) + 'b'))
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


# --------------------------------------------------------------------------- #
# configure the client logging
# --------------------------------------------------------------------------- #
# FORMAT = ('%(asctime)-15s %(threadName)-15s '
#           '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
# logging.basicConfig(format=FORMAT)
# log = logging.getLogger()
# log.setLevel(logging.DEBUG)
UNIT = 0x1


class Gateway():

    def __init__(self, url, port):
        """                
        Arguments:
            url {String} -- Address where the master is listening
            port {String} -- Serial port string as it is used in pyserial

        Keyword Arguments:
            discover {bool} -- True if the gateway should try to discover 
                               the devices on init (default: {True})
        """
        self._url = url
        self._port = port
        self._lock = Lock()
        self.config_client()

    def config_client(self):
        """
        Configure the serial port
        """
        with self._lock:
            self.client = ModbusClient(self._url, port=self._port)
            self.client.connect()

    # innobus doc type 3
    def read_holding_registers(self, machineid, address, num_registers):
        logging.debug(
            f'read holding registers machineId: {str(machineid)} address: {str(address)} num_registers: {str(num_registers)}')

        try:
            with self._lock:
                response = self.client.read_holding_registers(
                    address, num_registers, unit=machineid)

                logging.debug('response: ' + str(response.registers))
                return response.registers
        except:
            logging.exception('Error reading holding registers')
        return None

    def read_input_registers(self, machineid, address, num_registers):  # innobus doc type 4
        logging.debug('reading input registers: machineId:' + str(machineid) +
                      ' address: ' + str(address) + ' num_registers: ' + str(num_registers))
        try:
            with self._lock:
                response = self.client.read_input_registers(
                    address, num_registers, unit=machineid)
                logging.debug('response: ' + str(response.registers))
                return response.registers
        except:
            logging.exception('Error reading input registers')
        return None

    def write_single_register(self, machineid, address, value):
        with self._lock:
            test = self.client.write_register(address, value, unit=machineid)
            print(test)
    
    def __str__(self):
        return f'Modbus_{self._url}:{self._port}'
