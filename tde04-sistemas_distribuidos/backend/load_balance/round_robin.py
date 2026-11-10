from threading import Lock  


SERVER_LIST = [
    "http://localhost:8001",
    "http://localhost:8002",
    "http://localhost:8003" 
    ] 


class RoundRobin:

    def __init__(self,servers):
        self.servers = servers  
        self.current = 0    
        self.lock = Lock()

    def get_next_server(self):
        with self.lock:
            server = self.servers[self.current]
            self.current = (self.current + 1) % len(self.servers)
            return server

