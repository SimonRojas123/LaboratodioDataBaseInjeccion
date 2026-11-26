import os
import psycopg2

try:
    with psycopg2.connect(
        host="puntos-limpios.cgb82ymy6e27.us-east-1.rds.amazonaws.com",
        database="puntos_limpios_db",
        user="simon",
        password=os.environ["DB_PASSWORD"],
        port=5432,
        sslmode="require",
        connect_timeout=10
    ) as conexion:

        with conexion.cursor() as cursor:
            with open("01_modelo_y_sql.sql", "r", encoding="utf-8") as archivo:
                cursor.execute(archivo.read())

    print("Tablas creadas correctamente en PostgreSQL")

except Exception as error:
    print("Error al crear las tablas:", error)
