# src/simulator.py
import networkx as nx
import matplotlib.pyplot as plt
import random
import time
import ipaddress
import threading

from physical_layer import EndDevice, Hub, Connection
from data_link_layer import Switch, Device, parity_check, csma_cd, sliding_window
from network_layer import Router, NetworkDevice, IPPacket, ARP, RIP, OSPF
from transport_layer import TransportLayer, GoBackNProtocol, SelectiveRepeatProtocol
from application_layer import ApplicationLayer
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

def test_ospf_routing():
    print("\n--- Testing OSPF Dynamic Routing ---")
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
    
    # Create hosts
    host1 = NetworkDevice("Host1", "AA:BB:CC:11:11:11")
    host2 = NetworkDevice("Host2", "AA:BB:CC:22:22:22")
    host3 = NetworkDevice("Host3", "AA:BB:CC:33:33:33")
    host4 = NetworkDevice("Host4", "AA:BB:CC:44:44:44")
    
    network.add_device(host1)
    network.add_device(host2)
    network.add_device(host3)
    network.add_device(host4)
    
    # Configure router interfaces for OSPF topology
    router1.add_interface("eth0", "10.0.1.1/24", "AA:BB:CC:01:01:01")      # Host network
    router1.add_interface("eth1", "10.0.12.1/24", "AA:BB:CC:01:01:02")     # To Router2
    router1.add_interface("eth2", "10.0.13.1/24", "AA:BB:CC:01:01:03")     # To Router3
    
    router2.add_interface("eth0", "10.0.12.2/24", "AA:BB:CC:02:02:01")     # To Router1
    router2.add_interface("eth1", "10.0.2.1/24", "AA:BB:CC:02:02:02")      # Host network
    router2.add_interface("eth2", "10.0.24.1/24", "AA:BB:CC:02:02:03")     # To Router4
    
    router3.add_interface("eth0", "10.0.13.2/24", "AA:BB:CC:03:03:01")     # To Router1
    router3.add_interface("eth1", "10.0.3.1/24", "AA:BB:CC:03:03:02")      # Host network
    router3.add_interface("eth2", "10.0.34.1/24", "AA:BB:CC:03:03:03")     # To Router4
    
    router4.add_interface("eth0", "10.0.24.2/24", "AA:BB:CC:04:04:01")     # To Router2
    router4.add_interface("eth1", "10.0.34.2/24", "AA:BB:CC:04:04:02")     # To Router3
    router4.add_interface("eth2", "10.0.4.1/24", "AA:BB:CC:04:04:03")      # Host network
    
    # Configure hosts
    host1.set_ip("10.0.1.10/24", "10.0.1.1")
    host2.set_ip("10.0.2.10/24", "10.0.2.1")
    host3.set_ip("10.0.3.10/24", "10.0.3.1")
    host4.set_ip("10.0.4.10/24", "10.0.4.1")
    
    # Connect devices to routers
    router1.connect_device("eth0", host1)
    router1.connect_device("eth1", router2)
    router1.connect_device("eth2", router3)
    
    router2.connect_device("eth0", router1)
    router2.connect_device("eth1", host2)
    router2.connect_device("eth2", router4)
    
    router3.connect_device("eth0", router1)
    router3.connect_device("eth1", host3)
    router3.connect_device("eth2", router4)
    
    router4.connect_device("eth0", router2)
    router4.connect_device("eth1", router3)
    router4.connect_device("eth2", host4)
    
    # Initialize OSPF on all routers
    ospf1 = OSPF(router1, area=0)
    ospf2 = OSPF(router2, area=0)
    ospf3 = OSPF(router3, area=0)
    ospf4 = OSPF(router4, area=0)
    
    # Start OSPF protocol
    print("\n--- Starting OSPF Protocol ---")
    ospf1.start(network)
    ospf2.start(network)
    ospf3.start(network)
    ospf4.start(network)
    
    # Display routing tables after OSPF convergence
    print("\n--- Routing Tables After OSPF Convergence ---")
    router1.print_routing_table()
    router2.print_routing_table()
    router3.print_routing_table()
    router4.print_routing_table()
    
    # Test packet forwarding with OSPF routes
    print("\n--- Testing Packet Forwarding with OSPF ---")
    host1.send_packet("10.0.4.10", "Hello from Host1 to Host4 via OSPF routes", network)
    host2.send_packet("10.0.3.10", "Hello from Host2 to Host3 via OSPF routes", network)
    
    # Visualize OSPF network
    devices = [router1, router2, router3, router4, host1, host2, host3, host4]
    connections = [
        (router1, host1), (router1, router2), (router1, router3),
        (router2, host2), (router2, router4),
        (router3, host3), (router3, router4),
        (router4, host4)
    ]
    visualize_network(devices, connections, "Network Layer: OSPF Dynamic Routing")
    
    print("OSPF Dynamic Routing Test Completed")


