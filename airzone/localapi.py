import requests  # type: ignore


class Machine:

    def __init__(self, machine_ipaddr, port=3000, system_id=1):
        self._machine_ip = machine_ipaddr
        self._machine_id = system_id
        self._machine_state = None
        self._API_ENDPOINT = f"http://{machine_ipaddr}:{str(port)}/api/v1/hvac"
        self._data = {'SystemID': self._machine_id, 'ZoneID': 0}
        self._machine_state = None
        self._zones = []
        self.get_system_data()
        self.discover_zones()
        self._system_modes = self.get_system_modes()

    def discover_zones(self):
        self._zones = [Zone(self, listmember['zoneID']) for listmember in self._machine_state if
                       listmember['zoneID'] != 0]

    def get_zones(self):
        return self._zones

    def get_system_data(self):
        try:
            response = requests.post(url=self._API_ENDPOINT,
                                     json=self._data)
            if response.status_code == 200:
                response_json = response.json()
                self._machine_state = response_json['data']
            elif response.status_code >= 500:
                print(f'[!] [{response.status_code}] Server Error')
                return None
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise SystemExit(e)
        except requests.exceptions.Timeout as e:
            raise SystemExit(e)
        except requests.exceptions.ConnectionError as e:
            print("Error Connecting:", e)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)

    def get_system_modes(self):
        for listmember in self._machine_state:
            if 'modes' in listmember:
                return listmember['modes']

    def get_zone_property(self, zone_id, property):
        for listmember in self._machine_state:
            if zone_id == listmember['zoneID']:
                return listmember[property]

    def set_zone_parameter_value(self, zone_id, parameter, value):
        try:
            # print(self._data)
            self._data['ZoneID'] = zone_id
            self._data[parameter] = value
            # print(self._data)
            response = requests.put(url=self._API_ENDPOINT,
                                    json=self._data)
            if response.status_code == 200:
                # TODO: this response is the same as if we ask for the 0 zone?
                response_json = response.json()
                self._machine_state = response_json['data']
            elif response.status_code >= 500:
                print(f'[!] [{response.status_code}] Server Error')
                return None
            self._response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise SystemExit(e)
        except requests.exceptions.Timeout as e:
            raise SystemExit(e)
        except requests.exceptions.ConnectionError as e:
            print("Error Connecting:", e)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)

    def set_mode(self, mode):
        self._set_zone_parameter_value(0, 'mode', mode)

    def get_mode(self):
        # Mode is global to the system TODO: check that the zone_id = 0 is available for this
        # TODO: Transform in enum
        return self.get_zone_property(0, 'mode')

    def unique_id(self):
        return f'Local_Api{self._machineId}_{str(self._machine_ip)}'

    def get_machine_state(self):
        return self._machine_state

    def __str__(self):
        zs = "\n".join([str(z) for z in self.get_zones()])
        return "Machine with id: " + str(self._machineId) + \
               "Zones: \n" + zs


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
        if self.get_operation_mode() == 1:
            self.set_parameter_value('on', 0)
        else:
            self.set_parameter_value('on', 1)

    def set_setpoint(self, setpoint):
        self.set_zone_parameter_value('setpoint', setpoint)

    def set_maxtemp(self, maxtemp):
        self.set_zone_parameter_value('maxTemp', maxtemp)

    def set_mintemp(self, mintemp):
        self.set_zone_parameter_value('minTemp', mintemp)

    def set_name(self, name):
        self.set_zone_parameter_value('name', name)

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
        return self.get_property('roomtemp')

    def get_room_humidity(self):
        return self.get_property('humidity')

    def __str__(self):
        return "Zone with id: " + str(self._zone_id) + \
               " Name: " + str(self.get_name()) + \
               " Zone is On: " + str(self.is_on()) + \
               " Room Temp: " + str(self.get_room_temp()) + \
               " Room humidity: " + str(self.get_room_humidity()) + \
               " Max_Temp: " + str(self.get_max_temp()) + \
               " Min_Temp: " + str(self.get_min_temp())


if __name__ == '__main__':
    # Lines for Tests. Adapt argument ip address and system id (1 == standard).
    m = Machine('192.168.90.9', system_id=1)
    print("Printing Post JSON data")
    print(m.get_machine_state())
    print("Number of zones: ", len(m.get_zones()))
