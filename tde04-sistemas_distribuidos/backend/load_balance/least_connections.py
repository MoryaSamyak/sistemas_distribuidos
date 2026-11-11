from threading import Lock
from round_robin import RoundRobin


class LeastConnections:
    def __init__(self, servers):
        self.servers = servers
        self.connections = {server: 0 for server in servers}
        self.health = {server: True for server in servers}
        self.round_robin = RoundRobin(servers)
        self.lock = Lock()


    def set_server_health(self, server, healthy):
        with self.lock:
            if server in self.health:
                self.health[server] = healthy

    def get_server(self):
        with self.lock:
            
            servers_available = [server for server in self.servers if self.health[server]]
            
            if not servers_available:
                return None
            
            minimum_connections = min(self.connections[server] for server in servers_available)

            
            servers_least_connections = [server for server in servers_available 
                                        if self.connections[server] == minimum_connections]
            

            if len(servers_least_connections) == 1:
                server = servers_least_connections[0]
            else:
                while True:
                    server = self.round_robin.get_next_server()
                    if server in servers_least_connections:
                        break

            self.connections[server] += 1
                
        return server   

    def release_connection(self, server):
        with self.lock:
            if server in self.connections:
                if self.connections[server] > 0:
                    self.connections[server] -= 1