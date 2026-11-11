from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
from least_connections import LeastConnections
from producer import Producer
from threading import Thread, Event


SERVER_LIST = [
    "http://server01:8000",
    "http://server02:8000",
    "http://server03:8000",
]
HEALTH_CHECK_INTERVAL = 5
HEALTH_CHECK_TIMEOUT = 2

balance = LeastConnections(SERVER_LIST)
producer = None
stop_health_check = Event()

def check_server(server):
    try:
        request = Request(server + "/health")
        
        with urlopen(request, timeout=HEALTH_CHECK_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
            
            return (response.status == 200 and data.get("status") == "healthy")
    
    except(URLError,TimeoutError,json.JSONDecodeError,OSError,UnicodeDecodeError) as error:
        
        return False
        
def health_check():
    previous_state = {}
    
    while not stop_health_check.is_set():
        
        for server in SERVER_LIST:
            health = check_server(server)
            
            balance.set_server_health(server, health)
            
            if previous_state.get(server )!= health:
                
                status = "healthy" if health else "unhealthy"
                
                print(f"Servidor {server} está {status}.", flush=True)
                previous_state[server] = health
                
        stop_health_check.wait(HEALTH_CHECK_INTERVAL)
        
         

class LoadBalancerHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        server = balance.get_server()
        
        if server is None:
            self.send_error(503, "Nenhum servidor disponível.")
            return

        print(f"Encaminhando requisição para: {server}" ,flush=True)

        try: 
            request = Request(server + self.path, headers={
                    "User-Agent": self.headers.get("User-Agent", "")
                })

            try:
                response = urlopen(request, timeout=5)

            except HTTPError as error:
                response = error

            with response:
                body = response.read()

                if self.path == "/movie" and response.status == 200:
                    try:
                        data = json.loads(body.decode("utf-8"))
                        producer.publish(data)
                    except json.JSONDecodeError as error:
                        print(f"Erro na resposta do servidor {server}: {error}", flush=True)

                self.send_response(response.status)

                for header_name, value in response.headers.items():
                    if header_name.lower() not in (
                        "transfer-encoding",
                        "connection",
                        "keep-alive",
                    ):
                        self.send_header(header_name, value)

                self.end_headers()
                self.wfile.write(body)

        except (URLError,TimeoutError,OSError) as error:
            self.send_error(502, f"Erro ao acessar servidor {server}: {error}")

        finally:
            balance.release_connection(server)

def run():

    global producer
    producer = Producer()
    
    for server in SERVER_LIST:
        health = check_server(server)
        balance.set_server_health(server, health)
        
        status = "Funfando" if health else "funfando nao"
        print(f"Servidor {server} está {status}.", flush=True)
        
    health_thread = Thread(target=health_check, daemon=True)
    health_thread.start()

    server = ThreadingHTTPServer(('0.0.0.0', 8080), LoadBalancerHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_health_check.set()
        health_thread.join(timeout = 3)
        server.server_close()
        producer.close()


if __name__ == "__main__":
    run()