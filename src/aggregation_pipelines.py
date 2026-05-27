# ============================================================
# FASE 2 — AGGREGATION FRAMEWORK
# Proyecto: E-commerce de Alto Rendimiento
# Base de datos: ecommerce_tp
# Driver: PyMongo
# ============================================================

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pprint import pprint


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


def sales_by_day(db):
    """
    Pipeline 1:
    Calcula cantidad de órdenes pagadas e ingresos totales por día.
    """

    pipeline = [
        {"$match": {"status": "paid"}},
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "total_orders": {"$sum": 1},
                "total_revenue": {"$sum": "$total_amount"}
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "date": "$_id",
                "total_orders": 1,
                "total_revenue": {"$round": ["$total_revenue", 2]}
            }
        }
    ]

    print("\n========== PIPELINE 1: VENTAS TOTALES POR DÍA ==========")

    for doc in db.orders.aggregate(pipeline, allowDiskUse=True):
        pprint(doc)


def best_selling_electronics(db):
    """
    Pipeline 2:
    Calcula los productos electrónicos más vendidos.
    Como todo el catálogo del TP es electrónico, el análisis se
    organiza por subcategoría para que el reporte sea más útil.
    """

    pipeline = [
        {"$match": {"status": "paid"}},
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": {
                    "subcategory": "$items.subcategory",
                    "sku": "$items.sku",
                    "name": "$items.name"
                },
                "units_sold": {"$sum": "$items.quantity"},
                "revenue": {"$sum": "$items.subtotal"}
            }
        },
        {
            "$sort": {
                "units_sold": -1,
                "revenue": -1,
                "_id.subcategory": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "subcategory": "$_id.subcategory",
                "sku": "$_id.sku",
                "name": "$_id.name",
                "units_sold": 1,
                "revenue": {"$round": ["$revenue", 2]}
            }
        }
    ]

    print("\n========== PIPELINE 2: PRODUCTOS ELECTRÓNICOS MÁS VENDIDOS ==========")

    for doc in db.orders.aggregate(pipeline, allowDiskUse=True):
        pprint(doc)


def customer_ranking_by_total_spent(db):
    """
    Pipeline 3:
    Calcula ranking de clientes según gasto total.
    """

    pipeline = [
        {"$match": {"status": "paid"}},
        {
            "$group": {
                "_id": {
                    "user_id": "$user_id",
                    "user_email": "$user_email"
                },
                "orders_count": {"$sum": 1},
                "total_spent": {"$sum": "$total_amount"},
                "average_order_value": {"$avg": "$total_amount"}
            }
        },
        {"$sort": {"total_spent": -1}},
        {
            "$project": {
                "_id": 0,
                "user_id": "$_id.user_id",
                "user_email": "$_id.user_email",
                "orders_count": 1,
                "total_spent": {"$round": ["$total_spent", 2]},
                "average_order_value": {"$round": ["$average_order_value", 2]}
            }
        }
    ]

    print("\n========== PIPELINE 3: RANKING DE CLIENTES POR GASTO TOTAL ==========")

    for doc in db.orders.aggregate(pipeline, allowDiskUse=True):
        pprint(doc)


if __name__ == "__main__":

    db = get_database()

    if db is not None:
        sales_by_day(db)
        best_selling_electronics(db)
        customer_ranking_by_total_spent(db)

        print("\nPipelines ejecutados correctamente.")
