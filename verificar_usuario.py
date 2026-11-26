
from conexion import conectar_postgresql

conexion = conectar_postgresql()

try:

    with conexion.cursor() as cursor:

        for tabla in ["puntos_limpios", "retiros"]:

            print("\nTabla:", tabla)

            for permiso in ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE"]:

                cursor.execute("""
                    SELECT has_table_privilege(%s, %s, %s)
                """, ("etl_lector", f"public.{tabla}", permiso))

                resultado = cursor.fetchone()[0]

                print(permiso, ":", resultado)

finally:

    conexion.close()
