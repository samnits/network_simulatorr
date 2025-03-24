# src/physical_layer.py
import random

class EndDevice:
    def __init__(self, name):
        self.name = name

    def send_data(self, data, connection):
        print(f"{self.name} sending data: {data}")
        connection.transmit(self, data)

    def receive_data(self, data):
        print(f"{self.name} received data: {data}")

class Hub:
    def __init__(self, name):
        self.name = name
        self.devices = []

    def connect(self, device):
        self.devices.append(device)

    def transmit(self, sender, data):
        print(f"{self.name} broadcasting data...")
        for device in self.devices:
            if device != sender:
                device.receive_data(data)

class Connection:
    def __init__(self, device1, device2):
        self.device1 = device1
        self.device2 = device2

    def transmit(self, sender, data):
        receiver = self.device1 if sender == self.device2 else self.device2
        receiver.receive_data(data)