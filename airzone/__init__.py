#!/usr/bin/python

import time
import serial
import logging
from innobus import Machine
from threading  import Lock

from pymodbus.client.sync import ModbusTcpClient as ModbusClient

# --------------------------------------------------------------------------- #
# configure the client logging
# --------------------------------------------------------------------------- #
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

UNIT = 0x1

class Gateway():   

    def __init__(self, url, port, discover = True):
        """                
        Arguments:
            url {String} -- Address where the master is listening
            port {String} -- Serial port string as it is used in pyserial
        
        Keyword Arguments:
            discover {bool} -- True if the gateway should try to discover 
                               the devices on init (default: {True})
        """
        self.url = url
        self.port = port
        self._lock = Lock()
        self.config_client()
    
    def config_client(self):
        """
        Configure the serial port
        """
        with self._lock:
            self.client = ModbusClient(self.url, port=self.port)
            self.client.connect()
    
    def read_holding_registers(self, machineid, address, num_registers): #innobus doc type 3
        with self._lock:
            response = self.client.read_holding_registers(address, num_registers, unit = machineid)
            return response.registers

    def read_input_registers(self, machineid, address, num_registers): #innobus doc type 4
        with self._lock:
            response = self.client.read_input_registers(address, num_registers, unit = machineid)
            return response.registers
    
    def write_single_register(self, machineid, address, value):
        with self._lock:
            self.client.write_register(address,value, unit = machineid)



if __name__ == '__main__':
    gateway = Gateway('modbus.local', 5020)
    machine = Machine(gateway, 1)
    
