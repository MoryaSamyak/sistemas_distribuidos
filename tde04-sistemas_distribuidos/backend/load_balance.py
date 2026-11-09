from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from round_robin import RoundRobin



SERVER_LIST = [
    "http://server01:8000",
    "http://server02:8000",
    "http://server03:8000",
]

balance = RoundRobin(SERVER_LIST) 

class LoadBalancerHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        server = balance.get_next_server()

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
            self.send_error(502, f"Erro ao encaminhar requisição: {error}")

def run():
    server = ThreadingHTTPServer(('0.0.0.0', 8080), LoadBalancerHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run()