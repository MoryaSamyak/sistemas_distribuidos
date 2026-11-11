from threading import Lock  



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

