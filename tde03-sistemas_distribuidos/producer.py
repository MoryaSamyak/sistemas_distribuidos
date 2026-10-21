from kafka import KafkaProducer
import json
from transaction import Transaction
import time




def main():

    producer = KafkaProducer(   
        bootstrap_servers='kafka:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8'))

    topic = "transactions_topic"


    try:
        while True:
            transaction = Transaction()
            data = transaction.to_dict()
            key = data["id_transaction"]
            producer.send(topic, value=data, key=key)
            time.sleep(3)   
    except KeyboardInterrupt:
        print("\nFinalizando...")
        producer.close()


if __name__ == "__main__":
    main()