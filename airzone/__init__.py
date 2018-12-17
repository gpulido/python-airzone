#!/usr/bin/python

import time
import serial
import logging
import threading
from airzone.innobus import Machine
from threading import Lock

from pymodbus.client.sync import ModbusTcpClient as ModbusClient

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

    def __init__(self, url, port, machineId=1, discover=True):
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
        self._machineId = machineId
        self._lock = Lock()
        self.config_client()
        if discover:
            self.discover()

    def config_client(self):
        """
        Configure the serial port
        """
        with self._lock:
            self.client = ModbusClient(self.url, port=self.port)
            self.client.connect()

    def discover(self):
        """[summary]
            Discover all devices registered on the usb-commeo        
        """
        self._Machine = Machine(self, self._machineId)
        self.devices = self._Machine.get_zones()
        print(str(self.devices))

    def init_polling(self):
        self._poll = True
        self.t = threading.Thread(target=self.update_machine_state)
        self.t.start()

    def stop_polling(self):
        self._poll = False

    def update_machine_state(self):
        while(self._poll):
            self._Machine.retrieve_machine_status()
            time.sleep(2)

    # innobus doc type 3
    def read_holding_registers(self, machineid, address, num_registers):
        with self._lock:
            response = self.client.read_holding_registers(
                address, num_registers, unit=machineid)
            logging.debug('read holding registers machineId:' + str(machineid) +
                          ' address: ' + str(address) + ' num_registers: ' + str(num_registers))
            logging.debug('response: ' + str(response.registers))
            return response.registers

    def read_input_registers(self, machineid, address, num_registers):  # innobus doc type 4
        with self._lock:
            response = self.client.read_input_registers(
                address, num_registers, unit=machineid)
            logging.debug('read input registers machineId:' + str(machineid) +
                          ' address: ' + str(address) + ' num_registers: ' + str(num_registers))
            logging.debug('response: ' + str(response.registers))
            return response.registers

    def write_single_register(self, machineid, address, value):
        with self._lock:
            self.client.write_register(address, value, unit=machineid)


if __name__ == '__main__':
    gateway = Gateway('modbus.local', 5020, 1)
    a = gateway._Machine
    #gateway.init_polling()

