#!/usr/bin/python


if __name__ == '__main__':
    from airzone.protocol import Gateway
    gateway = Gateway('modbus.local', 5020)
    from airzone.innobus import Machine
    a = Machine(gateway, 1)
    z = a.get_zones()[0]
    print(a._machine_state)
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
    #a.get_zones()[0].turnoff_zone()
    print(a.get_operation_mode())
    from airzone.protocol import MachineOperationMode
    a.set_operation_mode('HOTPLUS')
    a.retrieve_machine_status()
    print(a.get_operation_mode())

