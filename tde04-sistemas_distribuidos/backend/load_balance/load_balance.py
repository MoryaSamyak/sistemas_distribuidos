from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
from least_connections import LeastConnections
from producer import Producer


SERVER_LIST = [
    "http://server01:8000",
    "http://server02:8000",
    "http://server03:8000",
]

balance = LeastConnections(SERVER_LIST)
producer = None

class LoadBalancerHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        server = balance.get_server()

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

    server = ThreadingHTTPServer(('0.0.0.0', 8080), LoadBalancerHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        producer.close()


if __name__ == "__main__":
    run()