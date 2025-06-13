# src/transport_layer.py

import random
import time
import threading
from collections import deque
from enum import Enum

class PortType(Enum):
    WELL_KNOWN = "well_known"  # 0-1023
    REGISTERED = "registered"  # 1024-49151
    EPHEMERAL = "ephemeral"   # 49152-65535

class PortManager:
    """Manages port number allocation and assignment"""
    
    def __init__(self):
        self.well_known_ports = {
            20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET",
            25: "SMTP", 53: "DNS", 67: "DHCP", 68: "DHCP",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
            993: "IMAPS", 995: "POP3S"
        }
        self.allocated_ports = set()
        self.ephemeral_start = 49152
        self.ephemeral_end = 65535
        self.current_ephemeral = self.ephemeral_start
        
    def get_well_known_port(self, service):
        """Get well-known port for a service"""
        for port, svc in self.well_known_ports.items():
            if svc.upper() == service.upper():
                return port
        return None
    
    def allocate_ephemeral_port(self):
        """Allocate an ephemeral port"""
        while self.current_ephemeral <= self.ephemeral_end:
            if self.current_ephemeral not in self.allocated_ports:
                port = self.current_ephemeral
                self.allocated_ports.add(port)
                self.current_ephemeral += 1
                return port
            self.current_ephemeral += 1
        raise Exception("No available ephemeral ports")
    
    def release_port(self, port):
        """Release an allocated port"""
        if port in self.allocated_ports:
            self.allocated_ports.remove(port)
    
    def is_port_available(self, port):
        """Check if a port is available"""
        return port not in self.allocated_ports

class TransportSegment:
    """Transport layer segment/datagram"""
    
    def __init__(self, src_port, dest_port, data, protocol="TCP", seq_num=0, ack_num=0, flags=None):
        self.src_port = src_port
        self.dest_port = dest_port
        self.data = data
        self.protocol = protocol
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.flags = flags or {}
        self.timestamp = time.time()
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self):
        """Simple checksum calculation"""
        data_str = str(self.data) + str(self.src_port) + str(self.dest_port)
        return sum(ord(c) for c in data_str) % 65536
    
    def verify_checksum(self):
        """Verify segment integrity"""
        return self.checksum == self._calculate_checksum()
    
    def __str__(self):
        return f"[{self.protocol}] {self.src_port} -> {self.dest_port}, Seq: {self.seq_num}, Data: {self.data[:50]}..."

class GoBackNProtocol:
    """Go-Back-N sliding window protocol implementation"""
    
    def __init__(self, window_size=4, timeout=2.0):
        self.window_size = window_size
        self.timeout = timeout
        self.send_base = 0
        self.next_seq_num = 0
        self.expected_seq_num = 0
        self.send_buffer = {}
        self.receive_buffer = {}
        self.timers = {}
        
    def send_data(self, socket, data_chunks):
        """Send data using Go-Back-N protocol"""
        print(f"Starting Go-Back-N transmission with window size {self.window_size}")
        
        for i, chunk in enumerate(data_chunks):
            # Wait if window is full
            while self.next_seq_num >= self.send_base + self.window_size:
                print(f"Window full, waiting... (base: {self.send_base}, next: {self.next_seq_num})")
                time.sleep(0.1)
            
            # Create and send segment
            segment = TransportSegment(
                socket.src_port, socket.dest_port, chunk,
                protocol="TCP", seq_num=self.next_seq_num
            )
            
            self.send_buffer[self.next_seq_num] = segment
            socket.send_segment(segment)
            self.receive_ack(segment.seq_num)
            # Start timer for first packet in window
            if self.send_base == self.next_seq_num:
                self._start_timer(socket)
            
            self.next_seq_num += 1
            print(f"Sent packet {segment.seq_num}: {chunk}")
        
        # Wait for all acknowledgments
        while self.send_base < len(data_chunks):
            time.sleep(0.1)
        
        print("Go-Back-N transmission completed")
    
    def receive_ack(self, ack_num):
        """Process received acknowledgment"""
        if ack_num >= self.send_base:
            print(f"Received ACK {ack_num}")
            self.send_base = ack_num + 1
            
            if self.send_base == self.next_seq_num:
                self._stop_timer()
            else:
                self._start_timer(None)  # Restart timer
    
    def receive_data(self, segment):
        """Process received data segment"""
        if segment.seq_num == self.expected_seq_num:
            print(f"Received expected packet {segment.seq_num}")
            self.receive_buffer[segment.seq_num] = segment
            self.expected_seq_num += 1
            return segment.seq_num  # Return ACK number
        else:
            print(f"Received out-of-order packet {segment.seq_num}, expected {self.expected_seq_num}")
            return self.expected_seq_num - 1  # Return last correctly received
    
    def _start_timer(self, socket):
        """Start timeout timer"""
        def timeout_handler():
            time.sleep(self.timeout)
            if socket:
                self._handle_timeout(socket)
        
        timer = threading.Thread(target=timeout_handler)
        timer.daemon = True
        timer.start()
    
    def _stop_timer(self):
        """Stop timeout timer"""
        pass  # Simplified implementation
    
    def _handle_timeout(self, socket):
        """Handle timeout - retransmit all unacknowledged packets"""
        print(f"Timeout occurred, retransmitting from {self.send_base}")
        for seq_num in range(self.send_base, self.next_seq_num):
            if seq_num in self.send_buffer:
                socket.send_segment(self.send_buffer[seq_num])
                print(f"Retransmitted packet {seq_num}")

