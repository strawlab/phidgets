#!/usr/bin/env python
#
# Author:      Andreas Poehlmann
# Last Change: 2012-12-14
#
#***************************************************
#
# This script gets called when the udev-rule in:
# >>> /etc/udev/rules.d/99-strawlab-voltcraft.rules
# matches a usb device.
# 
# udev calls this script with the /dev/ filename as 
# the first commandline parameter 
#
# depended on the settings in /etc/voltcraft.conf
# the script returns the new identifier as a string.
#
# udev then creates a symbolic link with that name.
# The device can then be accessed via /dev/'foo'
#
# 
# To distiguish different Volcraft Powersupplies
# the last (of 3) internally stored voltage and 
# current values are used as a identifier.
#
#***************************************************

import VoltCraft.pps
import sys

# Just in case
if len(sys.argv) == 1:
    exit()

# get device lists
try:
    with open('/etc/voltcraft.conf','r') as f:
        data = f.read()
except:
    print sys.argv[-1]
    exit()

devices = {}
for line in data.split('\n'):
    l = line.strip()
    if not l or l[0] == '#':
        continue
    try:
        name, val0, val1 = l.split()
        devices[(float(val0), float(val1))] = name 
    except:
        continue

# any configuration?
if not devices:
    print sys.argv[-1]
    exit()

# get identifier from device
try:
    p = VoltCraft.pps.PPS("/dev/%s" % sys.argv[-1], reset=False)
    _, _, t = p.load_presets()
    name = devices[t]
    print name
except:
    print sys.argv[-1]

