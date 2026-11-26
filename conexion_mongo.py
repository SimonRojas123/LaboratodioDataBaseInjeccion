
import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

try:
    cliente = MongoClient(
        os.getenv("MONGO_URI"),
        serverSelectionTimeoutMS=30000,
        tlsCAFile=certifi.where()
    )

    cliente.admin.command("ping")

    db = cliente[os.getenv("MONGO_DB")]

    print("Conexion exitosa a MongoDB Atlas")
    print("Base de datos:", db.name)
    print("Colecciones:", db.list_collection_names())

    cliente.close()

except Exception as error:
    print("Error de conexion:", error)

