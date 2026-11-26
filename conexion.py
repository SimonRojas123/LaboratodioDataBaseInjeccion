import os
import psycopg2

try:
    conexion = psycopg2.connect(
        host="puntos-limpios.cgb82ymy6e27.us-east-1.rds.amazonaws.com",
        database="puntos_limpios_db",
        user="simon",
        password=os.environ["DB_PASSWORD"],
        port=5432,
        sslmode="require",
        connect_timeout=10
    )

    print("Conexión exitosa a PostgreSQL en AWS")
    conexion.close()

except Exception as error:
    print("Error al conectar:", error)
