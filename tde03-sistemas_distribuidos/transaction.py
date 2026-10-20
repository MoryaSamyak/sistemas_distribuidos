import random
import uuid
from datetime import datetime, timezone



class Transaction:
    def __init__(self, database, fraude=0, motivo_fraude=None):
        self.id_transaction = str(uuid.uuid4())
        self.id_client = database.get_random_client_id()
        self.valor = round(random.uniform(10, 12000), 2)
        self.country = "Brasil"
        self.city = database.get_random_city()
        self.hora = datetime.now(timezone.utc).isoformat()
        self.fraude = fraude
        self.motivo_fraude = motivo_fraude


    def to_dict(self):  
        return {
            "id_transaction": self.id_transaction,
            "id_client": self.id_client,
            "valor": self.valor,
            "country": self.country,
            "city": self.city,
            "hora": self.hora,
            "fraude": self.fraude,
            "motivo_fraude": self.motivo_fraude
        }
