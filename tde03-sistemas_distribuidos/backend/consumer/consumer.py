from backend.consumer.database import Database
from datetime import datetime, timedelta
from kafka import KafkaConsumer
from colorama import Fore, init
import json
import os


init(autoreset=True)



def fraud_amount(transaction):
    return transaction["amount"] >= 10000


def fraud_time(transaction, database):
    transaction_timestamp = datetime.fromisoformat(transaction["timestamp"])
    minimum_timestamp = transaction_timestamp - timedelta(seconds=60)
    return database.verify_date_time(transaction, transaction_timestamp, minimum_timestamp)


def fraud_geo(transaction, database):
    transaction_timestamp = datetime.fromisoformat(transaction["timestamp"])
    minimum_timestamp = transaction_timestamp - timedelta(minutes=10)

    return database.verify_date_geo(transaction, transaction_timestamp, minimum_timestamp)

def create_consumer():
    return KafkaConsumer(
        'transactions_topic',
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        group_id='consumer_group', 
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        )


def main():
    database = Database("transactions.db")   
    consumer = create_consumer()

    try: 
        for message in consumer:   
            transaction = message.value
            motivos_fraude = []

            if fraud_amount(transaction):
                motivos_fraude.append("ALTO_VALOR")

            if fraud_time(transaction, database):
                motivos_fraude.append("TEMPO_60s")

            if fraud_geo(transaction, database):
                motivos_fraude.append("GEO_10m")

            transaction["is_fraud"] = 1 if motivos_fraude else 0
            transaction["fraud_history"] = (",".join(motivos_fraude) if motivos_fraude else None)

            if transaction["is_fraud"]:
                print(Fore.RED +
                    f"Fraude detectada: {transaction['fraud_history']} | "
                    f"transaction_id={transaction['id_transaction']} | "
                    f"client={transaction['id_client']} | "
                    f"amount=R${transaction['amount']:.2f} | "
                    f"city={transaction['city']}",
                    flush=True
                    )
            else:
                print(Fore.GREEN +
                    f"Transação recebida: "
                    f"id={transaction['id_transaction']} | "
                    f"client={transaction['id_client']} | "
                    f"amount=R${transaction['amount']:.2f} | "
                    f"city={transaction['city']}",
                    flush=True
                )

            try:
                database.insert_transaction(transaction)
            except Exception as error:
                print(Fore.RED + f"Erro ao inserir transação no banco: {error}", flush=True)

    except KeyboardInterrupt:
        print(Fore.CYAN + "Encerrando...", flush=True)    
    finally:    
        consumer.close()

if __name__ == "__main__":
    main()