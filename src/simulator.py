import networkx as nx
import matplotlib.pyplot as plt
from src.physical_layer import EndDevice, Hub, Connection
from src.data_link_layer import Switch, Device, parity_check, csma_cd, sliding_window

def visualize_network(devices, connections, title="Network Topology"):
    G = nx.Graph()

    for device in devices:
        color = "blue" if isinstance(device, EndDevice) else "red" if isinstance(device, Switch) else "green"
        G.add_node(device.name, color=color)

    for conn in connections:
        G.add_edge(conn[0].name, conn[1].name)

    colors = [G.nodes[n].get("color", "gray") for n in G.nodes]

    plt.figure(figsize=(8, 6))
    nx.draw(G, with_labels=True, node_color=colors, node_size=2000, font_size=10, edge_color="gray")
    plt.title(title)
    plt.show(block=False)  # Non-blocking display
    plt.pause(5)  # Pause for 2 seconds
    plt.close()  # Close the figure to allow the next one to appear

def test_physical_layer():
    print("\n--- Testing Physical Layer ---")
    device1 = EndDevice("Device1")
    device2 = EndDevice("Device2")
    connection = Connection(device1, device2)

    device1.send_data("Hello, Device2!", connection)

    hub = Hub("Hub1")
    device3 = EndDevice("Device3")
    device4 = EndDevice("Device4")
    device5 = EndDevice("Device5")
    device6 = EndDevice("Device6")

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
    try:
        switch = Switch("Switch1")
        devices = [Device(f"D{i+1}", f"AA:BB:CC:DD:EE:0{i+1}") for i in range(5)]

        for device in devices:
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


def test_extended_network():
    print("\n--- Testing Extended Network with Two Star Topologies ---")

    hub1 = Hub("Hub1")
    hub2 = Hub("Hub2")
    switch = Switch("MainSwitch")

    devices1 = [Device(f"H1_D{i+1}", f"AA:BB:CC:DD:11:0{i+1}") for i in range(5)]
    devices2 = [Device(f"H2_D{i+1}", f"AA:BB:CC:DD:22:0{i+1}") for i in range(5)]

    for device in devices1:
        hub1.connect(device)

    for device in devices2:
        hub2.connect(device)

    switch.connect(hub1, "AA:BB:CC:DD:11:00")
    switch.connect(hub2, "AA:BB:CC:DD:22:00")

    print("Devices connected to Hub1:", [d.name for d in hub1.connected_devices])
    print("Devices connected to Hub2:", [d.name for d in hub2.connected_devices])
    print("Switch MAC Table:", switch.mac_table)

    csma_cd(devices1[0], switch, devices2[0].mac_address, "Hello from H1 to H2")

    visualize_network(
        [switch, hub1, hub2] + devices1 + devices2,
        [(device, hub1) for device in devices1] +
        [(device, hub2) for device in devices2] +
        [(hub1, switch), (hub2, switch)],
        "Extended Network: Two Star Topologies with Switch"
    )


def main():
        # test_physical_layer()
        # test_data_link_layer()
        print("Proceeding to Extended Network Test...")
        test_extended_network()
    


if __name__ == "__main__":
    main()


