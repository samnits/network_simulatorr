# src/simulator.py
import networkx as nx
import matplotlib.pyplot as plt
import random
import ipaddress
from src.physical_layer import EndDevice, Hub, Connection
from src.data_link_layer import Switch, Device, parity_check, csma_cd, sliding_window
from src.network_layer import Router, NetworkDevice, IPPacket, ARP, RIP, OSPF

class Network:
    """Network class to manage all devices"""
    def __init__(self):
        self.devices = []
    
    def add_device(self, device):
        self.devices.append(device)
    
    def get_all_devices(self):
        return self.devices

def visualize_network(devices, connections, title="Network Topology"):
    G = nx.Graph()

    for device in devices:
        if isinstance(device, Router):
            color = "red"
            label = f"{device.name}"
            if hasattr(device, 'interfaces'):
                ips = [ip for ip, _ in device.interfaces.values()]
                if ips:
                    label += f"\n{ips[0]}"
        elif isinstance(device, NetworkDevice):
            color = "blue"
            label = f"{device.name}\n{device.ip_address}"
        elif isinstance(device, EndDevice):
            color = "blue"
            label = device.name
        elif isinstance(device, Switch):
            color = "green"
            label = device.name
        else:
            color = "gray"
            label = device.name
        
        G.add_node(device.name, color=color, label=label)

    for conn in connections:
        G.add_edge(conn[0].name, conn[1].name)

    colors = [G.nodes[n].get("color", "gray") for n in G.nodes]
    labels = {n: G.nodes[n].get("label", n) for n in G.nodes}

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)  # For consistent layout
    nx.draw(G, pos, with_labels=False, node_color=colors, node_size=2000, edge_color="gray")
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
    plt.title(title)
    plt.show(block=False)
    plt.pause(5)
    plt.close()

def test_physical_layer():
    print("\n--- Testing Physical Layer ---")
    network = Network()
    
    device1 = EndDevice("Device1")
    device2 = EndDevice("Device2")
    network.add_device(device1)
    network.add_device(device2)
    
    connection = Connection(device1, device2)

    device1.send_data("Hello, Device2!", connection)

    hub = Hub("Hub1")
    device3 = EndDevice("Device3")
    device4 = EndDevice("Device4")
    device5 = EndDevice("Device5")
    device6 = EndDevice("Device6")
    
    network.add_device(hub)
    network.add_device(device3)
    network.add_device(device4)
    network.add_device(device5)
    network.add_device(device6)

    hub.connect(device1)
    hub.connect(device2)
    hub.connect(device3)
    hub.connect(device4)
    hub.connect(device5)
    hub.connect(device6)

    device1.send_data("Hello, everyone!", hub)

    devices = [device1, device2, device3, device4, device5, device6, hub]
    connections = [(device1, hub), (device2, hub), (device3, hub), (device4, hub), (device5, hub), (device6, hub)]
    visualize_network(devices, connections, "Physical Layer: Hub Topology")

def test_data_link_layer():
    print("\n--- Testing Data Link Layer ---")
    network = Network()
    
    try:
        switch = Switch("Switch1")
        network.add_device(switch)
        devices = [Device(f"D{i+1}", f"AA:BB:CC:DD:EE:0{i+1}") for i in range(5)]
        
        for device in devices:
            network.add_device(device)
            switch.connect(device, device.mac_address)

        data = "1010101"  # Example data for parity check
        print("Running Parity Check...")
        if parity_check(data):
            print("Parity Check Passed, attempting CSMA/CD...")
            csma_cd(devices[0], switch, devices[1].mac_address, data)
        else:
            print("Data corrupted! Not sending.")

        print("Running Sliding Window Protocol...")
        sliding_window(devices, switch, devices[2].mac_address, "110011001100", window_size=2)

        visualize_network([switch] + devices, [(device, switch) for device in devices],
                          "Data Link Layer: Switch Topology")
        print("Data Link Layer Test Completed Successfully!")

    except Exception as e:
        print(f"Error during Data Link Layer testing: {e}")

