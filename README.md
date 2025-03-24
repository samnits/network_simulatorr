# Network Simulator Project

This project implements a network simulator with the following features:
- **Physical Layer:** Handles data transmission between devices through direct connections and hubs.
- **Data Link Layer:** Implements MAC addressing, error detection, access control protocols, and sliding window-based flow control.

## Project Structure
```
├── docs/                     # Documentation files
├── src/                      # Source code
│   ├── __init__.py           # Initialization for the src package
│   ├── data_link_layer.py    # Data Link Layer implementation
│   ├── extended.py           # Extended functionalities (if any)
│   ├── physical_layer.py     # Physical Layer implementation
│   ├── simulator.py          # Main simulator orchestrating the flow
│   └── tempCodeRunnerFile.py # Temporary file (can be ignored)
├── tests/                    # Test cases for validation
│   ├── test_data_link_layer.py
│   └── test_physical_layer.py
├── venv/                     # Virtual environment
├── main.py                   # Entry point for running the simulator
├── README.md                 # Project documentation (this file)
└── requirements.txt          # Dependencies
```

## How the Code Works
### Entry Point: `main.py`
- Initializes the simulator from `simulator.py`.
- Runs test cases for both layers to validate functionality.

### Physical Layer (`physical_layer.py`)
- **Devices and Hubs:** Defines devices that send/receive data and hubs that broadcast data.
- **Transmission:** Handles data transmission between devices through hubs.

### Data Link Layer (`data_link_layer.py`)
- **MAC Addressing:** Assigns and identifies devices using MAC addresses.
- **Error Detection:** Implements parity check for data integrity.
- **Access Control:** Uses CSMA/CD to handle collisions.
- **Flow Control:** Uses a Sliding Window Protocol for reliable data transfer.

### Simulator (`simulator.py`)
- Orchestrates the overall data transmission flow.
- Coordinates data transfer across both layers.

### Extended Functionalities (`extended.py`)
- Can include additional protocols or enhancements beyond initial requirements.

## Running the Project
1. Install dependencies:
```
pip install -r requirements.txt
```
2. Activate the virtual environment:
```
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate  # On Windows
```
3. Run the simulator:
```
python main.py
```
4. Run test cases:
```
pytest tests/
```

## Example Output
- Physical Layer: Simulates data transmission and collision domains.
- Data Link Layer: Demonstrates MAC addressing, parity check, CSMA/CD, and Sliding Window Protocol.

## Future Improvements
- Expand the protocol stack to include network and transport layers.
- Implement advanced error detection and correction.

## License
This project is for educational purposes only.

