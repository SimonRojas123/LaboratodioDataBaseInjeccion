
import os
import psycopg2

conexion = psycopg2.connect(
    host="puntos-limpios.cgb82ymy6e27.us-east-1.rds.amazonaws.com",
    port=5432,
    dbname="puntos_limpios_db",
    user="simon",
    password=os.environ["DB_PASSWORD"],
    sslmode="require"
)

try:
    with conexion.cursor() as cursor:

        cursor.execute("""
            SELECT
                t.relname AS tabla,
                c.conname AS restriccion,
                c.contype AS tipo,
                pg_get_constraintdef(c.oid) AS definicion
            FROM pg_constraint c
            JOIN pg_class t
                ON t.oid = c.conrelid
            JOIN pg_namespace n
                ON n.oid = t.relnamespace
            WHERE n.nspname = 'public'
              AND t.relname IN ('puntos_limpios', 'retiros')
            ORDER BY t.relname, c.contype, c.conname
        """)

        print("RESTRICCIONES DE POSTGRESQL\n")

        for fila in cursor.fetchall():
            print(fila)

finally:
    conexion.close()
