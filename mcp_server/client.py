import socket
import sys
import threading
import time
from typing import Optional

class MCPClient:
    def __init__(self, host: str = 'localhost', port: int = 5001):
        """Initialize the MCP client with server details."""
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.receive_thread: Optional[threading.Thread] = None

    def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            print(f"Connected to MCP Server at {self.host}:{self.port}")
            print("Type 'HELP' for available commands or 'EXIT' to quit.")
            return True
            
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False

    def _receive_messages(self) -> None:
        """Background thread to receive messages from the server."""
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    print("\nDisconnected from server.")
                    self.running = False
                    break
                    
                # Handle potential partial messages
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    print(f"\r{line}\n> ", end='', flush=True)
                    
            except ConnectionResetError:
                print("\nConnection to server was reset.")
                self.running = False
                break
            except Exception as e:
                print(f"\nError receiving message: {e}")
                self.running = False
                break

    def send_command(self, command: str) -> None:
        """Send a command to the server."""
        if not command.strip():
            return
            
        try:
            self.socket.sendall(f"{command}\n".encode('utf-8'))
        except Exception as e:
            print(f"Failed to send command: {e}")
            self.running = False

    def disconnect(self) -> None:
        """Disconnect from the server and clean up."""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

def main():
    """Main function to run the MCP client."""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MCP Client')
    parser.add_argument('--host', default='localhost', help='Server hostname or IP')
    parser.add_argument('--port', type=int, default=5001, help='Server port (default: 5001)')
    args = parser.parse_args()
    
    # Create and connect client
    client = MCPClient(host=args.host, port=args.port)
    print(f"Connecting to MCP Server at {args.host}:{args.port}...")
    
    if not client.connect():
        print(f"Failed to connect to server at {args.host}:{args.port}")
        print("Please make sure the server is running and the port is correct.")
        return 1
    
    try:
        # Main command loop
        while client.running:
            try:
                # Get user input (with prompt)
                command = input("> ").strip()
                
                # Handle exit command
                if command.upper() == 'EXIT':
                    client.send_command('EXIT')
                    time.sleep(0.5)  # Give time for the server to respond
                    break
                    
                # Send command to server
                client.send_command(command)
                
            except (EOFError, KeyboardInterrupt):
                print("\nDisconnecting...")
                client.send_command('EXIT')
                break
            except Exception as e:
                print(f"\nError: {e}")
                break
                
    finally:
        client.disconnect()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
