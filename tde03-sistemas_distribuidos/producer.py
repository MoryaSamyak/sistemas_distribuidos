from kafka import KafkaProducer
import json
from transaction import Transaction
from database import Database
import time



database = Database("transactions.db")  

producer = KafkaProducer(   
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'))

topic = "transactions_topic"

def main():

    try:
        while True:
            transaction = Transaction(database)
            data = transaction.to_dict()
            key = data["id_transaction"]
            producer.send(topic, value=data, key=key)
            time.sleep(3)   
    except KeyboardInterrupt:
        print("Finalizando...")
        producer.close()


if __name__ == "__main__":
    main()