from kafka import KafkaConsumer
import json



def fraud_amount(transaction):
    if transaction["valor"] >= 10000:
        return 


def fraud_time(transaction):

    return


def fraud_geo(transaction):

    return

def create_consumer():
    return KafkaConsumer(
        topic='transactions_topic',
        bootstrap_servers='kafka:9092', 
        group_id='consumer_group', 
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        )


def main():
    consumer = create_consumer()

    try: 
        for message in consumer:   
            transaction = message.value

            motivos_fraude = []

            if fraud_amount(transaction):
                motivos_fraude.append("ALTO_VALOR")
            if fraud_time(transaction):
                motivos_fraude.append("TEMPO_60s")
            if fraud_geo(transaction):
                motivos_fraude.append("GEO_10m")

    except KeyError:
        print("Erro: Mensagem recebida não contém os campos esperados.")    

        





if __name__ == "__main__":
    main()