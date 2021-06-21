#!/usr/bin/python
from airzone.protocol import Gateway


def airzone_factory(serial, port, machineId, system="innobus", **kwargs):
    gat = Gateway(serial, port)
    if system == 'innobus':
        from airzone.innobus import Machine
        m = Machine(gat, machineId)
    else:
        from airzone.aido import Aido
        m = Aido(gat, machineId, **kwargs)
    return m



if __name__ == '__main__':
    aido_args = {"has_louvres": False, "speed_as_per": True}    
    m = airzone_factory('modbus.local', 5020, 1, "aido", **aido_args)
    #m = airzone_factory('modbus.local', 5020, 1, "aido")
    
    z = m.get_zones()[0]
    print(m._machine_state)
    print (z._zone_state)
    print (bool(z.is_tacto_on()))
    print (z.get_signal_temperature_value())
    print (z.get_signal_temperature_value())
    print (z.is_floor_active())
    print (z.is_sleep_on())
    print (z.is_automatic_mode())
    print (z.get_zone_mode())
    from airzone.protocol import state_value
    print (state_value(z._zone_state, 0, 0, 1))
    print (format(z._zone_state[0], '016b'))
