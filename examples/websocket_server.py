#!/usr/bin/env python3
"""
WebSocket Server for Agent Clarification

This server listens on port 38765 and handles clarification requests from agents.
When an agent sends a clarification prompt, the server:
1. Displays the prompt to the user
2. Waits for user input
3. Sends the user's response back to the agent

Usage:
    python examples/websocket_server.py

Then run the research agent demo in another terminal:
    python examples/demo.py
"""

import json
import socket
import threading


class AgentClarificationServer:
    """WebSocket server for handling agent clarification requests."""

    def __init__(self, host="localhost", port=38765):
        """
        Initialize the clarification server.

        Args:
            host: Server host (default: localhost)
            port: Server port (default: 38765)
        """
        self.host = host
        self.port = port
        self.running = True

    def handle_client(self, client_socket, addr):
        """
        Handle client connection and process clarification requests.

        Args:
            client_socket: Client socket connection
            addr: Client address
        """
        print(f"\n{'='*60}")
        print(f"🤖 Agent connected from {addr}")
        print(f"{'='*60}")

        try:
            while self.running:
                # Receive message from agent
                data = client_socket.recv(4096).decode("utf-8")
                if not data:
                    break

                # Parse the message
                message = json.loads(data)
                prompt = message.get("prompt", "")
                session_id = message.get("session_id", "unknown")

                print(f"\n📨 Received clarification request:")
                print(f"   Session ID: {session_id}")
                print(f"\n{prompt}")
                print(f"\n{'-'*60}")

                # Get user input for clarification
                print("💬 Your response:")
                user_response = input("> ").strip()

                # Send user's response back to agent
                response = {"message": user_response, "status": "success", "session_id": session_id}
                client_socket.send(json.dumps(response).encode("utf-8"))
                
                print(f"\n✅ Sent response to agent: {user_response[:100]}...")
                print(f"{'='*60}\n")

        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
        except Exception as e:
            print(f"❌ Error handling client: {e}")
        finally:
            client_socket.close()
            print(f"🔌 Agent {addr} disconnected")

    def start_server(self):
        """Start the WebSocket server."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        print(f"\n{'='*60}")
        print(f"🚀 Agent Clarification Server Started")
        print(f"{'='*60}")
        print(f"📡 Listening on {self.host}:{self.port}")
        print(f"⏹️  Press Ctrl+C to stop")
        print(f"{'='*60}\n")
        print("Waiting for agent connections...")
        print("When an agent requests clarification, you'll be prompted to respond.\n")

        try:
            while self.running:
                client_socket, addr = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("\n\n{'='*60}")
            print("🛑 Shutting down server...")
            print(f"{'='*60}")
            self.running = False
        finally:
            server_socket.close()
            print("✅ Server stopped")


if __name__ == "__main__":
    server = AgentClarificationServer()
    server.start_server()

