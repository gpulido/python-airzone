""" Airzone Local api integration
"""
import logging
from enum import IntEnum

import requests  # type: ignore

_LOGGER = logging.getLogger(__name__)

class OperationMode(IntEnum):
    STOP = 1
    COOLING = 2
    HEATING = 3
    FAN = 4
    DRY = 5
    AUTO = 7

    @classmethod
    def _missing_(cls, value):
        return OperationMode.STOP

class TempUnits(IntEnum):
    CELSIUS = 0
    FAHRENHEIT = 1


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

class Machine():

    def __init__(self, machine_ipaddr, port=3000, system_id=1, vaf_cbs=False):
        self._API_ENDPOINT = f"http://{machine_ipaddr}:{str(port)}/api/v1/hvac"
        self._machine_id = system_id
        self._machine_ip = machine_ipaddr
        self._data = {'SystemID': self._machine_id, 'ZoneID': 0}
        self._error_log = []
        self._machine_state = None
        self._zones = {}                
        self.retrieve_system_state()                
    
    @property
    def machine_state(self):
        return self._machine_state

    @machine_state.setter
    def machine_state(self, value):
        self._machine_state = value
        _LOGGER.debug(value)
        self.update_zones()

    def discover_zones(self):                
        self._zones = {z['zoneID']: Zone(self, z['zoneID'], z) for z in self.machine_state if z['zoneID'] != 0}

    def update_zones(self):
        if self._zones == {}:
            self.discover_zones()
        for z in self.machine_state:
            self._zones[z['zoneID']].zone_state = z

    @property
    def zones(self):
        return self._zones.values()
    

    def retrieve_system_state(self):
        try:
            response = requests.post(url=self._API_ENDPOINT,
                                           json=self._data)
            if response.status_code == 200:
                response_json = response.json()
                self.machine_state = response_json['data']                  
            elif response.status_code >= 500:
                print(f'[!] [{response.status_code}] Server Error: ' + response.text)            
             
        except requests.exceptions.RequestException as e:
            _LOGGER.exception(str(e))            

    def set_zone_parameter_value(self, zone_id, parameter, value):
        try:

            self._data['ZoneID'] = zone_id
            self._data[parameter] = value
            response = requests.put(url=self._API_ENDPOINT,
                                    json=self._data)

            if response.status_code == 200:
                # Update successfully. We update manually the value.
                # WARNING: this will only update the first zone values for the system attributes.
                # so until a new retrieve_system_state is made the only zone with the proper
                # system values is the first one. It this is not desirable a retrieve_system_state
                # should be done just after this
                if zone_id == 0:
                    zone_id = next(iter(self._zones))    
                self._zones[zone_id][parameter] = value
            elif response.status_code >= 500:
                print(f'[!] [{response.status_code}] Server Error: ' + response.text)            
            
        except requests.exceptions.RequestException as e:
            _LOGGER.exception(str(e))                        
    
    def _get_zone_property(self, zone_id, prop):
        z_id = zone_id
        if z_id == 0:
            z_id = next(iter(self._zones))            
        if prop in self._zones[z_id].zone_state:
            return self._zones[z_id].zone_state[prop]        
        return None


    @property
    def speed(self):
        speed = self._get_zone_property(0, 'speed')
        if speed is not None:
            return Speed(speed)
        return Speed.AUTO
    
    @speed.setter
    def speed(self, speed):
        self.set_zone_parameter_value(0, 'speed', speed)
    
    @property
    def operation_mode(self):       
        return OperationMode(self._get_zone_property(0, 'mode'))

    @operation_mode.setter
    def operation_mode(self, mode):
        self.set_zone_parameter_value(0, 'mode', mode)
    
    @property    
    def units(self):
        return TempUnits(self._get_zone_property(0, 'units'))

    @property
    def unique_id(self):
        return f'Local_Api{self._machine_id}_{str(self._machine_ip)}'
  
    def __str__(self):
        zs = "\n".join([str(z) for z in self.zones])
        return "Machine with id: " + str(self._machine_id) + \
                "Mode: " + str(self.operation_mode) + \
                "\nZones\n" + str(zs)


class Zone:
    def __init__(self, machine, zone_id, data = {}):
        self._machine = machine
        self._zone_id = zone_id        
        self.zone_state = data
              
    def _set_parameter_value(self, prop, value):
        self._machine.set_zone_parameter_value(self._zone_id, prop, value)

    @property
    def zone_state(self):
        return self._zone_state
    
    @zone_state.setter
    def zone_state(self, value):
        self._zone_state = value
    
    def is_on(self):
        return self.zone_state['on']

    def turn_on(self):
        self._set_parameter_value('on', 1)

    def turn_off(self):
        self._set_parameter_value('on', 0)

    @property
    def signal_temperature_value(self):
        return self.zone_state['setpoint']
    
    @signal_temperature_value.setter
    def signal_temperature_value(self, setpoint):
        self._set_parameter_value('setpoint', setpoint)

    @property
    def name(self):
        return self.zone_state['name']
    
    @name.setter
    def name(self, name):
        self._set_parameter_value('name', name)

    @property
    def max_temp(self):
        return self.zone_state['maxTemp']

    @property
    def min_temp(self):
        return self.zone_state['minTemp']

    @property
    def local_temperature(self):
        return self.zone_state['roomTemp']

    @property
    def dif_current_temp(self):
        return self.signal_temperature_value - self.local_temperature

    @property
    def room_humidity(self):
        return self.zone_state['humidity']

    @property
    def air_demand(self):
        return self.zone_state['air_demand']

    @property
    def floor_demand(self):
        return self.zone_state['floor_demand']

    
    @property
    def units(self):
        return TempUnits(self.zone_state['units'])


    @property
    def unique_id(self):
        # TODO: review
        return f'{self.name}_Z{str(self._zone_id)}'        


    def __str__(self):
        return "Zone with id: " + str(self._zone_id) + \
               " Name: " + str(self.name) + \
               " Zone is On: " + str(self.is_on()) + \
               " Air demand is: " + str(self.air_demand) + \
               " Room Temp: " + str(round(self.local_temperature, 1)) + \
               " " + str(self.units) +\
               " Room humidity: " + str(self.room_humidity) + \
               " Max_Temp: " + str(self.max_temp) + \
               " Min_Temp: " + str(self.min_temp)