class SelectiveRepeatProtocol:
    """Selective Repeat sliding window protocol implementation"""
    
    def __init__(self, window_size=4, timeout=2.0):
        self.window_size = window_size
        self.timeout = timeout
        self.send_base = 0
        self.next_seq_num = 0
        self.rcv_base = 0
        self.send_buffer = {}
        self.receive_buffer = {}
        self.acked = set()
        
    def send_data(self, socket, data_chunks):
        """Send data using Selective Repeat protocol"""
        print(f"Starting Selective Repeat transmission with window size {self.window_size}")
        
        for i, chunk in enumerate(data_chunks):
            # Wait if window is full
            while self.next_seq_num >= self.send_base + self.window_size:
                time.sleep(0.1)
            
            segment = TransportSegment(
                socket.src_port, socket.dest_port, chunk,
                protocol="TCP", seq_num=self.next_seq_num
            )
            
            self.send_buffer[self.next_seq_num] = segment
            socket.send_segment(segment)
            self.receive_ack(segment.seq_num)
            self.next_seq_num += 1
            print(f"Sent packet {segment.seq_num}: {chunk}")
        
        # Wait for all acknowledgments
        while len(self.acked) < len(data_chunks):
            time.sleep(0.1)
        
        print("Selective Repeat transmission completed")
    
    def receive_ack(self, ack_num):
        """Process received acknowledgment"""
        if ack_num not in self.acked:
            print(f"Received ACK {ack_num}")
            self.acked.add(ack_num)
            
            # Slide window if base packet is acknowledged
            while self.send_base in self.acked:
                self.send_base += 1
    
    def receive_data(self, segment):
        """Process received data segment"""
        seq_num = segment.seq_num
        
        if self.rcv_base <= seq_num < self.rcv_base + self.window_size:
            print(f"Received packet {seq_num} within window")
            self.receive_buffer[seq_num] = segment
            
            # Deliver in-order packets
            while self.rcv_base in self.receive_buffer:
                del self.receive_buffer[self.rcv_base]
                self.rcv_base += 1
            
            return seq_num  # Send ACK for this packet
        else:
            print(f"Received packet {seq_num} outside window")
            return seq_num if seq_num < self.rcv_base else None

class Socket:
    """Base socket class"""
    
    def __init__(self, socket_type, port_manager):
        self.socket_type = socket_type
        self.port_manager = port_manager
        self.src_port = None
        self.dest_port = None
        self.dest_address = None
        self.state = "CLOSED"
        self.send_queue = deque()
        self.receive_queue = deque()
        
    def bind(self, port):
        """Bind socket to a port"""
        if self.port_manager.is_port_available(port):
            self.src_port = port
            self.port_manager.allocated_ports.add(port)
            self.state = "BOUND"
            print(f"Socket bound to port {port}")
        else:
            raise Exception(f"Port {port} is already in use")
    
    def connect(self, dest_address, dest_port):
        """Connect to remote address and port"""
        self.dest_address = dest_address
        self.dest_port = dest_port
        
        if not self.src_port:
            self.src_port = self.port_manager.allocate_ephemeral_port()
        
        self.state = "CONNECTED"
        print(f"Connected to {dest_address}:{dest_port} from port {self.src_port}")
    
    def close(self):
        """Close socket and release port"""
        if self.src_port:
            self.port_manager.release_port(self.src_port)
        self.state = "CLOSED"

