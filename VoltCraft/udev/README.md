
### creating device specific identifiers with udev

Everything is explained in the three files in this folder.
To set everything up do:

    cp 99-strawlab-voltcraft.rules /etc/udev/rules.d/
    cp voltcraft.conf /etc/
    cp vcpps_namer.py /usr/bin/
    chmod +x /usr/bin/vcpps_namer.py
    
