from backend.shared.data import clients, cities
from contextlib import closing
import sqlite3


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.create_table()
        self.insert_clients()
        self.insert_cities()

    def connect(self):
        connection = sqlite3.connect(self.db_name)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
    
    def create_table(self): 
        with closing(self.connect()) as conn:
            with conn:

                conn.execute("""CREATE TABLE IF NOT EXISTS clients (
                id_client TEXT PRIMARY KEY
                )""")

                conn.execute("""CREATE TABLE IF NOT EXISTS cities (
                id_city INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                state TEXT NOT NULL,
                country TEXT NOT NULL
                )""")

                conn.execute("""CREATE TABLE IF NOT EXISTS transactions (
                id_transaction TEXT PRIMARY KEY,
                id_client TEXT NOT NULL REFERENCES clients(id_client),
                amount REAL NOT NULL,
                country TEXT NOT NULL,
                city TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                is_fraud INTEGER NOT NULL DEFAULT 0,
                fraud_history TEXT
                )""")
            

    def insert_clients(self):
        with closing(self.connect()) as conn: 
            with conn:     
                conn.executemany(
                "INSERT OR IGNORE INTO clients (id_client) VALUES (?)",
                [(client,) for client in clients] )

    def insert_cities(self):
        with closing(self.connect()) as conn:
            with conn:
                conn.executemany(
                    """INSERT OR IGNORE INTO cities (name, state, country)
                    VALUES (?, 'Ceará', 'Brasil')""",
                    [(city,) for city in cities])
    

    def insert_transaction(self, transaction):
        with closing(self.connect()) as conn:
            with conn:
                conn.execute("""INSERT INTO transactions( \
                id_transaction,
                id_client,
                amount,
                country,
                city,
                timestamp,
                is_fraud,
                fraud_history
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (transaction["id_transaction"],
                transaction["id_client"],
                transaction["amount"],
                transaction["country"],
                transaction["city"],
                transaction["timestamp"],
                transaction["is_fraud"],
                transaction["fraud_history"]))




    def verify_date_geo(self, transaction, transaction_timestamp, minimum_timestamp):
        with closing(self.connect()) as conn:
            with conn:
                result = conn.execute("""SELECT * FROM transactions WHERE 
                id_client = ? 
                AND city != ? 
                AND timestamp > ?
                AND timestamp < ?
                  LIMIT 1""", (transaction["id_client"], 
                               transaction["city"], 
                               minimum_timestamp.isoformat(), 
                               transaction_timestamp.isoformat())).fetchone()

        return result is not None    

    def verify_date_time(self, transaction, transaction_timestamp, minimum_timestamp):
        with closing(self.connect()) as conn:
            with conn:
                result = conn.execute("""SELECT count(*) FROM transactions WHERE 
                id_client = ? 
                AND timestamp >= ?
                AND timestamp < ?
                """, (transaction["id_client"],  
                               minimum_timestamp.isoformat(), 
                               transaction_timestamp.isoformat())).fetchone()

        if result[0] >= 3:
            return True
        else:
            return False