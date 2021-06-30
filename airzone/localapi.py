import requests  # type: ignore


class Machine:

    def __init__(self, machine_ipaddr, port=3000, system_id=1):
        self._API_ENDPOINT = f"http://{machine_ipaddr}:{str(port)}/api/v1/hvac"
        self._machine_id = system_id
        self._machine_ip = machine_ipaddr
        self._data = {'SystemID': self._machine_id, 'ZoneID': 0}
        self._error_log = []
        self._machine_state = None
        self._response = None
        self._response_json = None
        self._system_modes = {1: "Stop", 2: "Cooling", 3: "Heating", 4: "Fan", 5: "Dry"}
        # fan speed is not in use
        self._fan_speeds = {0: "Auto", 1: "Low speed", 2: "Medium Speed", 3: "High Speed"}
        self._units = {0: "Celsius", 1: "Fahrenheit"}
        self._zones = []
        self.get_system_data()
        self.discover_zones()

    def discover_zones(self):
        self._zones = [Zone(self, listmember['zoneID']) for listmember in self._machine_state if
                       listmember['zoneID'] != 0]

    def get_zones(self):
        return self._zones

    def get_system_data(self):
        try:
            self._response = requests.post(url=self._API_ENDPOINT,
                                           json=self._data)
            if self._response.status_code == 200:
                self._response_json = self._response.json()
                self._machine_state = self._response_json['data']
            elif self._response.status_code >= 500:
                print(f'[!] [{self._response.status_code}] Server Error')
                return None
            self._response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def get_zone_property(self, zone_id, prop):
        for listmember in self._machine_state:
            if zone_id == listmember['zoneID']:
                return listmember[prop]

    def set_zone_parameter_value(self, zone_id, parameter, value):
        try:
            self._data['ZoneID'] = zone_id
            self._data[parameter] = value
            self._response = requests.put(url=self._API_ENDPOINT,
                                          json=self._data)
            if self._response.status_code == 200:
                self._response_json = self._response.json()
                self._machine_state = self._response_json['data']
            elif self._response.status_code >= 500:
                print(f'[!] [{self._response.status_code}] Server Error')
                return None
            self._response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def set_fan_speed(self, mode):
        self.set_zone_parameter_value(0, 'speed', mode)

    def set_system_mode(self, mode):
        self.set_zone_parameter_value(0, 'mode', mode)

    def get_system_modes(self):
        return self._system_modes

    def get_mode(self):
        return self.get_zone_property(1, 'mode')

    def unique_id(self):
        return f'Local_Api{self._machine_id}_{str(self._machine_ip)}'

    def get_machine_state(self):
        return self._machine_state

    def __str__(self):
        zs = "\n".join([str(z) for z in self.get_zones()])
        return "Machine with id: " + str(self._machine_id) + \
               "\nModes: " + str(self._system_modes) + \
               "\nSystem mode: " + str(self._system_modes[self.get_mode()]) + \
               "\nZones\n" + zs


class Zone:
    def __init__(self, machine, zone_id):
        self._machine = machine
        self._zone_id = zone_id

    def get_property(self, prop):
        return self._machine.get_zone_property(self._zone_id, prop)

    def set_parameter_value(self, prop, value):
        self._machine.set_zone_parameter_value(self._zone_id, prop, value)

    def turnon(self):
        self.set_parameter_value('on', 1)

    def turnoff(self):
        self.set_parameter_value('on', 0)

    def toggle_mode(self):
        if self._machine.get_operation_mode() == 1:
            self.set_parameter_value('on', 0)
        else:
            self.set_parameter_value('on', 1)

    def set_setpoint(self, setpoint):
        self._machine.set_zone_parameter_value('setpoint', setpoint)

    def set_maxtemp(self, maxtemp):
        self._machine.set_zone_parameter_value('maxTemp', maxtemp)

    def set_mintemp(self, mintemp):
        self._machine.set_zone_parameter_value('minTemp', mintemp)

    def set_name(self, name):
        self._machine.set_zone_parameter_value('name', name)

    def get_name(self):
        return self.get_property('name')

    def is_on(self):
        return self.get_property('on')

    def get_max_temp(self):
        return self.get_property('maxTemp')

    def get_min_temp(self):
        return self.get_property('minTemp')

    def get_set_point(self):
        return self.get_property('setpoint')

    def get_room_temp(self):
        return self.get_property('roomTemp')

    def get_room_humidity(self):
        return self.get_property('humidity')

    def get_air_demand(self):
        return self.get_property('air_demand')

    def get_floor_demand(self):
        return self.get_property('floor_demand')

    def get_units(self):
        return self.get_property('units')

    def __str__(self):
        return "Zone with id: " + str(self._zone_id) + \
               " Name: " + str(self.get_name()) + \
               " Zone is On: " + str(self.is_on()) + \
               " Air demand is: " + str(self.get_air_demand()) + \
               " Room Temp: " + str(round(self.get_room_temp(), 1)) + \
               " " + str(self._machine._units[self.get_units()]) +\
               " Room humidity: " + str(self.get_room_humidity()) + \
               " Max_Temp: " + str(self.get_max_temp()) + \
               " Min_Temp: " + str(self.get_min_temp())


if __name__ == '__main__':
    # Lines for Tests. Adapt argument ip address and system id (1 == standard).
    m = Machine('192.168.90.9', system_id=1)
    print("Printing Post JSON data")
    print(m.get_machine_state())
    print("Number of zones: ", len(m.get_zones()))
    print(m)