def test_network_layer():
    print("\n--- Testing Network Layer ---")
    network = Network()
    
    # Create routers
    router1 = Router("Router1")
    router2 = Router("Router2")
    router3 = Router("Router3")
    
    network.add_device(router1)
    network.add_device(router2)
    network.add_device(router3)
    
    # Create network devices (hosts)
    host1 = NetworkDevice("Host1", "AA:BB:CC:11:11:11")
    host2 = NetworkDevice("Host2", "AA:BB:CC:22:22:22")
    host3 = NetworkDevice("Host3", "AA:BB:CC:33:33:33")
    host4 = NetworkDevice("Host4", "AA:BB:CC:44:44:44")
    host5 = NetworkDevice("Host5", "AA:BB:CC:55:55:55")
    host6 = NetworkDevice("Host6", "AA:BB:CC:66:66:66")
    
    network.add_device(host1)
    network.add_device(host2)
    network.add_device(host3)
    network.add_device(host4)
    network.add_device(host5)
    network.add_device(host6)
    
    # Configure router interfaces
    router1.add_interface("eth0", "192.168.1.1/24", "AA:BB:CC:01:01:01")
    router1.add_interface("eth1", "10.0.0.1/24", "AA:BB:CC:01:01:02")
    
    router2.add_interface("eth0", "10.0.0.2/24", "AA:BB:CC:02:02:01")
    router2.add_interface("eth1", "192.168.2.1/24", "AA:BB:CC:02:02:02")
    
    router3.add_interface("eth0", "192.168.1.2/24", "AA:BB:CC:03:03:01")
    router3.add_interface("eth1", "192.168.3.1/24", "AA:BB:CC:03:03:02")
    
    # Configure hosts
    host1.set_ip("192.168.1.10/24", "192.168.1.1")
    host2.set_ip("192.168.1.11/24", "192.168.1.1")
    host3.set_ip("192.168.2.10/24", "192.168.2.1")
    host4.set_ip("192.168.2.11/24", "192.168.2.1")
    host5.set_ip("192.168.3.10/24", "192.168.3.1")
    host6.set_ip("192.168.3.11/24", "192.168.3.1")
    
    # Connect devices to routers
    router1.connect_device("eth0", host1)
    router1.connect_device("eth0", host2)
    router1.connect_device("eth1", router2)
    
    router2.connect_device("eth0", router1)
    router2.connect_device("eth1", host3)
    router2.connect_device("eth1", host4)
    
    router3.connect_device("eth0", router1)
    router3.connect_device("eth1", host5)
    router3.connect_device("eth1", host6)
    
    # Add static routes
    router1.add_route("192.168.2.0", "255.255.255.0", "10.0.0.2", "eth1")
    router1.add_route("192.168.3.0", "255.255.255.0", "192.168.1.2", "eth0")
    
    router2.add_route("192.168.1.0", "255.255.255.0", "10.0.0.1", "eth0")
    router2.add_route("192.168.3.0", "255.255.255.0", "10.0.0.1", "eth0")
    
    router3.add_route("192.168.2.0", "255.255.255.0", "192.168.1.1", "eth0")
    router3.add_route("10.0.0.0", "255.255.255.0", "192.168.1.1", "eth0")
    
    # Display routing tables
    router1.print_routing_table()
    router2.print_routing_table()
    router3.print_routing_table()
    
    # Test ARP
    print("\n--- Testing ARP Protocol ---")
    arp = ARP()
    mac = arp.request("192.168.1.10", network)
    print(f"ARP result for 192.168.1.10: {mac}")
    
    # Test packet forwarding
    print("\n--- Testing Packet Forwarding with Static Routing ---")
    # Host1 sends data to Host3 (across routers)
    host1.send_packet("192.168.2.10", "Hello from Host1 to Host3", network)
    
    # Host2 sends data to Host5 (across routers)
    host2.send_packet("192.168.3.10", "Hello from Host2 to Host5", network)
    
    # Visualize network
    devices = [router1, router2, router3, host1, host2, host3, host4, host5, host6]
    connections = [
        (router1, host1), (router1, host2), (router1, router2), (router1, router3),
        (router2, host3), (router2, host4),
        (router3, host5), (router3, host6)
    ]
    visualize_network(devices, connections, "Network Layer: Static Routing")
    
    print("Network Layer Static Routing Test Completed")