class TCPSocket(Socket):
    """TCP socket implementation"""
    
    def __init__(self, port_manager):
        super().__init__("TCP", port_manager)
        self.sliding_window = GoBackNProtocol()  # Default to Go-Back-N
        self.connection_established = False
        
    def set_sliding_window_protocol(self, protocol_type="go_back_n", window_size=4):
        """Set sliding window protocol"""
        if protocol_type.lower() == "go_back_n":
            self.sliding_window = GoBackNProtocol(window_size)
        elif protocol_type.lower() == "selective_repeat":
            self.sliding_window = SelectiveRepeatProtocol(window_size)
        else:
            raise ValueError("Invalid protocol type. Use 'go_back_n' or 'selective_repeat'")
    
    def send(self, data):
        """Send data using TCP with sliding window"""
        if self.state != "CONNECTED":
            raise Exception("Socket not connected")
        
        # Split data into chunks for sliding window
        chunk_size = 50  # Simulate MSS (Maximum Segment Size)
        data_chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        
        print(f"Sending {len(data_chunks)} chunks using TCP with {type(self.sliding_window).__name__}")
        self.sliding_window.send_data(self, data_chunks)
    
    def send_segment(self, segment):
        """Send individual segment"""
        print(f"TCP sending: {segment}")
        # In a real implementation, this would go to the network layer
        
    def listen(self, backlog=5):
        """Listen for incoming connections"""
        if not self.src_port:
            raise Exception("Socket not bound to a port")
        self.state = "LISTENING"
        print(f"TCP socket listening on port {self.src_port}")
    
    def accept(self):
        """Accept incoming connection"""
        # Simplified implementation
        new_socket = TCPSocket(self.port_manager)
        new_socket.src_port = self.src_port
        new_socket.state = "CONNECTED"
        return new_socket

class UDPSocket(Socket):
    """UDP socket implementation"""
    
    def __init__(self, port_manager):
        super().__init__("UDP", port_manager)
    
    def sendto(self, data, address):
        """Send data to specific address"""
        dest_host, dest_port = address
        
        if not self.src_port:
            self.src_port = self.port_manager.allocate_ephemeral_port()
        
        segment = TransportSegment(
            self.src_port, dest_port, data, protocol="UDP"
        )
        
        print(f"UDP sending to {dest_host}:{dest_port}: {segment}")
        # In a real implementation, this would go to the network layer
    
    def recvfrom(self, buffer_size):
        """Receive data from socket"""
        # Simplified implementation
        if self.receive_queue:
            segment = self.receive_queue.popleft()
            return segment.data, (segment.src_port, "remote_host")
        return None, None

class TransportLayer:
    """Transport layer manager"""
    
    def __init__(self):
        self.port_manager = PortManager()
        self.active_sockets = {}
        
    def create_socket(self, socket_type="TCP"):
        """Create a new socket"""
        if socket_type.upper() == "TCP":
            return TCPSocket(self.port_manager)
        elif socket_type.upper() == "UDP":
            return UDPSocket(self.port_manager)
        else:
            raise ValueError("Invalid socket type. Use 'TCP' or 'UDP'")
    
    def get_service_port(self, service_name):
        """Get well-known port for a service"""
        return self.port_manager.get_well_known_port(service_name)
    
    def print_port_allocation(self):
        """Print current port allocation status"""
        print("\n--- Port Allocation Status ---")
        print("Well-known ports:")
        for port, service in self.port_manager.well_known_ports.items():
            status = "ALLOCATED" if port in self.port_manager.allocated_ports else "AVAILABLE"
            print(f"  {port}: {service} ({status})")
        
        print(f"\nAllocated ephemeral ports: {sorted([p for p in self.port_manager.allocated_ports if p >= 49152])}")
        print(f"Next ephemeral port: {self.port_manager.current_ephemeral}")
