from backend.shared.data import clients, cities
from datetime import datetime, timezone
import random
import uuid





class Transaction:
    def __init__(self, is_fraud=0, fraud_history=None):
        self.id_transaction = str(uuid.uuid4())
        self.id_client = random.choice(clients)
        self.amount = round(random.uniform(10, 15000), 2)
        self.country = "Brasil"
        self.city = random.choice(cities)
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.is_fraud = is_fraud
        self.fraud_history = fraud_history


    def to_dict(self):  
        return {
            "id_transaction": self.id_transaction,
            "id_client": self.id_client,
            "amount": self.amount,
            "country": self.country,
            "city": self.city,
            "timestamp": self.timestamp,
        }
