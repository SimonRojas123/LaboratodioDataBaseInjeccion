
import os
import certifi
import logging

from conexion import conectar_postgresql
from psycopg2.extras import RealDictCursor
from bson.decimal128 import Decimal128
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne


load_dotenv()


# CONFIGURACION DE LOGS

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)


# EXTRACCION DE DATOS DESDE POSTGRESQL

def extraer_datos():

    conexion = conectar_postgresql()

    try:

        conexion.set_session(readonly=True)

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("""
                SELECT
                    punto_id,
                    nombre,
                    comuna,
                    region,
                    capacidad_kg,
                    estado,
                    materiales
                FROM public.puntos_limpios
            """)

            puntos_limpios = cursor.fetchall()

            cursor.execute("""
                SELECT
                    retiro_id,
                    punto_id,
                    fecha_retiro,
                    material,
                    kg,
                    transportista,
                    estado
                FROM public.retiros
            """)

            retiros = cursor.fetchall()

        return puntos_limpios, retiros

    finally:

        conexion.close()


# TRANSFORMACION DE DATOS

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


# VALIDACION DE DATOS

def validar_datos(puntos, retiros):

    puntos_validos = []
    retiros_validos = []

    puntos_rechazados = 0
    retiros_rechazados = 0

    ids_puntos = set()
    ids_retiros = set()

    for punto in puntos:

        try:

            if not isinstance(punto["punto_id"], str) or not punto["punto_id"].strip():
                raise ValueError("Identificador de punto incorrecto")

            if punto["punto_id"] in ids_puntos:
                raise ValueError("Punto duplicado")

            if not isinstance(punto["capacidad_kg"], int):
                raise ValueError("Tipo de capacidad incorrecto")

            if punto["capacidad_kg"] <= 0:
                raise ValueError("Capacidad incorrecta")

            if punto["estado"] not in ["activo", "mantencion"]:
                raise ValueError("Estado de punto incorrecto")

            if not isinstance(punto["materiales"], list):
                raise ValueError("Materiales incorrectos")

            if not punto["materiales"]:
                raise ValueError("Lista de materiales vacia")

            if any(
                not isinstance(material, str) or not material.strip()
                for material in punto["materiales"]
            ):
                raise ValueError("Material incorrecto")

            puntos_validos.append(punto)

            ids_puntos.add(punto["punto_id"])

        except ValueError as error:

            puntos_rechazados += 1

            logging.warning(f"Punto rechazado: {error}")

    for retiro in retiros:

        try:

            if not isinstance(retiro["retiro_id"], str) or not retiro["retiro_id"].strip():
                raise ValueError("Identificador de retiro incorrecto")

            if retiro["retiro_id"] in ids_retiros:
                raise ValueError("Retiro duplicado")

            if retiro["punto_id"] not in ids_puntos:
                raise ValueError("Retiro sin punto valido asociado")

            if not isinstance(retiro["fecha_retiro"], datetime):
                raise ValueError("Fecha incorrecta")

            if retiro["fecha_retiro"].utcoffset() is None:
                raise ValueError("Fecha sin zona horaria")

            if not isinstance(retiro["kg"], Decimal128):
                raise ValueError("Tipo de kg incorrecto")

            cantidad = retiro["kg"].to_decimal()

            if not cantidad.is_finite() or cantidad <= 0:
                raise ValueError("Cantidad de kg incorrecta")

            if retiro["estado"] not in ["recibido", "validado", "observado"]:
                raise ValueError("Estado de retiro incorrecto")

            retiros_validos.append(retiro)

            ids_retiros.add(retiro["retiro_id"])

        except ValueError as error:

            retiros_rechazados += 1

            logging.warning(f"Retiro rechazado: {error}")

    print("\nValidacion completada")

    print("Puntos validos:", len(puntos_validos))
    print("Puntos rechazados:", puntos_rechazados)

    print("Retiros validos:", len(retiros_validos))
    print("Retiros rechazados:", retiros_rechazados)

    logging.info(f"Puntos validos: {len(puntos_validos)}")
    logging.info(f"Puntos rechazados: {puntos_rechazados}")

    logging.info(f"Retiros validos: {len(retiros_validos)}")
    logging.info(f"Retiros rechazados: {retiros_rechazados}")

    return puntos_validos, retiros_validos


# CONEXION A MONGODB ATLAS

def conectar_mongodb():

    cliente = MongoClient(
        os.getenv("MONGO_URI"),
        serverSelectionTimeoutMS=30000,
        tlsCAFile=certifi.where()
    )

    return cliente


# CREACION DE INDICES UNICOS

def crear_indices(db):

    db.puntos_limpios.create_index(
        "punto_id",
        unique=True
    )

    db.retiros.create_index(
        "retiro_id",
        unique=True
    )

    print("\nIndices unicos creados correctamente")

    logging.info("Indices unicos creados correctamente")


# CARGA DE DATOS EN MONGODB