def test_transport_layer():
    """Test Transport Layer functionalities"""
    print("\n--- Testing Transport Layer ---")
    
    # Initialize transport layer
    transport = TransportLayer()
    
    # Test port management
    print("\n1. Testing Port Management:")
    http_port = transport.get_service_port("HTTP")
    ftp_port = transport.get_service_port("FTP")
    telnet_port = transport.get_service_port("TELNET")
    
    print(f"Well-known ports - HTTP: {http_port}, FTP: {ftp_port}, Telnet: {telnet_port}")
    
    # Create TCP socket
    print("\n2. Testing TCP Socket:")
    tcp_socket = transport.create_socket("TCP")
    tcp_socket.bind(8080)
    tcp_socket.connect("192.168.1.100", 80)
    
    # Test Go-Back-N protocol
    print("\n3. Testing Go-Back-N Protocol:")
    tcp_socket.set_sliding_window_protocol("go_back_n", window_size=3)
    test_data = "This is a test message for Go-Back-N sliding window protocol demonstration."
    tcp_socket.send(test_data)
    
    # Create another socket for Selective Repeat
    print("\n4. Testing Selective Repeat Protocol:")
    tcp_socket2 = transport.create_socket("TCP")
    tcp_socket2.bind(8081)
    tcp_socket2.connect("192.168.1.101", 80)
    tcp_socket2.set_sliding_window_protocol("selective_repeat", window_size=4)
    tcp_socket2.send("Testing Selective Repeat protocol with different data chunks.")
    
    # Test UDP socket
    print("\n5. Testing UDP Socket:")
    udp_socket = transport.create_socket("UDP")
    udp_socket.sendto("UDP test message", ("192.168.1.102", 53))
    
    # Print port allocation status
    transport.print_port_allocation()
    
    # Clean up
    tcp_socket.close()
    tcp_socket2.close()
    
    print("Transport Layer Test Completed")

def test_application_layer():
    """Test Application Layer functionalities"""
    print("\n--- Testing Application Layer ---")
    
    # Initialize layers
    transport = TransportLayer()
    application = ApplicationLayer(transport)
    
    print(f"Available protocols: {application.list_available_protocols()}")
    
    # Test HTTP protocol
    print("\n1. Testing HTTP Protocol:")
    print("Starting HTTP server...")
    http_server = threading.Thread(target=application.start_server, args=("HTTP", 8080))
    http_server.daemon = True
    http_server.start()
    
    time.sleep(1)  # Wait for server to start
    
    print("Starting HTTP client...")
    application.start_client("HTTP", "localhost", 8080)
    
    # Test FTP protocol
    print("\n2. Testing FTP Protocol:")
    print("Starting FTP server...")
    ftp_server = threading.Thread(target=application.start_server, args=("FTP", 2121))
    ftp_server.daemon = True
    ftp_server.start()
    
    time.sleep(1)
    
    print("Starting FTP client...")
    application.start_client("FTP", "localhost", 2121)
    
    # Test Telnet protocol
    print("\n3. Testing Telnet Protocol:")
    print("Starting Telnet server...")
    telnet_server = threading.Thread(target=application.start_server, args=("TELNET", 2323))
    telnet_server.daemon = True
    telnet_server.start()
    
    time.sleep(1)
    
    print("Starting Telnet client...")
    application.start_client("TELNET", "localhost", 2323)
    
    print("Application Layer Test Completed")

