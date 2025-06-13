# src/application_layer.py

import time
import socket
import threading
import random
from abc import ABC, abstractmethod

class ApplicationProtocol(ABC):
    """Base class for application layer protocols"""
    
    def __init__(self, transport_layer):
        self.transport_layer = transport_layer
        self.socket = None
        
    @abstractmethod
    def start_server(self, port):
        """Start server on specified port"""
        pass
    
    @abstractmethod
    def start_client(self, server_address, server_port):
        """Start client connecting to server"""
        pass

class HTTPProtocol(ApplicationProtocol):
    """HTTP protocol implementation"""
    
    def __init__(self, transport_layer):
        super().__init__(transport_layer)
        self.default_port = self.transport_layer.get_service_port("HTTP")  # Port 80
        
    def start_server(self, port=None):
        """Start HTTP server"""
        port = port or self.default_port
        self.socket = self.transport_layer.create_socket("TCP")
        self.socket.bind(port)
        self.socket.listen()
        
        print(f"HTTP Server started on port {port}")
        return self._run_server()
    
    def _run_server(self):
        """Run HTTP server loop"""
        while True:
            try:
                client_socket = self.socket.accept()
                print("HTTP: Client connected")
                
                # Simulate receiving HTTP request
                request = "GET /index.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
                print(f"HTTP Server received: {request.strip()}")
                
                # Send HTTP response
                response = self._create_http_response("Welcome to HTTP Server!")
                client_socket.send(response)
                print("HTTP Server sent response")
                
                client_socket.close()
                break  # For simulation purposes
                
            except Exception as e:
                print(f"HTTP Server error: {e}")
                break
    
    def start_client(self, server_address, server_port=None):
        """Start HTTP client"""
        server_port = server_port or self.default_port
        self.socket = self.transport_layer.create_socket("TCP")
        self.socket.connect(server_address, server_port)
        
        print(f"HTTP Client connected to {server_address}:{server_port}")
        
        # Send HTTP GET request
        request = self._create_http_request("GET", "/index.html")
        self.socket.send(request)
        print(f"HTTP Client sent: {request.strip()}")
        
        # Simulate receiving response
        response = "HTTP/1.1 200 OK\r\nContent-Length: 25\r\n\r\nWelcome to HTTP Server!"
        print(f"HTTP Client received: {response.strip()}")
        
        self.socket.close()
    
    def _create_http_request(self, method, path, host="localhost"):
        """Create HTTP request"""
        return f"{method} {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
    
    def _create_http_response(self, content):
        """Create HTTP response"""
        content_length = len(content)
        return f"HTTP/1.1 200 OK\r\nContent-Length: {content_length}\r\nConnection: close\r\n\r\n{content}"

