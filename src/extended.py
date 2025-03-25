import random
import networkx as nx
import matplotlib.pyplot as plt
from src.physical_layer import Hub, Connection
from src.data_link_layer import Switch, Device, parity_check, csma_cd, sliding_window

# Visualization function for network topology
def visualize_network(devices, connections, title="Network Topology"):
    G = nx.Graph()

    # Assign colors based on device types (Device - blue, Hub - green, Switch - red)
    for device in devices:
        if isinstance(device, Hub):
            color = "green"
        elif isinstance(device, Switch):
            color = "red"
        else:
            color = "blue"
        G.add_node(device.name, color=color)

    # Add edges for each connection (now explicitly using device1 and device2)
    for conn in connections:
        G.add_edge(conn.device1.name, conn.device2.name)

    # Set the color of each node
    colors = [G.nodes[n].get("color", "gray") for n in G.nodes]

    plt.figure(figsize=(8, 6))
    nx.draw(G, with_labels=True, node_color=colors, node_size=2000, font_size=10, edge_color="gray")
    plt.title(title)
    plt.show(block=False)  # Non-blocking display
    plt.pause(5)  # Pause for 2 seconds
    plt.close()  # Close the figure to allow the next one to appear

def test_extended_network():
    print("\n--- Testing Extended Network with Two Star Topologies ---")

    # Create two hubs
    hub1 = Hub("Hub1")
    hub2 = Hub("Hub2")
    
    # Create a switch to connect the two hubs
    switch = Switch("MainSwitch")

    
    # Create five end devices for each hub using the Device class
    devices1 = [Device(f"H1_D{i+1}", f"00:11:22:31:{1}{i+1:02}") for i in range(5)]  # Hub 1: 31
    devices2 = [Device(f"H2_D{i+1}", f"00:11:22:32:{2}{i+1:02}") for i in range(5)]  # Hub 2: 32


    # Manually add devices to the switch MAC address table
    for device in devices1:
       switch.mac_table[device.mac_address] = device  # Store Device object, not hub name

    for device in devices2: 
       switch.mac_table[device.mac_address] = device  # Store Device object, not hub name


    # Connect devices to their respective hubs
    for device in devices1:
        hub1.connect(device)
    
    for device in devices2:
        hub2.connect(device)

    # Now connect the two hubs to the switch
    connection_hub1_switch = Connection(hub1, switch)
    connection_hub2_switch = Connection(hub2, switch)

    # Add connections to the connection list
    connections = []
    for device1 in devices1:
        connections.append(Connection(device1, hub1))
    for device2 in devices2:
        connections.append(Connection(device2, hub2))
    
    connections.append(connection_hub1_switch)
    connections.append(connection_hub2_switch)

  


    print("\n--- Sending Actual Data After Learning Phase ---")
    # **Step 2:** Simulate data transmission from devices in both hubs
    for device in devices1:
        device.send_data(switch, devices2[0].mac_address, f"Data from {device.name}")

    for device in devices2:
        device.send_data(switch, devices1[0].mac_address, f"Data from {device.name}")

    # Calculate and report broadcast and collision domains
    broadcast_domains = 2  # One for each hub, plus switch creates a larger broadcast domain
    collision_domains = 2 + len(devices1) + len(devices2)  # One for each hub and each end device connected to a switch
    
    # Simulate CSMA/CD communication
    print("\n--- Simulating CSMA/CD Communication ---")
    csma_cd(devices1[0], switch, devices2[0].mac_address, "Hello from H1 to H2")

    print(f"\nTotal Broadcast Domains: {broadcast_domains}")
    print(f"Total Collision Domains: {collision_domains}")

    # Visualize the network
    visualize_network(
        [switch, hub1, hub2] + devices1 + devices2,
        connections,
        "Extended Network: Two Star Topologies with Hubs and Switch"
    )


# Main function to run the test
def main():
    test_extended_network()

if __name__ == "__main__":
    main()
