from contextlib import closing
import sqlite3
from data import clients, cities

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
                valor REAL NOT NULL,
                country TEXT NOT NULL,
                city TEXT NOT NULL,
                hora TEXT NOT NULL,
                fraude INTEGER NOT NULL DEFAULT 0,
                motivo_fraude TEXT
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
                valor,
                country,
                city,
                hora,
                fraude,
                motivo_fraude
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (transaction["id_transaction"],
                transaction["id_client"],
                transaction["valor"],
                transaction["country"],
                transaction["city"],
                transaction["hora"],
                transaction["fraude"],
                transaction["motivo_fraude"]))



    def verify_date_geo(self, transaction, hora_transacao, horario_minimo):
        with closing(self.connect()) as conn:
            with conn:
                resultado = conn.execute("""SELECT * FROM transactions WHERE 
                id_client = ? 
                AND city != ? 
                AND hora > ?
                AND hora < ?
                  LIMIT 1""", (transaction["id_client"], 
                               transaction["city"], 
                               horario_minimo.isoformat(), 
                               hora_transacao.isoformat())).fetchone()

        return resultado is not None    

    def verify_date_time(self, transaction, hora_transacao, horario_minimo):
        with closing(self.connect()) as conn:
            with conn:
                resultado = conn.execute("""SELECT count(*) FROM transactions WHERE 
                id_client = ? 
                AND hora > ?
                AND hora < ?
                """, (transaction["id_client"],  
                               horario_minimo.isoformat(), 
                               hora_transacao.isoformat())).fetchone()

        if resultado[0] >= 3:
            return True
        else:
            return False