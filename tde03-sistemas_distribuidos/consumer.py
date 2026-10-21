from kafka import KafkaConsumer
import json
from datetime import datetime, timedelta
from database import Database





def fraud_amount(transaction):
    return transaction["valor"] >= 10000


def fraud_time(transaction, database):
    hora_transacao = datetime.fromisoformat(transaction["hora"])
    horario_minimo = hora_transacao - timedelta(seconds=60)
    return database.verify_date_time(transaction, hora_transacao, horario_minimo)


def fraud_geo(transaction, database):
    hora_transacao = datetime.fromisoformat(transaction["hora"])
    horario_minimo = hora_transacao - timedelta(minutes=10)

    return database.verify_date_geo(transaction, hora_transacao, horario_minimo)

def create_consumer():
    return KafkaConsumer(
        'transactions_topic',
        bootstrap_servers='kafka:9092', 
        group_id='consumer_group', 
        auto_offset_reset='earliest',
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

            if fraud_amount(transaction,database):
                motivos_fraude.append("ALTO_VALOR")

            if fraud_time(transaction, database):
                motivos_fraude.append("TEMPO_60s")

            if fraud_geo(transaction, database):
                motivos_fraude.append("GEO_10m")

            transaction["fraude"] = 1 if motivos_fraude else 0
            transaction["motivo_fraude"] = (",".join(motivos_fraude) if motivos_fraude else None)

            database.insert_transaction(transaction)

            if transaction["fraude"]:
                print(f"Transação {transaction['id_transaction']} marcada como fraude. Motivos: {transaction['motivo_fraude']}")
            else:
                print(f"Transação {transaction['id_transaction']} processada com sucesso.")

    except KeyError:
        print("Erro: Sem transações recebidas ")    

if __name__ == "__main__":
    main()