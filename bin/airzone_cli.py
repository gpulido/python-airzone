#!/usr/bin/env python
import argparse

from importlib_metadata import PackageNotFoundError, version  # type: ignore

import airzone

try:
    __version__ = version("python-airzone")
except PackageNotFoundError:
    # package is not installed
    pass


def action(args):
    m = airzone.airzone_factory(args.serial, args.port, args.machine, args.system)
    if args.state == 'str':
        print(str(m))
    else:
        print(str(m.get_machine_state()))
    
    
parser = argparse.ArgumentParser(prog='airzone')
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
parser.add_argument("serial", type=str, help="serial device")
parser.add_argument("port", type=str, help="serial tcp port")
parser.add_argument("--machine", type=int, default=1, help="Machine number where connect")
parser.add_argument("--system", choices = ['innobus', 'aido'], default = 'innobus', help="Type of Airzone System")
parser.add_argument("--state", choices = ['str', 'raw'], default='str', help="Get the formatted state, or the raw machine state")
parser.set_defaults(func=action)

args = parser.parse_args()
args.func(args)
