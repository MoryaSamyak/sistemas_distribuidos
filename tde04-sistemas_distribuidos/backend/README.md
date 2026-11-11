# Backend

Este projeto executa três instâncias HTTP, um balanceador de carga e um broker
Kafka usando Docker Compose.

## Requisitos

- Docker Desktop com Docker Compose.
- Um arquivo `docker/.env` com as variáveis de ambiente usadas pelos serviços.
- Acesso à internet para consultar a API do TMDB.

O arquivo `.env` não deve ser compartilhado nem commitado. As variáveis usadas
pelo projeto são:

| Variável | Obrigatória | Descrição |
| --- | --- | --- |
| `TMDB_BEARER_TOKEN` | Sim para `/movie` | Token de autenticação do TMDB. |
| `TMDB_BASE_URL` | Não | URL base do TMDB; padrão `https://api.themoviedb.org/3`. |
| `KAFKA_BOOTSTRAP_SERVERS` | Não | Endereço do Kafka; padrão `kafka:9092` dentro do Compose. |
| `KAFKA_TOPIC` | Não | Tópico de publicação; padrão `movies_topic`. |

O Compose procura o arquivo em `docker/.env`. Não coloque valores secretos neste
README.

## Iniciar os serviços

No PowerShell, a partir desta pasta (`backend`), execute:

```powershell
docker compose -f ..\docker\docker-compose.yml up --build -d
```

Para acompanhar o estado:

```powershell
docker compose -f ..\docker\docker-compose.yml ps
docker compose -f ..\docker\docker-compose.yml logs -f load_balancer
```

O primeiro comando constrói as imagens e inicia três servidores, o balanceador,
o Kafka e a interface web do Kafka.

## Endereços

- **Balanceador:** `http://localhost:8080/movie`
- **Kafka UI:** `http://localhost:8081`
- Acesso direto às instâncias, sem balanceamento:
  - `http://localhost:8000/movie` (server01)
  - `http://localhost:8001/movie` (server02)
  - `http://localhost:8002/movie` (server03)

O balanceador escolhe uma instância usando least-connections e round-robin para
desempatar.

Uma resposta bem-sucedida de `/movie` é JSON com o nome da instância e os dados
de um filme. O balanceador também publica a resposta no tópico Kafka configurado.

## Teste de carga com ApacheBench

O comando abaixo executa o ApacheBench em um container temporário (Docker
Desktop), enviando 30 requisições com concorrência 3 ao balanceador:

```powershell
docker run --rm --network docker_default alpine sh -c "apk add --no-cache apache2-utils && ab -l -n 100 -c 10 http://load_balancer:8080/movie"

Teste com 100 requisições ab -n 100 -c 10 http://load_balancer:8080/movie

Teste com 500 requisições ab -n 500 -c 50 http://load_balancer:8080/movie

Teste com 2000 requisições ab -n 2000 -c 200 http://load_balancer:8080/movie

```

Cada requisição pode consultar o TMDB e publicar uma mensagem no Kafka. Use uma
carga moderada e observe os resultados e os logs:

```powershell
docker compose -f ..\docker\docker-compose.yml logs --since 5m load_balancer server01 server02 server03
```

## Encerrar

Para parar e remover os containers e a rede:

```powershell
docker compose -f ..\docker\docker-compose.yml down
```

Para remover também os dados persistidos do Kafka, use `docker compose down -v`.
Isso apaga o volume de dados do Kafka.

