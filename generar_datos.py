
import csv
import random
import os
from datetime import datetime, timedelta, timezone

random.seed(42)

os.makedirs("data", exist_ok=True)

comunas = [
    "Talca", "Curico", "Linares", "Constitucion",
    "Molina", "Parral", "San Javier", "Cauquenes"
]

materiales = ["vidrio", "papel", "carton", "plastico", "metal"]

transportistas = ["Ruta Verde", "EcoTrans", "Maule Circular"]

# GENERAR 30 PUNTOS LIMPIOS

puntos = []

for i in range(1, 31):

    punto = {
        "punto_id": f"PL-{i:03d}",
        "nombre": f"Punto Limpio {i}",
        "comuna": random.choice(comunas),
        "region": "Maule",
        "capacidad_kg": random.randint(500, 2000),
        "estado": random.choice(["activo", "mantencion"]),
        "materiales": "|".join(random.sample(materiales, 3))
    }

    puntos.append(punto)

with open("data/puntos_limpios.csv", "w", newline="", encoding="utf-8") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=puntos[0].keys())
    escritor.writeheader()
    escritor.writerows(puntos)

# GENERAR 1000 RETIROS

retiros = []

fecha_inicio = datetime(2025, 1, 1, tzinfo=timezone.utc)

for i in range(1, 1001):

    retiro = {
        "retiro_id": f"RET-{i:04d}",
        "punto_id": random.choice(puntos)["punto_id"],
        "fecha_retiro": (
            fecha_inicio + timedelta(days=random.randint(0, 650))
        ).isoformat(),
        "material": random.choice(materiales),
        "kg": f"{random.uniform(1, 500):.2f}",
        "transportista": random.choice(transportistas),
        "estado": random.choice([
            "recibido", "validado", "observado"
        ])
    }

    retiros.append(retiro)

with open("data/retiros.csv", "w", newline="", encoding="utf-8") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=retiros[0].keys())
    escritor.writeheader()
    escritor.writerows(retiros)

print("CSV generados correctamente.")
print("Puntos limpios:", len(puntos))
print("Retiros:", len(retiros))