def test_dynamic_routing():
    print("\n--- Testing Dynamic Routing (RIP) ---")
    network = Network()
    
    # Create routers
    router1 = Router("Router1")
    router2 = Router("Router2")
    router3 = Router("Router3")
    router4 = Router("Router4")
    
    network.add_device(router1)
    network.add_device(router2)
    network.add_device(router3)
    network.add_device(router4)
    
    # Create network devices (hosts)
    host1 = NetworkDevice("Host1", "AA:BB:CC:11:11:11")
    host2 = NetworkDevice("Host2", "AA:BB:CC:22:22:22")
    
    network.add_device(host1)
    network.add_device(host2)
    
    # Configure router interfaces
    router1.add_interface("eth0", "10.0.1.1/24", "AA:BB:CC:01:01:01")
    router1.add_interface("eth1", "10.0.12.1/24", "AA:BB:CC:01:01:02")
    router1.add_interface("eth2", "10.0.13.1/24", "AA:BB:CC:01:01:03")
    
    router2.add_interface("eth0", "10.0.12.2/24", "AA:BB:CC:02:02:01")
    router2.add_interface("eth1", "10.0.2.1/24", "AA:BB:CC:02:02:02")
    router2.add_interface("eth2", "10.0.24.1/24", "AA:BB:CC:02:02:03")
    
    router3.add_interface("eth0", "10.0.13.3/24", "AA:BB:CC:03:03:01")
    router3.add_interface("eth1", "10.0.3.1/24", "AA:BB:CC:03:03:02")
    router3.add_interface("eth2", "10.0.34.1/24", "AA:BB:CC:03:03:03")
    
    router4.add_interface("eth0", "10.0.24.4/24", "AA:BB:CC:04:04:01")
    router4.add_interface("eth1", "10.0.34.4/24", "AA:BB:CC:04:04:02")
    router4.add_interface("eth2", "10.0.4.1/24", "AA:BB:CC:04:04:03")
    
    # Configure hosts
    host1.set_ip("10.0.1.10/24", "10.0.1.1")
    host2.set_ip("10.0.4.10/24", "10.0.4.1")
    
    # Connect devices to routers
    router1.connect_device("eth0", host1)
    router1.connect_device("eth1", router2)
    router1.connect_device("eth2", router3)
    
    router2.connect_device("eth0", router1)
    router2.connect_device("eth2", router4)
    
    router3.connect_device("eth0", router1)
    router3.connect_device("eth2", router4)
    
    router4.connect_device("eth0", router2)
    router4.connect_device("eth1", router3)
    router4.connect_device("eth2", host2)
    
    # Initialize RIP on routers
    router1_rip = RIP(router1)
    router2_rip = RIP(router2)
    router3_rip = RIP(router3)
    router4_rip = RIP(router4)
    
    # Start RIP protocol
    router1_rip.start(network)
    router2_rip.start(network)
    router3_rip.start(network)
    router4_rip.start(network)
    
    # Simulate route exchange (would happen over time in a real network)
    # First round - directly connected networks
    print("\n--- Round 1: Initial RIP Updates ---")
    router2.process_rip_update(router1.name, "10.0.1.0", "255.255.255.0", 1)
    router3.process_rip_update(router1.name, "10.0.1.0", "255.255.255.0", 1)
    
    router1.process_rip_update(router2.name, "10.0.2.0", "255.255.255.0", 1)
    router1.process_rip_update(router2.name, "10.0.24.0", "255.255.255.0", 1)
    
    router1.process_rip_update(router3.name, "10.0.3.0", "255.255.255.0", 1)
    router1.process_rip_update(router3.name, "10.0.34.0", "255.255.255.0", 1)
    
    router2.process_rip_update(router4.name, "10.0.4.0", "255.255.255.0", 1)
    router3.process_rip_update(router4.name, "10.0.4.0", "255.255.255.0", 1)
    
    # Second round - propagate routes
    print("\n--- Round 2: Propagating Routes ---")
    router3.process_rip_update(router1.name, "10.0.2.0", "255.255.255.0", 2)
    router3.process_rip_update(router1.name, "10.0.24.0", "255.255.255.0", 2)
    
    router2.process_rip_update(router1.name, "10.0.3.0", "255.255.255.0", 2)
    router2.process_rip_update(router1.name, "10.0.34.0", "255.255.255.0", 2)
    
    router1.process_rip_update(router2.name, "10.0.4.0", "255.255.255.0", 2)
    router1.process_rip_update(router3.name, "10.0.4.0", "255.255.255.0", 2)
    
    # Display routing tables
    router1.print_routing_table()
    router2.print_routing_table()
    router3.print_routing_table()
    router4.print_routing_table()
    
    # Test packet forwarding
    print("\n--- Testing Packet Forwarding with RIP ---")
    # Host1 sends data to Host2 (across multiple routers)
    host1.send_packet("10.0.4.10", "Hello from Host1 to Host2 via RIP routes", network)
    
    # Visualize network
    devices = [router1, router2, router3, router4, host1, host2]
    connections = [
        (router1, host1), (router1, router2), (router1, router3),
        (router2, router4), (router3, router4), (router4, host2)
    ]
    visualize_network(devices, connections, "Network Layer: RIP Dynamic Routing")
    
    print("Network Layer RIP Dynamic Routing Test Completed")

def main():
    print("Network Simulator")
    print("=================")
    
    # Uncomment the tests you want to run
    # test_physical_layer()
    # test_data_link_layer()
    test_network_layer()
    test_dynamic_routing()

if __name__ == "__main__":
    main()
