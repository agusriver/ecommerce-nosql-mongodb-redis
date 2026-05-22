# ============================================================
# FASE 2 — CAPA DE APLICACIÓN CON PYMONGO
# Proyecto: E-commerce de Alto Rendimiento
# Base de datos: ecommerce_tp
# ============================================================

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


# ============================================================
# 1. CONFIGURACIÓN DE CONEXIÓN
# ============================================================

# URI de conexión al servidor local de MongoDB.
# Es la misma conexión que usamos en MongoDB Compass:
# mongodb://localhost:27017
MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0"
# Nombre de la base de datos del TP
DB_NAME = "ecommerce_tp"


# ============================================================
# 2. FUNCIÓN PARA CONECTARSE A MONGODB
# ============================================================

def get_database():
    """
    Crea la conexión con MongoDB y devuelve la base de datos ecommerce_tp.

    Esta función centraliza la conexión para que el resto de la aplicación
    pueda reutilizarla sin repetir código.
    """

    try:
        # serverSelectionTimeoutMS evita que Python quede esperando demasiado
        # si MongoDB no está levantado.
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

        # Verificamos que el servidor responda correctamente.
        client.admin.command("ping")

        print("Conexión exitosa a MongoDB.")

        # Seleccionamos y devolvemos la base de datos del proyecto.
        db = client[DB_NAME]
        return db

    except (ConnectionFailure, ServerSelectionTimeoutError) as error:
        print("Error: no se pudo conectar a MongoDB.")
        print("Detalle:", error)
        return None


# ============================================================
# 3. FUNCIÓN DE VALIDACIÓN GENERAL
# ============================================================

def validate_collections(db):
    """
    Muestra la cantidad de documentos existentes en cada colección principal.
    Sirve para verificar que el seed se haya cargado correctamente.
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


# ============================================================
# 4. CONSULTAS BÁSICAS DESDE PYTHON
# ============================================================

def show_active_products(db):
    """
    Consulta productos activos del catálogo.
    Esta consulta valida que Python puede leer documentos desde MongoDB.
    """

    print("\n========== PRODUCTOS ACTIVOS ==========")

    products = db.products.find(
        {"status": "active"},
        {"_id": 0, "sku": 1, "name": 1, "category": 1, "price": 1, "stock": 1}
    )

    for product in products:
        print(product)


def show_orders_by_user(db, user_email):
    """
    Consulta el historial de órdenes de un usuario específico.
    El resultado se ordena de más reciente a más antiguo.
    """

    print(f"\n========== ÓRDENES DE {user_email} ==========")

    orders = db.orders.find(
        {"user_email": user_email}
    ).sort("created_at", -1)

    for order in orders:
        print({
            "order_number": order.get("order_number"),
            "status": order.get("status"),
            "total_amount": order.get("total_amount"),
            "created_at": order.get("created_at")
        })


def search_products_by_spec(db, key, value):
    """
    Consulta productos usando el Attribute Pattern.
    Busca dentro del array specs por pares {k, v}.
    """

    print(f"\n========== PRODUCTOS CON {key} = {value} ==========")

    products = db.products.find(
        {
            "specs.k": key,
            "specs.v": value
        },
        {
            "_id": 0,
            "sku": 1,
            "name": 1,
            "brand": 1,
            "specs": 1
        }
    )

    for product in products:
        print(product)


# ============================================================
# 5. PROGRAMA PRINCIPAL
# ============================================================

if __name__ == "__main__":

    # Obtenemos la conexión a la base de datos
    db = get_database()

    # Si la conexión fue exitosa, ejecutamos pruebas básicas
    if db is not None:
        validate_collections(db)

        show_active_products(db)

        show_orders_by_user(db, "agustin@example.com")

        search_products_by_spec(db, "ram", "16GB")