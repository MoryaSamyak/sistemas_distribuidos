from kafka  import KafkaProducer
import json
import os


class Producer:
    def __init__(self):
        self.topic = os.getenv("KAFKA_TOPIC", "movies_topic")

        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def publish(self, data):
        try:
            key = data["server"].encode("utf-8")
            future = self.producer.send(self.topic, data, key=key)

            result = future.get(timeout=5)

            print(
                f"Mensagem publicada no Kafka: "
                f"topic={result.topic}, "
                f"partition={result.partition}, "
                f"offset={result.offset}",
                flush=True)

        except Exception as error:
            print(f"Erro ao publicar mensagem no Kafka: {error}", flush=True)
    
    def close(self):
        self.producer.flush()
        self.producer.close()
    