import http.server
import socket


class MyHandler(http.server.SimpleHTTPRequestHandler):  
    def do_GET(self):

        server = socket.gethostname()
        url = f"http://{server}:8000{self.path}"    

        message = f"""
        <html>
            <body>
                <h1>Servidor funcionando!</h1>
                <p>Instancia: {server}</p>
                <p>URL: {url}</p>
            </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(bytes(message, "utf8"))

def run(server_class=http.server.ThreadingHTTPServer, handler_class=MyHandler, port=8000):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Encerrando servidor...")


if __name__ == "__main__":
    run()