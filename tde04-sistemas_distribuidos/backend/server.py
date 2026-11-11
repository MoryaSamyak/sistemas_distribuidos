import http.server
import os
import socket
import random
import json
import requests 

    


class MyHandler(http.server.SimpleHTTPRequestHandler):  
    def do_GET(self):

        server = socket.gethostname()

        if self.path == "/movie":
            self.get_movie(server)
            return

        
        self.send_response(200)


    def get_movie(self, server):
        token =  os.getenv("TMDB_BEARER_TOKEN")
        base_url = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")

        if not token:
            self.send_error(500, "Token de autenticação não configurado.")
            return

        url = f"{base_url}/discover/movie"

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        params = {
            "language": "pt-BR",
            "page": 1
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            movies = data.get("results", [])

            if not movies:
                self.send_error(404, "Nenhum filme encontrado.")
                return

            movie = random.choice(movies)

            result = {"FilmShopNow. Uma indicação bacanuda para você assistir hoje!"
                "server": server,
                "movie": {
                    "title": movie.get("title"),
                    "overview": movie.get("overview"),
                    "release_date": movie.get("release_date"),
                    "vote_average": movie.get("vote_average")
                }
            }

            response_body = json.dumps(result, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body) 

        except requests.exceptions.RequestException as error:
            self.send_error(502, f"Erro ao acessar a API do TMDB: {error}")


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