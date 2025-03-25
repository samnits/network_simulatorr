import random
class Switch:
    def __init__(self, name):
        self.name = name
        self.mac_table = {}

    def connect(self, device, mac_address):
        self.mac_table[mac_address] = device  # Ensure correct mapping
        print(f"{device.name} with MAC {mac_address} connected to {self.name}")

    def forward_frame(self, source_mac, dest_mac, data):
        # Learn the source MAC address
        if source_mac not in self.mac_table:
            print(f"Learning MAC address {source_mac}")
            self.mac_table[source_mac] = self.mac_table.get(source_mac)

        # Forward frame if destination MAC is known
        if dest_mac in self.mac_table and self.mac_table[dest_mac] is not None:
            print(f"Switch forwarding data from {source_mac} to {dest_mac}")
            self.mac_table[dest_mac].receive_data(data)
        else:
            # Broadcast if destination is unknown
            print(f"Broadcasting data since {dest_mac} is unknown")
            for device in self.mac_table.values():
                if device is not None and device.mac_address != source_mac:  # Avoid broadcasting to None
                    device.receive_data(data)


class Bridge:
    def __init__(self, name):
        self.name = name
        self.mac_table = {}

    def connect(self, segment, mac_addresses):
        """ Connect a segment (list of devices) with MAC addresses """
        for mac, device in zip(mac_addresses, segment):
            self.mac_table[mac] = device

    def forward_frame(self, source_mac, dest_mac, data):
        if dest_mac in self.mac_table:
            print(f"{self.name} forwarding data from {source_mac} to {dest_mac}")
            self.mac_table[dest_mac].receive_data(data)
        else:
            print(f"{self.name} does not know {dest_mac}, flooding frame...")
            for device in self.mac_table.values():
                if device.mac_address != source_mac:
                    device.receive_data(data)

class Device:
    def __init__(self, name, mac_address):
        self.name = name
        self.mac_address = mac_address

    def send_data(self, switch, dest_mac, data):
        print(f"{self.name} sending data to {dest_mac}")
        switch.forward_frame(self.mac_address, dest_mac, data)

    def receive_data(self, data):
        print(f"{self.name} received: {data}")

# Error Control (Simple Parity Check)
def parity_check(data):
    ones_count = data.count('1')
    return ones_count % 2 == 0

# Access Control (CSMA/CD Simulation)
def csma_cd(transmitting_device, switch, dest_mac, data):
    if random.random() < 0.2:  # Simulate a collision with 20% probability
        print("Collision detected! Retransmitting...")
        return csma_cd(transmitting_device, switch, dest_mac, data)
    else:
        transmitting_device.send_data(switch, dest_mac, data)

# Sliding Window Protocol
def sliding_window(devices, switch, dest_mac, data, window_size=3):
    print(f"Initiating Sliding Window Protocol with window size: {window_size}")
    total_frames = len(data)
    sent = 0

    while sent < total_frames:
        window_end = min(sent + window_size, total_frames)
        print(f"Sending frames {sent + 1} to {window_end}")

        for i in range(sent, window_end):
            print(f"Frame {i + 1} sent: {data[i]}")
            devices[0].send_data(switch, dest_mac, data[i])

        ack_received = random.choice([True, False])  # Simulating random ACK
        if ack_received:
            print("Acknowledgment received.")
            sent = window_end  # Slide window forward
        else:
            print("No acknowledgment received. Resending frames...")

    print("Sliding Window Protocol completed.")
