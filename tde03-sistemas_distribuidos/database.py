from contextlib import closing
import sqlite3
import uuid


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_table()

    def connect(self):
        connection = sqlite3.connect(self.db_name)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def get_random_client_id(self):
        with closing(self.connect()) as conn:
            row = conn.execute(
                "SELECT id_client FROM clients ORDER BY RANDOM() LIMIT 1"
            ).fetchone()
        if row is None:
            raise LookupError("No clients are available")
        return row[0]

    def get_random_city(self):
        with closing(self.connect()) as conn:
            row = conn.execute(
                "SELECT name FROM cities ORDER BY RANDOM() LIMIT 1"
            ).fetchone()
        if row is None:
            raise LookupError("No cities are available")
        return row[0]

    
    def create_table(self): 
        with self.connection as conn:
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
            conn.execute("""CREATE TABLE IF NOT EXISTS clients (
            id_client TEXT PRIMARY KEY
            )""")

            client_count = conn.execute(
                "SELECT COUNT(*) FROM clients"
            ).fetchone()[0]
            if client_count < 15:
                conn.executemany(
                    "INSERT INTO clients (id_client) VALUES (?)",
                    ((str(uuid.uuid4()),) for _ in range(15 - client_count)),
                )

            conn.execute("""CREATE TABLE IF NOT EXISTS cities (
            id_city INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            state TEXT NOT NULL,
            country TEXT NOT NULL
            )""")
            conn.executemany(
                """INSERT OR IGNORE INTO cities (name, state, country)
                VALUES (?, 'Ceará', 'Brasil')""",
                (
                    (city,)
                    for city in (
                        "Abaiara",
                        "Altaneira",
                        "Antonina do Norte",
                        "Araripe",
                        "Assaré",
                        "Aurora",
                        "Barbalha",
                        "Barro",
                        "Brejo Santo",
                        "Campos Sales",
                        "Caririaçu",
                        "Crato",
                        "Farias Brito",
                        "Granjeiro",
                        "Jardim",
                        "Jati",
                        "Juazeiro do Norte",
                        "Lavras da Mangabeira",
                        "Mauriti",
                        "Milagres",
                        "Missão Velha",
                        "Nova Olinda",
                        "Penaforte",
                        "Porteiras",
                        "Potengi",
                        "Salitre",
                        "Santana do Cariri",
                        "Tarrafas",
                        "Várzea Alegre",
                    )
                ),
            )


    def insert_transaction(self, transaction):
        dados = transaction.to_dict()
        with closing(self.connection) as conn:
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
            (dados["id_transaction"],
            dados["id_client"],
            dados["valor"],
            dados["country"],
            dados["city"],
            dados["hora"],
            dados["fraude"],
            dados["motivo_fraude"]))
        conn.commit()