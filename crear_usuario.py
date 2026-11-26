
from conexion import conectar_postgresql
from getpass import getpass

conexion = conectar_postgresql()

try:

    password = getpass("Contraseña del nuevo usuario: ")

    with conexion.cursor() as cursor:

        cursor.execute(
            "CREATE USER etl_lector WITH PASSWORD %s",
            (password,)
        )

        cursor.execute("""
            GRANT CONNECT ON DATABASE puntos_limpios_db
            TO etl_lector
        """)

        cursor.execute("""
            GRANT USAGE ON SCHEMA public
            TO etl_lector
        """)

        cursor.execute("""
            GRANT SELECT ON TABLE
                public.puntos_limpios,
                public.retiros
            TO etl_lector
        """)

    conexion.commit()

    print("Usuario creado correctamente")
    print("Permisos de lectura asignados")

except Exception as error:

    conexion.rollback()
    print("Error:", type(error).__name__)

finally:

    conexion.close()
