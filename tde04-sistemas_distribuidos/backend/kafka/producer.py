from kafka  import KafkaProducer
import json
import os


class producer:
    def __init__(self):
        self.topic = os.getenv("KAFKA_TOPIC", "http_requests_topic")

        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def publish(self, data):
        try:
            future = self.producer.send(self.topic, data)

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
    