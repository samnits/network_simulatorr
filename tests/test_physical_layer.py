# tests/test_physical_layer.py
from src.physical_layer import EndDevice, Connection

def test_data_transmission():
    device1 = EndDevice("Device1")
    device2 = EndDevice("Device2")
    connection = Connection(device1, device2)

    device1.send_data("Test Message", connection)

if __name__ == "__main__":
    test_data_transmission()