class FTPProtocol(ApplicationProtocol):
    """FTP protocol implementation"""
    
    def __init__(self, transport_layer):
        super().__init__(transport_layer)
        self.control_port = self.transport_layer.get_service_port("FTP")  # Port 21
        self.data_port = self.transport_layer.get_service_port("FTP-DATA")  # Port 20
        
    def start_server(self, port=None):
        """Start FTP server"""
        port = port or self.control_port
        self.socket = self.transport_layer.create_socket("TCP")
        self.socket.bind(port)
        self.socket.listen()
        
        print(f"FTP Server started on port {port}")
        return self._run_server()
    
    def _run_server(self):
        """Run FTP server loop"""
        try:
            client_socket = self.socket.accept()
            print("FTP: Client connected")
            
            # Send welcome message
            welcome = "220 Welcome to FTP Server\r\n"
            client_socket.send(welcome)
            print(f"FTP Server sent: {welcome.strip()}")
            
            # Simulate USER command
            user_cmd = "USER anonymous\r\n"
            print(f"FTP Server received: {user_cmd.strip()}")
            
            user_response = "331 User name okay, need password\r\n"
            client_socket.send(user_response)
            print(f"FTP Server sent: {user_response.strip()}")
            
            # Simulate PASS command
            pass_cmd = "PASS anonymous@example.com\r\n"
            print(f"FTP Server received: {pass_cmd.strip()}")
            
            pass_response = "230 User logged in, proceed\r\n"
            client_socket.send(pass_response)
            print(f"FTP Server sent: {pass_response.strip()}")
            
            # Simulate LIST command
            list_cmd = "LIST\r\n"
            print(f"FTP Server received: {list_cmd.strip()}")
            
            list_response = "150 Opening data connection for directory listing\r\n"
            client_socket.send(list_response)
            
            # Simulate file listing
            file_list = "-rw-r--r-- 1 user user 1234 Jan 01 12:00 file1.txt\r\n-rw-r--r-- 1 user user 5678 Jan 01 12:01 file2.txt\r\n"
            client_socket.send(file_list)
            
            list_complete = "226 Directory listing complete\r\n"
            client_socket.send(list_complete)
            print("FTP Server completed directory listing")
            
            client_socket.close()
            
        except Exception as e:
            print(f"FTP Server error: {e}")
    
    def start_client(self, server_address, server_port=None):
        """Start FTP client"""
        server_port = server_port or self.control_port
        self.socket = self.transport_layer.create_socket("TCP")
        self.socket.connect(server_address, server_port)
        
        print(f"FTP Client connected to {server_address}:{server_port}")
        
        # Simulate FTP session
        print("FTP Client received: 220 Welcome to FTP Server")
        
        self.socket.send("USER anonymous\r\n")
        print("FTP Client sent: USER anonymous")
        print("FTP Client received: 331 User name okay, need password")
        
        self.socket.send("PASS anonymous@example.com\r\n")
        print("FTP Client sent: PASS anonymous@example.com")
        print("FTP Client received: 230 User logged in, proceed")
        
        self.socket.send("LIST\r\n")
        print("FTP Client sent: LIST")
        print("FTP Client received directory listing")
        
        self.socket.close()

class TelnetProtocol(ApplicationProtocol):
    """Telnet protocol implementation"""
    
    def __init__(self, transport_layer):
        super().__init__(transport_layer)
        self.default_port = self.transport_layer.get_service_port("TELNET")  # Port 23
        
    def start_server(self, port=None):
        """Start Telnet server"""
        port = port or self.default_port
        self.socket = self.transport_layer.create_socket("TCP")
        self.socket.bind(port)
        self.socket.listen()
        
        print(f"Telnet Server started on port {port}")
        return self._run_server()
    
    def _run_server(self):
        """Run Telnet server loop"""
        try:
            client_socket = self.socket.accept()
            print("Telnet: Client connected")
            
            # Send welcome message
            welcome = "Welcome to Telnet Server\r\nLogin: "
            client_socket.send(welcome)
            print("Telnet Server sent welcome message")
            
            # Simulate login process
            username = "admin"
            print(f"Telnet Server received username: {username}")
            
            password_prompt = "Password: "
            client_socket.send(password_prompt)
            
            password = "password123"
            print(f"Telnet Server received password: {'*' * len(password)}")
            
            login_success = "Login successful!\r\n$ "
            client_socket.send(login_success)
            print("Telnet Server: User logged in")
            
            # Simulate command execution
            command = "ls -la"
            print(f"Telnet Server received command: {command}")
            
            command_output = "total 8\r\ndrwxr-xr-x 2 user user 4096 Jan 01 12:00 .\r\ndrwxr-xr-x 3 user user 4096 Jan 01 12:00 ..\r\n-rw-r--r-- 1 user user   20 Jan 01 12:00 file.txt\r\n$ "
            client_socket.send(command_output)
            print("Telnet Server sent command output")
            
            client_socket.close()
            
        except Exception as e:
            print(f"Telnet Server error: {e}")
    
    def start_client(self, server_address, server_port=None):
        """Start Telnet client"""
        server_port = server_port or self.default_port
        self.socket = self.transport_layer.create_socket("TCP")
        self.socket.connect(server_address, server_port)
        
        print(f"Telnet Client connected to {server_address}:{server_port}")
        
        # Simulate Telnet session
        print("Telnet Client received: Welcome to Telnet Server")
        
        self.socket.send("admin\r\n")
        print("Telnet Client sent username: admin")
        
        self.socket.send("password123\r\n")
        print("Telnet Client sent password")
        print("Telnet Client received: Login successful!")
        
        self.socket.send("ls -la\r\n")
        print("Telnet Client sent command: ls -la")
        print("Telnet Client received command output")
        
        self.socket.close()