def cargar_datos(db, puntos, retiros):

    if not puntos or not retiros:
        raise ValueError("Una coleccion no tiene registros validos")

    operaciones_puntos = [

        UpdateOne(
            {"punto_id": punto["punto_id"]},
            {"$set": punto},
            upsert=True
        )

        for punto in puntos
    ]

    operaciones_retiros = [

        UpdateOne(
            {"retiro_id": retiro["retiro_id"]},
            {"$set": retiro},
            upsert=True
        )

        for retiro in retiros
    ]

    resultado_puntos = db.puntos_limpios.bulk_write(
        operaciones_puntos,
        ordered=False
    )

    resultado_retiros = db.retiros.bulk_write(
        operaciones_retiros,
        ordered=False
    )

    print("\nCarga completada")

    print("\nPuntos limpios:")
    print("Insertados:", resultado_puntos.upserted_count)
    print("Coincidentes:", resultado_puntos.matched_count)
    print("Modificados:", resultado_puntos.modified_count)

    print("\nRetiros:")
    print("Insertados:", resultado_retiros.upserted_count)
    print("Coincidentes:", resultado_retiros.matched_count)
    print("Modificados:", resultado_retiros.modified_count)

    logging.info(
        f"Puntos insertados: {resultado_puntos.upserted_count}"
    )

    logging.info(
        f"Puntos coincidentes: {resultado_puntos.matched_count}"
    )

    logging.info(
        f"Puntos modificados: {resultado_puntos.modified_count}"
    )

    logging.info(
        f"Retiros insertados: {resultado_retiros.upserted_count}"
    )

    logging.info(
        f"Retiros coincidentes: {resultado_retiros.matched_count}"
    )

    logging.info(
        f"Retiros modificados: {resultado_retiros.modified_count}"
    )


# VERIFICACION Y CONCILIACION DE CONTEOS

def verificar_carga(db, puntos, retiros):

    total_puntos = db.puntos_limpios.count_documents({})

    total_retiros = db.retiros.count_documents({})

    print("\nVerificacion de carga")

    print("\nPuntos limpios:")
    print("Registros validos de PostgreSQL:", len(puntos))
    print("MongoDB:", total_puntos)
    print("Diferencia:", len(puntos) - total_puntos)

    print("\nRetiros:")
    print("Registros validos de PostgreSQL:", len(retiros))
    print("MongoDB:", total_retiros)
    print("Diferencia:", len(retiros) - total_retiros)

    logging.info(f"Total puntos en MongoDB: {total_puntos}")
    logging.info(f"Total retiros en MongoDB: {total_retiros}")

    logging.info(
        f"Diferencia puntos: {len(puntos) - total_puntos}"
    )

    logging.info(
        f"Diferencia retiros: {len(retiros) - total_retiros}"
    )

    if total_puntos == len(puntos) and total_retiros == len(retiros):

        print("\nConteos conciliados correctamente")

        logging.info("Conteos conciliados correctamente")

    else:

        logging.error("Los conteos no coinciden")

        raise ValueError("Los conteos no coinciden")


# VERIFICACION DE VARIABLES DE ENTORNO

def verificar_variables():

    variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "MONGO_URI",
        "MONGO_DB"
    ]

    for variable in variables:

        if not os.getenv(variable):

            logging.error(f"Variable faltante: {variable}")

            raise ValueError(f"Variable faltante: {variable}")


# EJECUCION PRINCIPAL DEL ETL

if __name__ == "__main__":

    logging.info("Inicio del proceso ETL")

    try:

        verificar_variables()

        # EXTRACCION

        puntos_limpios, retiros = extraer_datos()

        print("Extraccion completada")

        print("Puntos limpios:", len(puntos_limpios))
        print("Retiros:", len(retiros))

        logging.info(f"Puntos leidos: {len(puntos_limpios)}")
        logging.info(f"Retiros leidos: {len(retiros)}")

        # TRANSFORMACION

        puntos, retiros = transformar_datos(
            puntos_limpios,
            retiros
        )

        print("\nTransformacion completada")

        print("Puntos transformados:", len(puntos))
        print("Retiros transformados:", len(retiros))

        logging.info(f"Puntos transformados: {len(puntos)}")
        logging.info(f"Retiros transformados: {len(retiros)}")

        if puntos:

            print("\nEjemplo de punto transformado:")
            print(puntos[0])

        if retiros:

            print("\nEjemplo de retiro transformado:")
            print(retiros[0])

        # VALIDACION

        puntos, retiros = validar_datos(puntos, retiros)

        # CONEXION A MONGODB

        cliente = conectar_mongodb()

        try:

            cliente.admin.command("ping")

            db = cliente[os.getenv("MONGO_DB")]

            print("\nConexion exitosa a MongoDB Atlas")

            logging.info("Conexion exitosa a MongoDB Atlas")

            # INDICES

            crear_indices(db)

            # CARGA

            cargar_datos(db, puntos, retiros)

            # VERIFICACION

            verificar_carga(db, puntos, retiros)

        finally:

            cliente.close()

        print("\nProceso ETL finalizado correctamente")

        logging.info("Proceso ETL finalizado correctamente")

    except Exception as error:

        print("\nError durante el proceso ETL:", type(error).__name__)

        if isinstance(error, NameError):

            print("Detalle:", error)

        logging.error(
            f"Error durante el proceso ETL: {type(error).__name__}"
        )

        raise SystemExit(1)
