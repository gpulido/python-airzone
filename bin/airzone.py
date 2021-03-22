#!/usr/bin/env python
import airzone
import sys
import argparse
from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("python-airzone")
except PackageNotFoundError:
    # package is not installed
    pass


def action(args):
    print(args.machine)
    m = airzone.airzone_factory(args.serial, args.port, args.machine, args.system)
    print(str(m))
    
    
parser = argparse.ArgumentParser(prog='airzone')
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
parser.add_argument("serial", type=str, help="serial device")
parser.add_argument("port", type=str, help="serial tcp port")
parser.add_argument("--machine", type=int, default=1, help="Machine number where connect")
parser.add_argument("--system", choices = ['innobus', 'aido'], default = 'innobus', help="Type of Airzone System")
parser.set_defaults(func=action)

args = parser.parse_args()
args.func(args)