class SMTPProtocol(ApplicationProtocol):
    """SMTP protocol implementation"""
    
    def __init__(self, transport_layer):
        super().__init__(transport_layer)
        self.default_port = self.transport_layer.get_service_port("SMTP")  # Port 25
        
    def start_server(self, port=None):
        """Start SMTP server"""
        port = port or self.default_port
        self.socket = self.transport_layer.create_socket("TCP")
        self.socket.bind(port)
        self.socket.listen()
        
        print(f"SMTP Server started on port {port}")
        return self._run_server()
    
    def _run_server(self):
        """Run SMTP server loop"""
        try:
            client_socket = self.socket.accept()
            print("SMTP: Client connected")
            
            # Send greeting
            greeting = "220 mail.example.com SMTP Service ready\r\n"
            client_socket.send(greeting)
            print(f"SMTP Server sent: {greeting.strip()}")
            
            # EHLO/HELO
            helo_response = "250 Hello client.example.com\r\n"
            client_socket.send(helo_response)
            print("SMTP Server responded to HELO")
            
            # MAIL FROM
            mail_from_response = "250 Sender OK\r\n"
            client_socket.send(mail_from_response)
            print("SMTP Server accepted sender")
            
            # RCPT TO
            rcpt_to_response = "250 Recipient OK\r\n"
            client_socket.send(rcpt_to_response)
            print("SMTP Server accepted recipient")
            
            # DATA
            data_response = "354 Start mail input; end with <CRLF>.<CRLF>\r\n"
            client_socket.send(data_response)
            print("SMTP Server ready for message data")
            
            # End of message
            end_response = "250 Message accepted for delivery\r\n"
            client_socket.send(end_response)
            print("SMTP Server accepted message")
            
            client_socket.close()
            
        except Exception as e:
            print(f"SMTP Server error: {e}")
    
    def start_client(self, server_address, server_port=None):
        """Start SMTP client"""
        server_port = server_port or self.default_port
        self.socket = self.transport_layer.create_socket("TCP")
        self.socket.connect(server_address, server_port)
        
        print(f"SMTP Client connected to {server_address}:{server_port}")
        
        # Simulate SMTP session
        print("SMTP Client received: 220 mail.example.com SMTP Service ready")
        
        self.socket.send("HELO client.example.com\r\n")
        print("SMTP Client sent: HELO client.example.com")
        
        self.socket.send("MAIL FROM:<sender@example.com>\r\n")
        print("SMTP Client sent: MAIL FROM:<sender@example.com>")
        
        self.socket.send("RCPT TO:<recipient@example.com>\r\n")
        print("SMTP Client sent: RCPT TO:<recipient@example.com>")
        
        self.socket.send("DATA\r\n")
        print("SMTP Client sent: DATA")
        
        message = "Subject: Test Email\r\n\r\nThis is a test email message.\r\n.\r\n"
        self.socket.send(message)
        print("SMTP Client sent email message")
        
        self.socket.close()

class ApplicationLayer:
    """Application layer manager"""
    
    def __init__(self, transport_layer):
        self.transport_layer = transport_layer
        self.protocols = {
            'HTTP': HTTPProtocol(transport_layer),
            'FTP': FTPProtocol(transport_layer),
            'TELNET': TelnetProtocol(transport_layer),
            'SMTP': SMTPProtocol(transport_layer)
        }
        
    def get_protocol(self, protocol_name):
        """Get protocol instance"""
        return self.protocols.get(protocol_name.upper())
    
    def start_server(self, protocol_name, port=None):
        """Start server for specified protocol"""
        protocol = self.get_protocol(protocol_name)
        if protocol:
            return protocol.start_server(port)
        else:
            raise ValueError(f"Protocol {protocol_name} not supported")
    
    def start_client(self, protocol_name, server_address, server_port=None):
        """Start client for specified protocol"""
        protocol = self.get_protocol(protocol_name)
        if protocol:
            return protocol.start_client(server_address, server_port)
        else:
            raise ValueError(f"Protocol {protocol_name} not supported")
    
    def list_available_protocols(self):
        """List all available protocols"""
        return list(self.protocols.keys())
