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


class API():

    def __init__(self,  machine_ipaddr, port=3000):
        self._machine_ip = machine_ipaddr
        self._port = port
        self._API_ENDPOINT = f"http://{machine_ipaddr}:{str(port)}/api/v1/hvac"
    
    def retrieve_state(self, system_id, zone_id):
        try:
            data = {'SystemID': system_id, 'ZoneID': zone_id}
            response = requests.post(url=self._API_ENDPOINT,
                                           json=data)
            if response.status_code == 200:
                response_json = response.json()
                return response_json['data']                
            elif response.status_code >= 500:
                _LOGGER.info(f'[!] [{response.status_code}] Server Error: ' + response.text)                
                return None

        except requests.exceptions.RequestException as e:
            _LOGGER.exception(str(e))

    def set_zone_parameter_value(self, machine_id, zone_id, parameter, value):
        try:
            
            data = {'systemID': machine_id, 'zoneID': zone_id}
            data[parameter] = value
            response = requests.put(url=self._API_ENDPOINT,
                                    json=data)

            if response.status_code == 200:
                # Update successfully. We update manually the value.
                # WARNING: this will only update the first zone values for the system attributes.
                # so until a new retrieve_system_state is made the only zone with the proper
                # system values is the first one. It this is not desirable a retrieve_system_state
                # should be done just after this
                return value                
            elif response.status_code >= 500:
                _LOGGER.info(f'[!] [{response.status_code}] Server Error: ' + response.text)
                return None
                

        except requests.exceptions.RequestException as e:
            _LOGGER.exception(str(e))

    def __str__(self):
        return f'LocalApi: {str(self._machine_ip)}'

    

class Machine():

    def __init__(self, api, system_id=1, vaf_cbs=False):
        self._api = api        
        self._machine_id = system_id        
        self._error_log = []        
        self._machine_state = None
        self._machine_zone_state = None
        self._zones = {}                
        self.retrieve_machine_state()

    @property
    def machine_state(self):
        return self._machine_state


    @machine_state.setter
    def machine_state(self, value):
        self._machine_state = value
        _LOGGER.debug(value)
    
    @property
    def machine_id(self):
        return self._machine_id
     
 
    def retrieve_machine_state(self, update_zones = False):
        state = self._api.retrieve_state(self._machine_id, 0)
        if state is not None and len(state) > 0:
            if self._zones == {}:
                self.discover_zones(state)
            self.machine_state = state[0]
            if update_zones:
                for z in state:
                    zone_id = z['zoneID']
                    if zone_id in self._zones:
                        self._zones[zone_id].zone_state = z
    
    def discover_zones(self, state):
        self._zones = {z['zoneID']: Zone(self._api, self, z['zoneID']) for z in state if z['zoneID'] != 0}        
                    
    @property
    def zones(self):
        return self._zones.values()
          
    @property
    def speed(self):
        if 'speed' in self.machine_state:
            speed = self.machine_state['speed']
            if speed is not None:
                return Speed(speed)
        return Speed.AUTO

    @speed.setter
    def speed(self, speed):
        s = speed
        if isinstance(speed, IntEnum):
            s = speed.value
        value = self._api.set_zone_parameter_value(self._machine_id, 0, 'speed', s)
        if value:
            self.machine_state['speed'] = value

    @property
    def operation_mode(self):
        return OperationMode(self.machine_state['mode'])

    @operation_mode.setter
    def operation_mode(self, mode):
        m = mode
        if isinstance(mode, IntEnum):
            m = mode.value
        value = self._api.set_zone_parameter_value(self._machine_id, 0, 'mode', m)
        if value:
            self.machine_state['mode'] = value

    @property
    def units(self):
        return TempUnits(self.machine_state['units'])        

    @property
    def unique_id(self):
        return f'{str(self._api)}_{self._machine_id}'


    def __str__(self):
        zs = "\n".join([str(z) for z in self.zones])
        return "Machine with id: " + str(self._machine_id) + \
                "Mode: " + str(self.operation_mode) + \
                "\nZones\n" + str(zs)


class Zone:
    def __init__(self, api, machine, zone_id):  
        self._api = api
        self._machine = machine
        self._machine_id = self.machine.machine_id              
        self._zone_id = zone_id        
        self.zone_state = None      
        self._name = f"Zone_{zone_id}"
        self.retrieve_zone_state()        

    def _set_parameter_value(self, prop, value):
        self._api.set_zone_parameter_value(self._machine_id, self._zone_id, prop, value)


    @property
    def zone_state(self):
        return self._zone_state

    @zone_state.setter
    def zone_state(self, value):
        self._zone_state = value

    @property
    def machine(self):
        return self._machine

    def retrieve_zone_state(self):
        state = self._api.retrieve_state(self._machine_id, self._zone_id)        
        if state is not None and len(state)> 0:
            self.zone_state = state[0]

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
        # Old fw doesn't expose the name
        if 'name' in self.zone_state:
            return self.zone_state['name']
        return self._name

    @name.setter
    def name(self, name):
        # Old fw doesn't expose the name
        self._name = name
        if 'name' in self.zone_state:
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
