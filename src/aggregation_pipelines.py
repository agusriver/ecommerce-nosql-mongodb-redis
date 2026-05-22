# ============================================================
# FASE 2 — AGGREGATION FRAMEWORK
# Proyecto: E-commerce de Alto Rendimiento
# Base de datos: ecommerce_tp
# Driver: PyMongo
# ============================================================

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pprint import pprint


# ============================================================
# 1. CONFIGURACIÓN DE CONEXIÓN
# ============================================================

MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0"
DB_NAME = "ecommerce_tp"


def get_database():
    """
    Conecta la aplicación Python con MongoDB usando PyMongo.
    Devuelve la base de datos ecommerce_tp si la conexión es exitosa.
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


# ============================================================
# 2. PIPELINE 1 — VENTAS TOTALES POR DÍA
# ============================================================

def sales_by_day(db):
    """
    Reporte:
    Calcula la cantidad de órdenes pagadas y el ingreso total por día.

    Colección base:
    orders

    Conceptos aplicados:
    - $match: filtra solo órdenes pagadas.
    - $group: agrupa por fecha.
    - $sum: suma órdenes e ingresos.
    - $sort: ordena cronológicamente.
    - $project: da formato final al resultado.
    """

    pipeline = [
        {
            "$match": {
                "status": "paid"
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "total_orders": {
                    "$sum": 1
                },
                "total_revenue": {
                    "$sum": "$total_amount"
                }
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "date": "$_id",
                "total_orders": 1,
                "total_revenue": 1
            }
        }
    ]

    print("\n========== PIPELINE 1: VENTAS TOTALES POR DÍA ==========")

    results = db.orders.aggregate(pipeline, allowDiskUse=True)

    for doc in results:
        pprint(doc)


# ============================================================
# 3. PIPELINE 2 — PRODUCTOS MÁS VENDIDOS POR CATEGORÍA
# ============================================================

def best_selling_products_by_category(db):
    """
    Reporte:
    Calcula qué productos vendieron más unidades y generaron más ingresos,
    agrupados por categoría.

    Colección base:
    orders

    Conceptos aplicados:
    - $match: filtra órdenes pagadas.
    - $unwind: descompone el array items.
    - $group: agrupa por categoría, SKU y nombre del producto.
    - $sum: calcula unidades vendidas e ingresos.
    - $sort: ordena por unidades vendidas e ingresos.
    - $project: limpia el formato de salida.
    """

    pipeline = [
        {
            "$match": {
                "status": "paid"
            }
        },
        {
            "$unwind": "$items"
        },
        {
            "$group": {
                "_id": {
                    "category": "$items.category",
                    "sku": "$items.sku",
                    "name": "$items.name"
                },
                "units_sold": {
                    "$sum": "$items.quantity"
                },
                "revenue": {
                    "$sum": "$items.subtotal"
                }
            }
        },
        {
            "$sort": {
                "_id.category": 1,
                "units_sold": -1,
                "revenue": -1
            }
        },
        {
            "$project": {
                "_id": 0,
                "category": "$_id.category",
                "sku": "$_id.sku",
                "name": "$_id.name",
                "units_sold": 1,
                "revenue": 1
            }
        }
    ]

    print("\n========== PIPELINE 2: PRODUCTOS MÁS VENDIDOS POR CATEGORÍA ==========")

    results = db.orders.aggregate(pipeline, allowDiskUse=True)

    for doc in results:
        pprint(doc)


# ============================================================
# 4. PIPELINE 3 — RANKING DE CLIENTES POR GASTO TOTAL
# ============================================================

def customer_ranking_by_total_spent(db):
    """
    Reporte:
    Calcula el ranking de clientes según el gasto total realizado.

    Colección base:
    orders

    Conceptos aplicados:
    - $match: filtra órdenes pagadas.
    - $group: agrupa por usuario.
    - $sum: calcula gasto total y cantidad de órdenes.
    - $avg: calcula ticket promedio.
    - $sort: ordena de mayor a menor gasto.
    - $project: da formato final al resultado.
    """

    pipeline = [
        {
            "$match": {
                "status": "paid"
            }
        },
        {
            "$group": {
                "_id": {
                    "user_id": "$user_id",
                    "user_email": "$user_email"
                },
                "orders_count": {
                    "$sum": 1
                },
                "total_spent": {
                    "$sum": "$total_amount"
                },
                "average_order_value": {
                    "$avg": "$total_amount"
                }
            }
        },
        {
            "$sort": {
                "total_spent": -1
            }
        },
        {
            "$project": {
                "_id": 0,
                "user_id": "$_id.user_id",
                "user_email": "$_id.user_email",
                "orders_count": 1,
                "total_spent": 1,
                "average_order_value": 1
            }
        }
    ]

    print("\n========== PIPELINE 3: RANKING DE CLIENTES POR GASTO TOTAL ==========")

    results = db.orders.aggregate(pipeline, allowDiskUse=True)

    for doc in results:
        pprint(doc)


# ============================================================
# 5. PROGRAMA PRINCIPAL
# ============================================================

if __name__ == "__main__":

    db = get_database()

    if db is not None:
        sales_by_day(db)
        best_selling_products_by_category(db)
        customer_ranking_by_total_spent(db)

        print("\nPipelines ejecutados correctamente.")