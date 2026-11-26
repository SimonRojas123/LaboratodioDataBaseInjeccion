
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def conectar_postgresql():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=int(os.getenv("DB_PORT", "5432")),
        sslmode="require",
        connect_timeout=10
    )


if __name__ == "__main__":
    try:
        conexion = conectar_postgresql()

        print("Conexion exitosa a PostgreSQL en AWS")

        conexion.close()

    except Exception as error:
        print("Error al conectar:", error)
