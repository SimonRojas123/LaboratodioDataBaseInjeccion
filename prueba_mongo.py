
import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient, ReadPreference

load_dotenv()

try:
    cliente = MongoClient(
        os.getenv("MONGO_URI"),
        serverSelectionTimeoutMS=30000,
        tlsCAFile=certifi.where(),
        read_preference=ReadPreference.SECONDARY
    )

    db = cliente[os.getenv("MONGO_DB")]

    print("Conexion exitosa con servidor secundario")
    print("Base de datos:", db.name)
    print("Puntos limpios:", db.puntos_limpios.count_documents({}))
    print("Retiros:", db.retiros.count_documents({}))

    cliente.close()

except Exception as error:
    print("Error de conexion:", error)
