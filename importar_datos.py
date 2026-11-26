
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
    with conexion:
        with conexion.cursor() as cursor:

            # IMPORTAR PUNTOS LIMPIOS
            with open(
                "data/puntos_limpios.csv",
                "r",
                encoding="utf-8"
            ) as archivo:

                cursor.copy_expert("""
                    COPY public.puntos_limpios (
                        punto_id,
                        nombre,
                        comuna,
                        region,
                        capacidad_kg,
                        estado,
                        materiales
                    )
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE)
                """, archivo)

            print("Puntos limpios importados.")

            # IMPORTAR RETIROS
            with open(
                "data/retiros.csv",
                "r",
                encoding="utf-8"
            ) as archivo:

                cursor.copy_expert("""
                    COPY public.retiros (
                        retiro_id,
                        punto_id,
                        fecha_retiro,
                        material,
                        kg,
                        transportista,
                        estado
                    )
                    FROM STDIN
                    WITH (FORMAT CSV, HEADER TRUE)
                """, archivo)

            print("Retiros importados.")

            # VERIFICAR CANTIDADES
            cursor.execute(
                "SELECT COUNT(*) FROM public.puntos_limpios"
            )
            print("Total puntos limpios:", cursor.fetchone()[0])

            cursor.execute(
                "SELECT COUNT(*) FROM public.retiros"
            )
            print("Total retiros:", cursor.fetchone()[0])

    print("Importación finalizada correctamente.")

except Exception as error:
    print("Error durante la importación:", error)

finally:
    conexion.close()
