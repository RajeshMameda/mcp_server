import socket
import threading
import logging
from typing import Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp_server.log')
    ]
)

class MCPServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 5001):
        """Initialize the MCP server with host and port."""
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients: Dict[tuple, socket.socket] = {}
        self.running = False
        self.command_handlers = {
            'HELLO': self._handle_hello,
            'ECHO': self._handle_echo,
            'EXIT': self._handle_exit,
            'HELP': self._handle_help
        }

    def start(self) -> None:
        """Start the MCP server and begin accepting connections."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logging.info(f"MCP Server started on {self.host}:{self.port}")
            logging.info("Waiting for connections...")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    logging.info(f"New connection from {client_address}")
                except OSError as e:
                    if self.running:
                        logging.error(f"Error accepting connection: {e}")
        except Exception as e:
            logging.error(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the MCP server and close all connections."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                logging.error(f"Error closing server socket: {e}")
        
        # Close all client connections
        for client_socket in self.clients.values():
            try:
                client_socket.close()
            except Exception as e:
                logging.error(f"Error closing client socket: {e}")
        
        self.clients.clear()
        logging.info("MCP Server stopped")

    def _handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
        """Handle communication with a connected client."""
        self.clients[client_address] = client_socket
        
        try:
            # Send welcome message
            self._send_response(client_socket, "MCP Server: Connected. Type 'HELP' for available commands.")
            
            while self.running:
                try:
                    # Receive data from client
                    data = client_socket.recv(1024).decode('utf-8').strip()
                    if not data:
                        break
                        
                    logging.info(f"Received from {client_address}: {data}")
                    
                    # Process command
                    parts = data.split(' ', 1)
                    command = parts[0].upper()
                    arg = parts[1] if len(parts) > 1 else ''
                    
                    if command in self.command_handlers:
                        self.command_handlers[command](client_socket, arg)
                    else:
                        self._send_response(client_socket, f"ERROR: Unknown command: {command}")
                        
                except ConnectionResetError:
                    break
                except Exception as e:
                    logging.error(f"Error handling client {client_address}: {e}")
                    self._send_response(client_socket, f"ERROR: {str(e)}")
                    break
                    
        except Exception as e:
            logging.error(f"Error in client handler for {client_address}: {e}")
        finally:
            # Clean up
            if client_address in self.clients:
                del self.clients[client_address]
            try:
                client_socket.close()
            except:
                pass
            logging.info(f"Client disconnected: {client_address}")

    def _send_response(self, client_socket: socket.socket, message: str) -> None:
        """Send a response to a client."""
        try:
            client_socket.sendall(f"{message}\n".encode('utf-8'))
        except Exception as e:
            logging.error(f"Error sending response: {e}")

    # Command Handlers
    def _handle_hello(self, client_socket: socket.socket, arg: str) -> None:
        """Handle HELLO command."""
        name = arg if arg else 'Guest'
        self._send_response(client_socket, f"Hello, {name}! Welcome to MCP Server.")

    def _handle_echo(self, client_socket: socket.socket, arg: str) -> None:
        """Handle ECHO command."""
        if not arg:
            self._send_response(client_socket, "ECHO: You didn't provide any text to echo.")
        else:
            self._send_response(client_socket, f"ECHO: {arg}")

    def _handle_exit(self, client_socket: socket.socket, arg: str) -> None:
        """Handle EXIT command."""
        self._send_response(client_socket, "Goodbye!")
        if client_socket in self.clients.values():
            client_socket.close()

    def _handle_help(self, client_socket: socket.socket, arg: str) -> None:
        """Handle HELP command."""
        help_text = """
Available Commands:
  HELLO [name]  - Greet the server
  ECHO <text>   - Echo back the provided text
  EXIT          - Disconnect from the server
  HELP          - Show this help message
"""
        self._send_response(client_socket, help_text.strip())


def main():
    """Main function to start the MCP server."""
    import socket
    
    # Try default port, if busy, try next available port
    port = 5001
    max_attempts = 5
    server = None
    
    for attempt in range(max_attempts):
        try:
            server = MCPServer(host='0.0.0.0', port=port)
            print(f"Starting MCP Server on port {port}...")
            server.start()
            break
        except OSError as e:
            if "Address already in use" in str(e) and attempt < max_attempts - 1:
                print(f"Port {port} is in use, trying port {port + 1}...")
                port += 1
            else:
                logging.error(f"Failed to start server: {e}")
                return 1
        except KeyboardInterrupt:
            logging.info("\nShutting down server...")
            if server:
                server.stop()
            break
        except Exception as e:
            logging.error(f"Fatal error: {e}")
            if server:
                server.stop()
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())