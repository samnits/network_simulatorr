import random
import networkx as nx
import matplotlib.pyplot as plt
from src.physical_layer import EndDevice, Hub, Connection
# Remove these since you are using the physical layer definitions
from src.data_link_layer import Switch, Device, parity_check, csma_cd, sliding_window

# Visualization function for network topology
def visualize_network(devices, connections, title="Network Topology"):
    G = nx.Graph()

    # Assign colors based on device types (EndDevice - blue, Hub - green)
    for device in devices:
        color = "blue" if isinstance(device, EndDevice) else "green"
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

    # Create five end devices for each hub
    devices1 = [EndDevice(f"H1_D{i+1}") for i in range(5)]
    devices2 = [EndDevice(f"H2_D{i+1}") for i in range(5)]

    # Connect devices to their respective hubs
    for device in devices1:
        hub1.connect(device)
    
    for device in devices2:
        hub2.connect(device)

    # Now connect the two hubs to the switch
    # Connect Hub1 to the Switch
    connection_hub1_switch = Connection(hub1, switch)
    # Connect Hub2 to the Switch
    connection_hub2_switch = Connection(hub2, switch)

    # Add connections to the connection list
    connections = []
    for device1 in devices1:
        connection = Connection(device1, hub1)
        connections.append(connection)
    for device2 in devices2:
        connection = Connection(device2, hub2)
        connections.append(connection)
    
    # Add connections between hubs and the switch
    connections.append(connection_hub1_switch)
    connections.append(connection_hub2_switch)

    # Simulate data transmission from devices in both hubs
    for device in devices1:
        device.send_data(f"Data from {device.name}", hub1)
    for device in devices2:
        device.send_data(f"Data from {device.name}", hub2)

    # Calculate and report broadcast and collision domains
    broadcast_domains = 2  # One for each hub, plus switch creates a larger broadcast domain
    collision_domains = 2 + len(devices1) + len(devices2)  # One for each hub and each end device connected to a switch

    print(f"\nTotal Broadcast Domains: {broadcast_domains}")
    print(f"Total Collision Domains: {collision_domains}")

    # Visualize the network
    visualize_network(
        [switch, hub1, hub2] + devices1 + devices2,
        connections,  # Use the updated connections list
        "Extended Network: Two Star Topologies with Hubs and Switch"
    )

# Main function to run the test
def main():
    test_extended_network()

if __name__ == "__main__":
    main()