def test_encapsulation_decapsulation():
    """Test end-to-end encapsulation and decapsulation"""
    print("\n--- Testing Complete Protocol Stack with Encapsulation ---")
    
    # Create network
    network = Network()
    
    # Initialize all layers
    transport = TransportLayer()
    application = ApplicationLayer(transport)
    
    # Create network devices with all layer support
    print("1. Creating network devices with protocol stack support...")
    
    # Create enhanced network device
    class ProtocolStackDevice:
        def __init__(self, name, mac_address, ip_address):
            self.name = name
            self.mac_address = mac_address
            self.ip_address = ip_address
            self.transport_layer = TransportLayer()
            self.application_layer = ApplicationLayer(self.transport_layer)
            
        def send_application_data(self, dest_ip, protocol, data):
            """Demonstrate encapsulation process"""
            print(f"\n--- Encapsulation Process from {self.name} ---")
            
            # Application Layer
            print(f"5. Application Layer: {protocol} data: '{data}'")
            app_header = f"[{protocol}] "
            app_pdu = app_header + data
            
            # Transport Layer
            src_port = self.transport_layer.port_manager.allocate_ephemeral_port()
            dest_port = self.transport_layer.get_service_port(protocol)
            print(f"4. Transport Layer: Adding TCP header (Src:{src_port}, Dst:{dest_port})")
            transport_header = f"[TCP:{src_port}->{dest_port}] "
            transport_pdu = transport_header + app_pdu
            
            # Network Layer  
            print(f"3. Network Layer: Adding IP header (Src:{self.ip_address}, Dst:{dest_ip})")
            network_header = f"[IP:{self.ip_address}->{dest_ip}] "
            network_pdu = network_header + transport_pdu
            
            # Data Link Layer
            print(f"2. Data Link Layer: Adding Ethernet header (Src:{self.mac_address})")
            datalink_header = f"[ETH:{self.mac_address}] "
            datalink_pdu = datalink_header + network_pdu
            
            # Physical Layer
            print(f"1. Physical Layer: Converting to bits and transmitting")
            physical_bits = f"[BITS] {datalink_pdu}"
            
            print(f"\nFinal transmitted frame: {physical_bits}")
            return physical_bits
        
        def receive_frame(self, frame):
            """Demonstrate decapsulation process"""
            print(f"\n--- Decapsulation Process at {self.name} ---")
            
            # Physical Layer
            print(f"1. Physical Layer: Received bits, converting to frame")
            datalink_frame = frame.replace("[BITS] ", "")
            
            # Data Link Layer
            print(f"2. Data Link Layer: Processing Ethernet header, extracting payload")
            network_packet = datalink_frame.split("[ETH:", 1)[1].split("] ", 1)[1]
            
            # Network Layer
            print(f"3. Network Layer: Processing IP header, extracting payload")
            transport_segment = network_packet.split("[IP:", 1)[1].split("] ", 1)[1]
            
            # Transport Layer
            print(f"4. Transport Layer: Processing TCP header, extracting payload")
            app_data = transport_segment.split("[TCP:", 1)[1].split("] ", 1)[1]
            
            # Application Layer
            print(f"5. Application Layer: Processing application data")
            protocol = app_data.split("] ", 1)[0].replace("[", "")
            final_data = app_data.split("] ", 1)[1]
            
            print(f"Final received data: '{final_data}' via {protocol}")
            return final_data
    
    # Create devices
    client = ProtocolStackDevice("Client", "AA:BB:CC:11:11:11", "192.168.1.10")
    server = ProtocolStackDevice("Server", "AA:BB:CC:22:22:22", "192.168.1.20")
    
    network.add_device(client)
    network.add_device(server)
    
    # Test different application protocols with encapsulation
    test_scenarios = [
        ("HTTP", "GET /index.html HTTP/1.1"),
        ("FTP", "LIST /home/user"),
        ("TELNET", "ls -la"),
        ("SMTP", "MAIL FROM:<test@example.com>")
    ]
    
    for protocol, data in test_scenarios:
        print(f"\n{'='*60}")
        print(f"Testing {protocol} Protocol Stack")
        print(f"{'='*60}")
        
        # Send data with encapsulation
        transmitted_frame = client.send_application_data("192.168.1.20", protocol, data)
        
        # Simulate network transmission delay
        time.sleep(0.5)
        
        # Receive and decapsulate data
        received_data = server.receive_frame(transmitted_frame)
        
        print(f"\nTransmission successful: '{data}' -> '{received_data}'")
        
        # Demonstrate sliding window if TCP
        if protocol in ["HTTP", "FTP", "TELNET", "SMTP"]:
            print(f"\nDemonstrating sliding window for {protocol}:")
            tcp_socket = client.transport_layer.create_socket("TCP")
            tcp_socket.connect("192.168.1.20", client.transport_layer.get_service_port(protocol))
            tcp_socket.set_sliding_window_protocol("go_back_n", window_size=3)
            tcp_socket.send(f"Large data transmission for {protocol}: " + "X" * 200)
            tcp_socket.close()
    
    print("\n" + "="*60)
    print("Complete Protocol Stack Test Completed Successfully!")
    print("="*60)

def main():
    print("Network Simulator")
    print("=================")
    
    # Uncomment the tests you want to run
    # test_physical_layer()
    # test_data_link_layer()
    # test_network_layer()
    # test_ospf_routing()
    test_transport_layer()
    test_application_layer()
    test_encapsulation_decapsulation()

if __name__ == "__main__":
    main()
