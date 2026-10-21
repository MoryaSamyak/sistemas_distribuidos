from backend.shared.data import clients
from transaction import Transaction
from kafka.errors import KafkaError
from colorama import Fore, init
from kafka import KafkaProducer
import json
import time
import os


init(autoreset=True)


def main():

    producer = KafkaProducer(   
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8'),
        acks='all',
        retries=5,
    )

    topic = "transactions_topic"

    print(Fore.CYAN + f"Clientes: {', '.join(clients)}", flush=True)

    try:
        while True:
            transaction = Transaction()

            print(f"Enviando transação: "
                  f"id={transaction.id_transaction} | "
                  f"client={transaction.id_client} | "
                  f"amount=R${transaction.amount:.2f} | "
                  f"city={transaction.city}",
                  flush=True)

            try:
                data = transaction.to_dict()
                
                key = data["id_transaction"]
                producer.send(topic, value=data, key=key)
  
            except KafkaError as error:
                print(Fore.RED + f"Erro ao enviar transação: {error}", flush=True)

            time.sleep(3) 

    except KeyboardInterrupt:
        print("Encerrando...", flush=True)
    finally:
        producer.close()


if __name__ == "__main__":
    main()