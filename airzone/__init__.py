#!/usr/bin/python



def airzone_factory(address, port, machineId, system="innobus", **kwargs):
    if system == 'localapi':        
        from airzone.localapi import Machine, API
        api = API(address, port)
        m = Machine(api, machineId)
    else:
        from airzone.protocol import Gateway
        gat = Gateway(address, port)
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
    # m = airzone_factory('modbus.local', 5020, 1, "aido")

    z = m.get_zones()[0]
    print(m._machine_state)
    print(z._zone_state)
    print(bool(z.is_tacto_on()))
    print(z.get_signal_temperature_value())    
    print(z.is_floor_active())
    print(z.is_sleep_on())
    print(z.is_automatic_mode())
    print(z.get_zone_mode())
    from airzone.protocol import state_value

    print(state_value(z._zone_state, 0, 0, 1))
    print(format(z._zone_state[0], '016b'))

    ## Localapi
    # Lines for Tests. Adapt argument ip address and system id (1 == standard).
    #m = airzone_factory('192.168.90.9', 3000, 1, "localapi")  
    #print("Printing Post JSON data")
    #print(m.machine_state)
    #print("Number of zones: ", len(m.zones))
    #print(m)
