# ============================================================
# FASE 2 — OPTIMIZACIÓN CON ÍNDICES ESR
# Proyecto: E-commerce de Alto Rendimiento
# Base de datos: ecommerce_tp
# Driver: PyMongo
# ============================================================

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pprint import pprint


MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0"
DB_NAME = "ecommerce_tp"


def get_database():
    """
    Conecta Python con MongoDB mediante PyMongo.
    Devuelve la base ecommerce_tp si la conexión es exitosa.
    """

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("Conexión exitosa a MongoDB.")
        return client[DB_NAME]

    except (ConnectionFailure, ServerSelectionTimeoutError) as error:
        print("Error: no se pudo conectar a MongoDB.")
        print("Detalle:", error)
        return None


def create_indexes(db):
    """
    Crea los índices necesarios para optimizar consultas críticas
    siguiendo la regla ESR.
    """

    print("\n========== CREACIÓN DE ÍNDICES ==========")

    idx1 = db.products.create_index([
        ("category", ASCENDING),
        ("status", ASCENDING),
        ("price", DESCENDING)
    ])
    print("Índice creado en products:", idx1)

    idx2 = db.products.create_index([
        ("specs.k", ASCENDING),
        ("specs.v", ASCENDING)
    ])
    print("Índice creado en products:", idx2)

    idx3 = db.orders.create_index([
        ("user_email", ASCENDING),
        ("created_at", DESCENDING)
    ])
    print("Índice creado en orders:", idx3)

    idx4 = db.orders.create_index([
        ("status", ASCENDING),
        ("created_at", ASCENDING)
    ])
    print("Índice creado en orders:", idx4)

    idx5 = db.payments.create_index([
        ("order_id", ASCENDING)
    ])
    print("Índice creado en payments:", idx5)

    idx6 = db.inventory_movements.create_index([
        ("product_id", ASCENDING),
        ("created_at", DESCENDING)
    ])
    print("Índice creado en inventory_movements:", idx6)


def show_indexes(db):
    """
    Muestra los índices existentes en las colecciones principales.
    """

    print("\n========== ÍNDICES EN products ==========")
    pprint(list(db.products.list_indexes()))

    print("\n========== ÍNDICES EN orders ==========")
    pprint(list(db.orders.list_indexes()))

    print("\n========== ÍNDICES EN payments ==========")
    pprint(list(db.payments.list_indexes()))

    print("\n========== ÍNDICES EN inventory_movements ==========")
    pprint(list(db.inventory_movements.list_indexes()))


def run_critical_queries(db):
    """
    Ejecuta consultas críticas para validar los índices.
    """

    print("\n========== CONSULTA 1: CATÁLOGO ELECTRÓNICO POR PRECIO ==========")

    products = db.products.find(
        {
            "category": "electronics",
            "status": "active"
        },
        {
            "_id": 0,
            "sku": 1,
            "name": 1,
            "subcategory": 1,
            "price": 1,
            "stock": 1
        }
    ).sort("price", DESCENDING)

    for product in products:
        pprint(product)


    print("\n========== CONSULTA 2: BÚSQUEDA POR ATTRIBUTE PATTERN ==========")

    specs_products = db.products.find(
        {
            "category": "electronics",
            "specs.k": "ram",
            "specs.v": "16GB"
        },
        {
            "_id": 0,
            "sku": 1,
            "name": 1,
            "subcategory": 1,
            "brand": 1,
            "specs": 1
        }
    )

    for product in specs_products:
        pprint(product)


    print("\n========== CONSULTA 3: HISTORIAL DE ÓRDENES POR USUARIO ==========")

    orders = db.orders.find(
        {
            "user_email": "agustin@example.com"
        },
        {
            "_id": 0,
            "order_number": 1,
            "status": 1,
            "total_amount": 1,
            "created_at": 1
        }
    ).sort("created_at", DESCENDING)

    for order in orders:
        pprint(order)


def explain_catalog_query(db):
    """
    Ejecuta explain usando db.command().
    """

    print("\n========== EXPLAIN: CONSULTA DE CATÁLOGO ELECTRÓNICO ==========")

    explain_result = db.command({
        "explain": {
            "find": "products",
            "filter": {
                "category": "electronics",
                "status": "active"
            },
            "sort": {
                "price": -1
            },
            "hint": {
                "category": 1,
                "status": 1,
                "price": -1
            }
        },
        "verbosity": "executionStats"
    })

    execution_stats = explain_result.get("executionStats", {})

    print("Índice esperado: category_1_status_1_price_-1")
    print("nReturned:", execution_stats.get("nReturned"))
    print("totalDocsExamined:", execution_stats.get("totalDocsExamined"))
    print("totalKeysExamined:", execution_stats.get("totalKeysExamined"))


if __name__ == "__main__":

    db = get_database()

    if db is not None:
        create_indexes(db)
        show_indexes(db)
        run_critical_queries(db)

        # Si en tu entorno explain no da error, podés descomentar:
        # explain_catalog_query(db)

        print("\nOptimización con índices ejecutada correctamente.")
