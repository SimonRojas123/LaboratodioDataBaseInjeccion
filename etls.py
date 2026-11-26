
from conexion import conectar_postgresql
from psycopg2.extras import RealDictCursor
from bson.decimal128 import Decimal128


def extraer_datos():

    conexion = conectar_postgresql()

    try:
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("SELECT * FROM puntos_limpios")
            puntos_limpios = cursor.fetchall()

            cursor.execute("SELECT * FROM retiros")
            retiros = cursor.fetchall()

        return puntos_limpios, retiros

    finally:
        conexion.close()


def transformar_datos(puntos_limpios, retiros):

    puntos_transformados = []
    retiros_transformados = []

    for punto in puntos_limpios:

        documento = dict(punto)

        documento["materiales"] = punto["materiales"].split("|")

        puntos_transformados.append(documento)

    for retiro in retiros:

        documento = dict(retiro)

        documento["kg"] = Decimal128(retiro["kg"])

        retiros_transformados.append(documento)

    return puntos_transformados, retiros_transformados


def validar_datos(puntos, retiros):

    ids_puntos = {punto["punto_id"] for punto in puntos}
    ids_retiros = {retiro["retiro_id"] for retiro in retiros}

    if len(ids_puntos) != len(puntos):
        raise ValueError("Existen puntos limpios duplicados")

    if len(ids_retiros) != len(retiros):
        raise ValueError("Existen retiros duplicados")

    for punto in puntos:

        if punto["capacidad_kg"] <= 0:
            raise ValueError("Capacidad incorrecta")

        if punto["estado"] not in ["activo", "mantencion"]:
            raise ValueError("Estado de punto incorrecto")

    for retiro in retiros:

        if retiro["punto_id"] not in ids_puntos:
            raise ValueError("Retiro sin punto limpio asociado")

        if retiro["kg"].to_decimal() <= 0:
            raise ValueError("Cantidad de kg incorrecta")

        if retiro["estado"] not in ["recibido", "validado", "observado"]:
            raise ValueError("Estado de retiro incorrecto")

    print("\nValidacion completada")
    print("Puntos duplicados: 0")
    print("Retiros duplicados: 0")
    print("Retiros sin punto asociado: 0")
    print("Todos los registros son validos")

if __name__ == "__main__":

    puntos_limpios, retiros = extraer_datos()

    print("Extraccion completada")
    print("Puntos limpios:", len(puntos_limpios))
    print("Retiros:", len(retiros))

    puntos, retiros = transformar_datos(puntos_limpios, retiros)

    print("\nTransformacion completada")
    print("Puntos transformados:", len(puntos))
    print("Retiros transformados:", len(retiros))

    print("\nEjemplo de punto transformado:")
    print(puntos[0])

    print("\nEjemplo de retiro transformado:")
    print(retiros[0])

    validar_datos(puntos, retiros)
