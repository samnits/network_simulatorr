# tests/test_data_link_layer.py
from src.data_link_layer import Switch, Device

def test_switch():
    switch = Switch("TestSwitch")
    dev1 = Device("D1", "AA:BB:CC:DD:EE:01")
    dev2 = Device("D2", "AA:BB:CC:DD:EE:02")

    switch.connect(dev1, dev1.mac_address)
    switch.connect(dev2, dev2.mac_address)

    dev1.send_data(switch, dev2.mac_address, "Test Message")

if __name__ == "__main__":
    test_switch()
