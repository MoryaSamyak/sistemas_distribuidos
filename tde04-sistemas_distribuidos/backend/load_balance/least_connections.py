from threading import Lock
from round_robin import RoundRobin

SERVER_LIST = [
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003" 
    ] 


class LeastConnections:
    def __init__(self, servers):
        self.servers = servers
        self.connections = {server: 0 for server in servers}
        self.round_robin = RoundRobin(servers)
        self.lock = Lock()


    def get_server(self):
        with self.lock:

            minimum_connections = min(self.connections.values())


            servers_available = []

            for server in self.servers:
                if self.connections[server] == minimum_connections:
                    servers_available.append(server)

        if len(servers_available) == 1:
            server = servers_available[0]
        else:
            while True:
                server = self.round_robin.get_next_server()
                if server in servers_available:
                    break

        self.connections[server] += 1
        return server   


    def release_connection(self, server):
        with self.lock:
            if server in self.connections and self.connections[server] > 0:
                self.connections[server] -= 1