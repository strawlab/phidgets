
### creating device specific identifiers with udev

Everything is explained in the three files in this folder.
To set everything up do:

    cp 99-strawlab-voltcraft.rules /etc/udev/rules.d/
    cp voltcraft.conf /etc/
    cp vcpps_namer.py /usr/bin/
    chmod +x /usr/bin/vcpps_namer.py

To set up the powersupply do:

    import VoltCraft.pps
    v = VoltCraft.pps.PPS('/dev/ttyUSBX')
    v.store_presets((V0, C0), (V1, C1), (V2, C2))

where V2 and C2 are the two floats that are used by *vcpps_namer.py* for identification of the device.


