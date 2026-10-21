# TDE 03 - Sistemas Distribuídos

Projeto de simulação de transações financeiras com Kafka. Um produtor gera transações continuamente, e um consumidor as analisa em busca de possíveis fraudes e registra os resultados em um banco SQLite.

## Como funciona

- **Producer**: gera uma transação aleatória a cada 3 segundos e a publica no tópico `transactions_topic`.
- **Kafka**: recebe e distribui as mensagens.
- **Consumer**: verifica cada transação e a classifica como suspeita quando:
  - o valor é igual ou superior a R$ 10.000;
  - há pelo menos três transações anteriores do mesmo cliente nos 60 segundos anteriores;
  - o cliente realizou uma transação em outra cidade nos 10 minutos anteriores.
- **SQLite**: armazena clientes, cidades e transações no arquivo `transactions.db`, criado pelo consumidor.
- **Kafka UI**: interface web para visualizar o cluster Kafka.

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (ou Docker Engine)
- Docker Compose v2, disponível como `docker compose`

Não é necessário instalar Python ou as dependências manualmente ao executar com Docker: as imagens instalam `kafka-python` e `colorama`.

## Instalar e executar

Abra um terminal na pasta do projeto e inicie os serviços:

```powershell
docker compose -f docker\docker-compose.yaml up --build
```

O comando constrói as imagens do produtor e do consumidor e inicia o Kafka, a interface web e os dois processos Python. As transações e os resultados aparecem nos logs do terminal.

Para executar em segundo plano:

```powershell
docker compose -f docker\docker-compose.yaml up --build -d
```

## Acompanhar a execução

- Kafka UI: [http://localhost:8080](http://localhost:8080)
- Logs de todos os serviços:

  ```powershell
  docker compose -f docker\docker-compose.yaml logs -f
  ```

- Logs apenas do consumidor:

  ```powershell
  docker compose -f docker\docker-compose.yaml logs -f consumer
  ```

O produtor registra cada transação enviada. O consumidor registra as transações recebidas e destaca as classificadas como fraude, incluindo os motivos `ALTO_VALOR`, `TEMPO_60s` e `GEO_10m`.

## Encerrar

Para parar e remover os containers e a rede criada pelo Compose:

```powershell
docker compose -f docker\docker-compose.yaml down
```

O volume `kafka_data` é mantido ao encerrar dessa forma. Para removê-lo também:

```powershell
docker compose -f docker\docker-compose.yaml down -v
```

**Atenção:** a opção `-v` apaga os dados persistidos do Kafka. O arquivo SQLite é criado dentro do container do consumidor e não está configurado como volume; portanto, pode ser perdido quando esse container for removido.

## Executar os scripts Python separadamente

Também é possível executar os scripts diretamente, desde que haja um broker Kafka acessível e configurado para anunciar `localhost:9092`. Instale Python 3.14 e as dependências:

```powershell
python -m pip install kafka-python colorama
$env:PYTHONPATH = (Get-Location).Path
```

Com o Kafka já em execução, abra terminais separados na raiz do projeto e inicie primeiro o consumidor e depois o produtor:

```powershell
python backend\consumer\consumer.py
```

```powershell
python backend\producer\producer.py
```

Os scripts usam `localhost:9092` por padrão. Para apontar para outro endereço, defina `KAFKA_BOOTSTRAP_SERVERS` no terminal antes de executar cada script. O broker usado nesta configuração deve anunciar um endereço acessível pelos processos Python; o Kafka definido no Compose anuncia `kafka:9092`, nome acessível dentro da rede Docker.
