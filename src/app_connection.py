# ============================================================
# FASE 2 — CAPA DE APLICACIÓN CON PYMONGO
# Proyecto: E-commerce de Alto Rendimiento
# Base de datos: ecommerce_tp
# ============================================================

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0"
DB_NAME = "ecommerce_tp"


def get_database():
    """
    Crea la conexión con MongoDB y devuelve la base de datos ecommerce_tp.
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


def validate_collections(db):
    """
    Muestra la cantidad de documentos existentes en cada colección principal.
    """

    collections = [
        "users",
        "products",
        "orders",
        "payments",
        "inventory_movements",
        "daily_sales"
    ]

    print("\n========== VALIDACIÓN DE COLECCIONES ==========")

    for collection_name in collections:
        count = db[collection_name].count_documents({})
        print(f"{collection_name}: {count} documentos")

    print("================================================")


def show_active_products(db):
    """
    Consulta productos electrónicos activos del catálogo.
    """

    print("\n========== PRODUCTOS ELECTRÓNICOS ACTIVOS ==========")

    products = db.products.find(
        {"status": "active", "category": "electronics"},
        {"_id": 0, "sku": 1, "name": 1, "subcategory": 1, "price": 1, "stock": 1}
    ).sort("price", -1)

    for product in products:
        print(product)


def show_orders_by_user(db, user_email):
    """
    Consulta el historial de órdenes de un usuario específico.
    """

    print(f"\n========== ÓRDENES DE {user_email} ==========")

    orders = db.orders.find(
        {"user_email": user_email},
        {"_id": 0, "order_number": 1, "status": 1, "total_amount": 1, "created_at": 1}
    ).sort("created_at", -1)

    for order in orders:
        print(order)


def search_products_by_spec(db, key, value):
    """
    Consulta productos usando el Attribute Pattern.
    Busca dentro del array specs por pares {k, v}.
    """

    print(f"\n========== PRODUCTOS CON {key} = {value} ==========")

    products = db.products.find(
        {"specs.k": key, "specs.v": value, "category": "electronics"},
        {"_id": 0, "sku": 1, "name": 1, "subcategory": 1, "brand": 1, "specs": 1}
    )

    for product in products:
        print(product)


if __name__ == "__main__":

    db = get_database()

    if db is not None:
        validate_collections(db)
        show_active_products(db)
        show_orders_by_user(db, "agustin@example.com")
        search_products_by_spec(db, "ram", "16GB")
