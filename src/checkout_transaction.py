# ============================================================
# FASE 3 — TRANSACCIONES MULTI-DOCUMENTO
# Proceso crítico: Checkout de una orden de compra
# Proyecto: E-commerce de Alto Rendimiento
# Base de datos: ecommerce_tp
# Driver: PyMongo
# ============================================================

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError
from bson import ObjectId, Decimal128
from decimal import Decimal
from datetime import datetime, timezone


MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0"
DB_NAME = "ecommerce_tp"


def get_database():
    """
    Conecta Python con MongoDB usando PyMongo.
    Devuelve la base ecommerce_tp si la conexión es exitosa.
    """

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("Conexión exitosa a MongoDB.")
        return client, client[DB_NAME]

    except (ConnectionFailure, ServerSelectionTimeoutError) as error:
        print("Error: no se pudo conectar a MongoDB.")
        print("Detalle:", error)
        return None, None


def decimal128_to_decimal(value):
    """
    Convierte Decimal128 de MongoDB a Decimal de Python.
    Esto permite calcular totales monetarios de forma precisa.
    """

    return value.to_decimal()


def generate_order_number(db, session):
    """
    Genera un número simple de orden basado en la cantidad actual de órdenes.
    Para un sistema real, convendría usar una secuencia más robusta.
    """

    count = db.orders.count_documents({}, session=session)
    return f"ORD-2026-{count + 1:06d}"


def checkout_order(db, user_email, cart_items, payment_method, provider):
    """
    Ejecuta el checkout de una compra utilizando una transacción ACID.

    Operaciones incluidas:
    1. Validar usuario.
    2. Validar productos electrónicos y stock.
    3. Crear orden.
    4. Descontar stock.
    5. Registrar movimientos de inventario.
    6. Crear pago.
    7. Actualizar daily_sales.
    """

    client = db.client

    with client.start_session() as session:

        try:
            with session.start_transaction():

                user = db.users.find_one(
                    {"email": user_email, "status": "active"},
                    session=session
                )

                if not user:
                    raise Exception(f"Usuario no encontrado o inactivo: {user_email}")

                user_id = user["_id"]
                order_items = []
                total_amount = Decimal("0.00")

                for item in cart_items:

                    sku = item["sku"]
                    quantity = int(item["quantity"])

                    product = db.products.find_one(
                        {"sku": sku, "status": "active", "category": "electronics"},
                        session=session
                    )

                    if not product:
                        raise Exception(f"Producto electrónico no encontrado o inactivo: {sku}")

                    if product["stock"] < quantity:
                        raise Exception(
                            f"Stock insuficiente para {sku}. "
                            f"Stock actual: {product['stock']}, solicitado: {quantity}"
                        )

                    unit_price = decimal128_to_decimal(product["price"])
                    subtotal = unit_price * Decimal(quantity)
                    total_amount += subtotal

                    order_items.append({
                        "product_id": product["_id"],
                        "sku": product["sku"],
                        "name": product["name"],
                        "category": product["category"],
                        "subcategory": product["subcategory"],
                        "quantity": quantity,
                        "unit_price": Decimal128(str(unit_price)),
                        "subtotal": Decimal128(str(subtotal))
                    })

                now = datetime.now(timezone.utc)
                order_id = ObjectId()
                order_number = generate_order_number(db, session)

                order_doc = {
                    "_id": order_id,
                    "order_number": order_number,
                    "user_id": user_id,
                    "user_email": user_email,
                    "status": "paid",
                    "items": order_items,
                    "total_amount": Decimal128(str(total_amount)),
                    "currency": "USD",
                    "shipping_address": user["default_address"],
                    "created_at": now,
                    "paid_at": now
                }

                db.orders.insert_one(order_doc, session=session)

                inventory_movements = []

                for item in order_items:

                    update_result = db.products.update_one(
                        {
                            "_id": item["product_id"],
                            "stock": {"$gte": item["quantity"]}
                        },
                        {
                            "$inc": {"stock": -item["quantity"]},
                            "$set": {"updated_at": now}
                        },
                        session=session
                    )

                    if update_result.modified_count != 1:
                        raise Exception(f"No se pudo descontar stock para {item['sku']}")

                    inventory_movements.append({
                        "_id": ObjectId(),
                        "product_id": item["product_id"],
                        "order_id": order_id,
                        "movement_type": "sale",
                        "quantity": -item["quantity"],
                        "reason": "checkout",
                        "created_at": now
                    })

                db.inventory_movements.insert_many(
                    inventory_movements,
                    session=session
                )

                payment_doc = {
                    "_id": ObjectId(),
                    "order_id": order_id,
                    "user_id": user_id,
                    "provider": provider,
                    "payment_method": payment_method,
                    "status": "approved",
                    "amount": Decimal128(str(total_amount)),
                    "currency": "USD",
                    "transaction_id": f"txn_{order_id}",
                    "created_at": now
                }

                db.payments.insert_one(payment_doc, session=session)

                day_key = now.strftime("%Y-%m-%d")

                db.daily_sales.update_one(
                    {"date": day_key},
                    {
                        "$inc": {
                            "total_orders": 1,
                            "total_revenue": Decimal128(str(total_amount))
                        },
                        "$set": {
                            "currency": "USD",
                            "updated_at": now
                        },
                        "$setOnInsert": {
                            "_id": ObjectId(),
                            "date": day_key
                        }
                    },
                    upsert=True,
                    session=session
                )

                print("\nCheckout ejecutado correctamente.")
                print("Orden creada:", order_number)
                print("Usuario:", user_email)
                print("Total:", f"USD {total_amount}")
                print("Productos:", len(order_items))

                return order_id

        except PyMongoError as error:
            print("\nError de MongoDB durante la transacción.")
            print("La operación fue revertida automáticamente.")
            print("Detalle:", error)

        except Exception as error:
            print("\nError de negocio durante el checkout.")
            print("La operación fue revertida automáticamente.")
            print("Detalle:", error)


def validate_checkout(db, order_id):
    """
    Muestra la orden, el pago y los movimientos de inventario generados.
    """

    if order_id is None:
        print("\nNo hay orden para validar.")
        return

    print("\n========== VALIDACIÓN POST-CHECKOUT ==========")

    order = db.orders.find_one({"_id": order_id})
    payment = db.payments.find_one({"order_id": order_id})
    movements = list(db.inventory_movements.find({"order_id": order_id}))

    print("Orden:")
    print({
        "order_number": order["order_number"],
        "status": order["status"],
        "total_amount": order["total_amount"],
        "items": len(order["items"])
    })

    print("\nPago:")
    print({
        "provider": payment["provider"],
        "payment_method": payment["payment_method"],
        "status": payment["status"],
        "amount": payment["amount"]
    })

    print("\nMovimientos de inventario:")
    for movement in movements:
        print({
            "product_id": movement["product_id"],
            "quantity": movement["quantity"],
            "reason": movement["reason"]
        })


if __name__ == "__main__":

    client, db = get_database()

    if db is not None:

        # Carrito de ejemplo con productos electrónicos simples.
        cart = [
            {"sku": "ELEC-MOUSE", "quantity": 1},
            {"sku": "ELEC-KEYBOARD", "quantity": 1}
        ]

        order_id = checkout_order(
            db=db,
            user_email="agustin@example.com",
            cart_items=cart,
            payment_method="credit_card",
            provider="stripe"
        )

        validate_checkout(db, order_id)

        client.close()
