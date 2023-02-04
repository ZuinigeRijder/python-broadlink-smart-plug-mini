# == python_broadlink_smart_plug_mini_info Author: Zuinige Rijder ===============
"""
Simple Python3 script to get values of broadlink SP mini using python_broadlink library

Example output (MAC addresses are changed):
device: Lader (Broadlink SP3S-EU 0x947a / 192.168.178.234:80 / 32:AA:31:72:62:40)
device: Badkamer (Broadlink SP3S-EU 0x947a / 192.168.178.214:80 / 32:AA:31:72:63:43)
"""
import broadlink

for device in broadlink.xdiscover():
    print(f"device: {device}")
