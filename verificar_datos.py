
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

        # CONTAR PUNTOS LIMPIOS
        cursor.execute("""
            SELECT COUNT(*)
            FROM public.puntos_limpios
        """)

        print("Puntos limpios:", cursor.fetchone()[0])

        # CONTAR RETIROS
        cursor.execute("""
            SELECT COUNT(*)
            FROM public.retiros
        """)

        print("Retiros:", cursor.fetchone()[0])

        # VERIFICAR INTEGRIDAD REFERENCIAL
        cursor.execute("""
            SELECT COUNT(*)
            FROM public.retiros r
            LEFT JOIN public.puntos_limpios p
                ON r.punto_id = p.punto_id
            WHERE p.punto_id IS NULL
        """)

        print(
            "Retiros sin punto limpio:",
            cursor.fetchone()[0]
        )

        # CONSULTA INNER JOIN
        cursor.execute("""
            SELECT
                r.retiro_id,
                p.nombre,
                p.comuna,
                r.material,
                r.kg
            FROM public.retiros r
            INNER JOIN public.puntos_limpios p
                ON r.punto_id = p.punto_id
            ORDER BY r.retiro_id
            LIMIT 5
        """)

        print("\nEjemplo de INNER JOIN:")

        for fila in cursor.fetchall():
            print(fila)

finally:
    conexion.close()
