import uuid
import random

rng = random.Random(13)

clients = [
    str(uuid.UUID(int=rng.getrandbits(128), version=4))
    for _ in range(100)
]

cities = [
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
]
