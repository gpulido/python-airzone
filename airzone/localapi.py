"""
Author: Stefan Senftleben
email address: stefan.senftleben@posteo.de
Version: 0.2
Description: Class for getting and setting information on an airzone ethernet gateway, which serves on tcp 3000 with a
             REST api.
"""

import requests


class Machine:

    def __init__(self, machine_ipaddr, system_id):
        self._machine_ip = machine_ipaddr
        self._system_id = system_id
        self._machine_state = None
        self._zones = []
        self._API_ENDPOINT = "http://{}:3000/api/v1/hvac".format(self._machine_ip)
        self._data = {'SystemID': 1, 'ZoneID': 0}
        self._response = None
        self._response_json = None
        self._zonecount = None
        self._zone_name = None
        self._zone_status = None
        self._zone_maxtemp = None
        self._zone_mintemp = None
        self._zone_setpoint = None
        self._zone_roomtemp = None
        self._zone_roomhumidity = None
        self._zone_air_demand = None
        self._zone_mode = None
        if system_id != 1:
            self._data['SystemID'] = system_id
        self.get_system_data()

    def set_zone_parameter_value(self, zone_id, parameter, value):
        try:
            print(self._data)
            self._data['ZoneID'] = zone_id
            self._data[parameter] = value
            print(self._data)
            self._response = requests.put(url=self._API_ENDPOINT,
                                          json=self._data)
            if self._response.status_code == 200:
                self._response_json = self._response.json()
            elif self._response.status_code >= 500:
                print('[!] [{0}] Server Error'.format(self._response.status_code))
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

    def set_zone_operation_toggle(self, zone_id):
        if self.get_operation_mode(zone_id) == 1:
            self.set_zone_parameter_value(zone_id, 'on', 0)
        else:
            self.set_zone_parameter_value(zone_id, 'on', 1)

    def get_system_data(self):
        try:
            self._response = requests.post(url=self._API_ENDPOINT,
                                           json=self._data)
            if self._response.status_code == 200:
                self._response_json = self._response.json()
            elif self._response.status_code >= 500:
                print('[!] [{0}] Server Error'.format(self._response.status_code))
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

    @property
    def response_json(self):
        return self._response_json

    @property
    def zone_count(self):
        self._zonecount = len(m._response_json['data'])
        return self._zonecount + 1

    def get_name(self, zonenumber):
        for listmember in m._response_json['data']:
            if zonenumber == listmember['zoneID']:
                self._zone_name = listmember['name']
                return self._zone_name

    def get_operation_mode(self, zonenumber):
        for listmember in m._response_json['data']:
            if zonenumber == listmember['zoneID']:
                self._zone_status = listmember['on']
                return self._zone_status

    def get_max_temp(self, zonenumber):
        for listmember in m._response_json['data']:
            if zonenumber == listmember['zoneID']:
                self._zone_maxtemp = listmember['maxTemp']
                return self._zone_maxtemp

    def get_min_temp(self, zonenumber):
        for listmember in m._response_json['data']:
            if zonenumber == listmember['zoneID']:
                self._zone_mintemp = listmember['minTemp']
                return self._zone_mintemp

    def get_set_point(self, zonenumber):
        for listmember in m._response_json['data']:
            if zonenumber == listmember['zoneID']:
                self._zone_mintemp = listmember['setpoint']
                return self._zone_setpoint

    def get_room_temp(self, zonenumber):
        for listmember in m._response_json['data']:
            if zonenumber == listmember['zoneID']:
                self._zone_roomtemp = listmember['roomTemp']
                return round(self._zone_roomtemp, 1)

    def get_room_humidity(self, zonenumber):
        for listmember in m._response_json['data']:
            if zonenumber == listmember['zoneID']:
                self._zone_roomhumidity = listmember['humidity']
                return self._zone_roomhumidity

    def get_air_demand(self, zonenumber):
        for listmember in m._response_json['data']:
            if zonenumber == listmember['zoneID']:
                self._zone_air_demand = listmember['air_demand']
                return self._zone_air_demand

    def get_zone_mode(self, zonenumber):
        for listmember in m._response_json['data']:
            if zonenumber == listmember['zoneID']:
                self._zone_mode = listmember['mode']
                return self._zone_mode


# Lines for Tests. Adapt argument ip address and system id (1 == standard).

m = Machine('192.168.90.9', 1)
print("Printing Post JSON data")
# print(m.response_json)
print(m.response_json['data'])
print(u"\nNumber of zones: ", m.zone_count)
for i in range(1, m.zone_count):
    print(i, m.get_name(i), m.get_operation_mode(i), m.get_max_temp(i),
          m.get_min_temp(i), m.get_room_temp(i), m.get_room_humidity(i),
          m.get_air_demand(i), m.get_zone_mode(i), '\n')

# m.set_zone_parameter_value(1, 'setpoint', 23)

# Toggle the operation mode of a zone
# m.set_zone_operation_toggle(1)
