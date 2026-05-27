# ============================================================
# SEED — E-COMMERCE NoSQL
# Proyecto: Trabajo Práctico Integrador
#
# Objetivo:
# - Poblar MongoDB con datos realistas para defensa académica.
# - Trabajar solamente con productos electrónicos.
# - Usar nombres simples de productos para que la defensa sea clara.
# - Generar múltiples órdenes por día, pagos, movimientos de inventario
#   y ventas diarias agregadas.
# ============================================================

from pymongo import MongoClient
from bson import ObjectId, Decimal128
from datetime import datetime, timezone, timedelta
from collections import defaultdict


MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0"
DB_NAME = "ecommerce_tp"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def reset_database():
    """
    Limpia las colecciones principales para evitar duplicados
    al ejecutar el seed varias veces.
    """

    collections = [
        "users",
        "products",
        "orders",
        "payments",
        "inventory_movements",
        "daily_sales"
    ]

    for collection in collections:
        db[collection].delete_many({})

    print("Base ecommerce_tp limpiada correctamente.")


def create_users():
    """
    Crea usuarios de prueba con direcciones embebidas.
    """

    users_data = [
        ("Agustín Peña", "agustin@example.com", "Buenos Aires", "Av. Corrientes 1500", "C1042"),
        ("Lucía Gómez", "lucia@example.com", "Buenos Aires", "Av. Santa Fe 2500", "C1425"),
        ("Mateo Rodríguez", "mateo@example.com", "Rosario", "Bv. Oroño 900", "S2000"),
        ("Sofía Martínez", "sofia@example.com", "Córdoba", "Colón 400", "X5000"),
        ("Tomás Fernández", "tomas@example.com", "Mendoza", "San Martín 700", "M5500"),
        ("Camila Suárez", "camila@example.com", "La Plata", "Mitre 350", "B1900"),
        ("Juan Pérez", "juan@example.com", "Buenos Aires", "Rivadavia 1100", "C1033"),
        ("Valentina Ruiz", "valentina@example.com", "Mar del Plata", "Belgrano 800", "B7600"),
        ("Nicolás Torres", "nicolas@example.com", "Salta", "Independencia 120", "A4400"),
        ("Martina López", "martina@example.com", "Tucumán", "Sarmiento 500", "T4000"),
        ("Pedro Naón", "pedro@example.com", "Pilar", "Panamericana Km 50", "B1629"),
        ("Matías Roberti", "matias@example.com", "Buenos Aires", "Cabildo 2200", "C1428"),
    ]

    users = []

    for i, (name, email, city, street, zip_code) in enumerate(users_data, start=1):
        users.append({
            "_id": ObjectId(),
            "name": name,
            "email": email,
            "status": "active",
            "created_at": datetime(2026, 5, i, 9, 0, tzinfo=timezone.utc),
            "default_address": {
                "street": street,
                "city": city,
                "country": "Argentina",
                "zip_code": zip_code
            }
        })

    db.users.insert_many(users)
    print(f"Usuarios insertados: {len(users)}")
    return users


def create_products():
    """
    Crea un catálogo de productos electrónicos con nombres simples.
    Todos los documentos usan category='electronics'.
    """

    catalog = [
        ("ELEC-COMPUTER", "Computadora", "computacion", "1200.00", 80, [("ram", "16GB"), ("cpu", "Intel i7"), ("storage", "512GB SSD")]),
        ("ELEC-PHONE", "Celular", "telefonia", "850.00", 100, [("storage", "256GB"), ("camera", "50MP"), ("battery", "4000mAh")]),
        ("ELEC-TABLET", "Tablet", "tablets", "650.00", 70, [("storage", "128GB"), ("screen", "10 inch"), ("connection", "WiFi")]),
        ("ELEC-MONITOR", "Monitor", "perifericos", "180.00", 120, [("size", "24 inch"), ("resolution", "Full HD"), ("refresh_rate", "75Hz")]),
        ("ELEC-KEYBOARD", "Teclado", "perifericos", "45.00", 180, [("layout", "QWERTY"), ("connection", "USB"), ("backlight", "true")]),
        ("ELEC-MOUSE", "Mouse", "perifericos", "35.00", 220, [("connection", "Bluetooth"), ("dpi", "4000"), ("color", "black")]),
        ("ELEC-HEADPHONES", "Auriculares", "audio", "120.00", 130, [("connection", "Bluetooth"), ("noise_cancelling", "true"), ("battery_life", "24h")]),
        ("ELEC-SPEAKER", "Parlante", "audio", "95.00", 100, [("connection", "Bluetooth"), ("power", "20W"), ("water_resistant", "true")]),
        ("ELEC-WEBCAM", "Webcam", "perifericos", "70.00", 95, [("resolution", "Full HD"), ("fps", "30"), ("connection", "USB")]),
        ("ELEC-MICROPHONE", "Micrófono", "audio", "110.00", 85, [("connection", "USB"), ("pattern", "cardioid"), ("color", "black")]),
        ("ELEC-ROUTER", "Router", "redes", "100.00", 90, [("wifi", "WiFi 6"), ("ports", "4"), ("band", "dual")]),
        ("ELEC-SSD", "Disco SSD", "almacenamiento", "90.00", 200, [("capacity", "1TB"), ("type", "SSD"), ("interface", "NVMe")]),
        ("ELEC-RAM", "Memoria RAM", "componentes", "75.00", 160, [("capacity", "16GB"), ("type", "DDR4"), ("speed", "3200MHz")]),
        ("ELEC-CHARGER", "Cargador", "accesorios", "25.00", 260, [("type", "USB-C"), ("power", "65W"), ("fast_charge", "true")]),
        ("ELEC-HDMI", "Cable HDMI", "accesorios", "12.00", 350, [("length", "2m"), ("type", "HDMI"), ("version", "2.1")]),
        ("ELEC-HUB", "Hub USB-C", "accesorios", "60.00", 140, [("ports", "7"), ("connection", "USB-C"), ("hdmi", "true")]),
        ("ELEC-PRINTER", "Impresora", "oficina", "160.00", 70, [("type", "inkjet"), ("connection", "WiFi"), ("color_print", "true")]),
        ("ELEC-WATCH", "Reloj inteligente", "wearables", "210.00", 110, [("gps", "true"), ("battery_life", "7d"), ("water_resistant", "true")]),
        ("ELEC-CONSOLE", "Consola", "gaming", "500.00", 65, [("storage", "1TB"), ("resolution", "4K"), ("controllers", "1")]),
        ("ELEC-CONTROLLER", "Joystick", "gaming", "65.00", 150, [("connection", "Bluetooth"), ("battery_life", "30h"), ("color", "black")]),
        ("ELEC-CAMERA", "Cámara", "fotografia", "320.00", 55, [("resolution", "24MP"), ("storage", "SD"), ("video", "4K")]),
        ("ELEC-TV", "Televisor", "video", "700.00", 45, [("size", "50 inch"), ("resolution", "4K"), ("smart_tv", "true")]),
        ("ELEC-PROJECTOR", "Proyector", "video", "430.00", 40, [("resolution", "Full HD"), ("brightness", "3500lm"), ("connection", "HDMI")]),
        ("ELEC-CARDREADER", "Lector de tarjetas", "accesorios", "18.00", 190, [("connection", "USB-C"), ("formats", "SD/microSD"), ("portable", "true")]),
    ]

    products = []
    now = datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)

    for i, (sku, name, subcategory, price, stock, specs_pairs) in enumerate(catalog):
        products.append({
            "_id": ObjectId(),
            "sku": sku,
            "name": name,
            "category": "electronics",
            "subcategory": subcategory,
            "brand": "ElectroStore",
            "status": "active",
            "price": Decimal128(price),
            "currency": "USD",
            "stock": stock,
            "specs": [{"k": k, "v": v} for k, v in specs_pairs],
            "created_at": now + timedelta(minutes=i * 10),
            "updated_at": now + timedelta(minutes=i * 10)
        })

    db.products.insert_many(products)
    print(f"Productos insertados: {len(products)}")
    return products


def decimal_to_float(value):
    """
    Convierte Decimal128 a float para cálculos internos del seed.
    """
    return float(value.to_decimal())


def create_order_item(product, quantity):
    """
    Crea un item embebido dentro de una orden.
    Se guarda snapshot histórico del producto.
    """

    unit_price = product["price"]
    subtotal = decimal_to_float(unit_price) * quantity

    return {
        "product_id": product["_id"],
        "sku": product["sku"],
        "name": product["name"],
        "category": product["category"],
        "subcategory": product["subcategory"],
        "quantity": quantity,
        "unit_price": unit_price,
        "subtotal": Decimal128(f"{subtotal:.2f}")
    }


def create_orders_payments_movements(users, products):
    """
    Crea órdenes realistas con varias ventas por día.
    Todas las órdenes contienen productos electrónicos.
    """

    products_by_sku = {p["sku"]: p for p in products}
    users_by_email = {u["email"]: u for u in users}

    daily_order_counts = {
        "2026-05-10": 4,
        "2026-05-11": 3,
        "2026-05-12": 5,
        "2026-05-13": 2,
        "2026-05-14": 6,
        "2026-05-15": 4,
        "2026-05-16": 5,
        "2026-05-17": 3,
        "2026-05-18": 7,
        "2026-05-19": 4,
        "2026-05-20": 5,
    }

    # Patrones de compra realistas: algunos tickets altos y muchos accesorios.
    baskets = [
        [("ELEC-COMPUTER", 1), ("ELEC-MOUSE", 1)],
        [("ELEC-PHONE", 1), ("ELEC-CHARGER", 1)],
        [("ELEC-MONITOR", 1), ("ELEC-KEYBOARD", 1), ("ELEC-MOUSE", 1)],
        [("ELEC-HDMI", 3), ("ELEC-CARDREADER", 1)],
        [("ELEC-HEADPHONES", 1), ("ELEC-SPEAKER", 1)],
        [("ELEC-SSD", 1), ("ELEC-RAM", 1)],
        [("ELEC-TABLET", 1), ("ELEC-HUB", 1)],
        [("ELEC-WEBCAM", 1), ("ELEC-MICROPHONE", 1)],
        [("ELEC-ROUTER", 1), ("ELEC-HDMI", 2)],
        [("ELEC-WATCH", 1), ("ELEC-CHARGER", 1)],
        [("ELEC-TV", 1), ("ELEC-HDMI", 2)],
        [("ELEC-PRINTER", 1), ("ELEC-CARDREADER", 2)],
        [("ELEC-CONSOLE", 1), ("ELEC-CONTROLLER", 2)],
        [("ELEC-PROJECTOR", 1), ("ELEC-HDMI", 2)],
        [("ELEC-CHARGER", 2), ("ELEC-HUB", 1)],
    ]

    providers = ["stripe", "mercadopago"]
    payment_methods = ["credit_card", "debit_card", "wallet"]

    users_emails = [u["email"] for u in users]
    orders = []
    payments = []
    inventory_movements = []

    order_index = 1

    for day_index, (date_key, count) in enumerate(daily_order_counts.items()):
        for n in range(count):
            email = users_emails[(order_index - 1) % len(users_emails)]
            basket = baskets[(order_index - 1) % len(baskets)]
            provider = providers[(order_index - 1) % len(providers)]
            payment_method = payment_methods[(order_index - 1) % len(payment_methods)]

            created_at = datetime.fromisoformat(f"{date_key}T{9 + (n * 2):02d}:{(15 + n * 7) % 60:02d}:00+00:00")
            paid_at = created_at + timedelta(minutes=2)

            user = users_by_email[email]
            order_id = ObjectId()
            order_number = f"ORD-2026-{order_index:06d}"

            items = []
            total = 0.0

            for sku, quantity in basket:
                product = products_by_sku[sku]
                item = create_order_item(product, quantity)
                items.append(item)
                total += decimal_to_float(item["subtotal"])

                inventory_movements.append({
                    "_id": ObjectId(),
                    "product_id": product["_id"],
                    "order_id": order_id,
                    "movement_type": "sale",
                    "quantity": -quantity,
                    "reason": "checkout",
                    "created_at": paid_at
                })

            orders.append({
                "_id": order_id,
                "order_number": order_number,
                "user_id": user["_id"],
                "user_email": user["email"],
                "status": "paid",
                "items": items,
                "total_amount": Decimal128(f"{total:.2f}"),
                "currency": "USD",
                "shipping_address": user["default_address"],
                "created_at": created_at,
                "paid_at": paid_at
            })

            payments.append({
                "_id": ObjectId(),
                "order_id": order_id,
                "user_id": user["_id"],
                "provider": provider,
                "payment_method": payment_method,
                "status": "approved",
                "amount": Decimal128(f"{total:.2f}"),
                "currency": "USD",
                "transaction_id": f"txn_{order_index:06d}",
                "created_at": paid_at
            })

            order_index += 1

    db.orders.insert_many(orders)
    db.payments.insert_many(payments)
    db.inventory_movements.insert_many(inventory_movements)

    # Descontar stock en products según los movimientos generados.
    for movement in inventory_movements:
        db.products.update_one(
            {"_id": movement["product_id"]},
            {"$inc": {"stock": movement["quantity"]}}
        )

    print(f"Órdenes insertadas: {len(orders)}")
    print(f"Pagos insertados: {len(payments)}")
    print(f"Movimientos de inventario insertados: {len(inventory_movements)}")

    return orders, payments, inventory_movements


def create_extra_inventory_movements(products):
    """
    Agrega movimientos de inventario adicionales para que la colección
    inventory_movements sea más realista.

    Además de las ventas generadas por checkout, un e-commerce real
    también tiene reposiciones, ajustes manuales y devoluciones.
    """

    products_by_sku = {p["sku"]: p for p in products}

    extra_movements_plan = [
        # Reposiciones de stock por proveedor
        ("ELEC-COMPUTER", "restock", 10, "supplier_delivery", "2026-05-09T08:00:00Z"),
        ("ELEC-PHONE", "restock", 15, "supplier_delivery", "2026-05-09T08:15:00Z"),
        ("ELEC-MOUSE", "restock", 30, "supplier_delivery", "2026-05-09T08:30:00Z"),
        ("ELEC-KEYBOARD", "restock", 25, "supplier_delivery", "2026-05-09T08:45:00Z"),
        ("ELEC-MONITOR", "restock", 12, "supplier_delivery", "2026-05-09T09:00:00Z"),

        # Ajustes manuales de inventario
        ("ELEC-HDMI", "adjustment", -2, "inventory_correction", "2026-05-12T18:00:00Z"),
        ("ELEC-HEADPHONES", "adjustment", -1, "damaged_item", "2026-05-13T16:30:00Z"),

        # Devoluciones de clientes
        ("ELEC-MOUSE", "return", 1, "customer_return", "2026-05-15T11:20:00Z"),
        ("ELEC-KEYBOARD", "return", 1, "customer_return", "2026-05-16T14:10:00Z"),
    ]

    extra_movements = []

    for sku, movement_type, quantity, reason, date_str in extra_movements_plan:
        product = products_by_sku.get(sku)

        if not product:
            print(f"Producto no encontrado para movimiento extra: {sku}")
            continue

        created_at = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

        movement = {
            "_id": ObjectId(),
            "product_id": product["_id"],
            "order_id": None,
            "movement_type": movement_type,
            "quantity": quantity,
            "reason": reason,
            "created_at": created_at
        }

        extra_movements.append(movement)

        db.products.update_one(
            {"_id": product["_id"]},
            {"$inc": {"stock": quantity}}
        )

    if extra_movements:
        db.inventory_movements.insert_many(extra_movements)

    print(f"Movimientos extra de inventario insertados: {len(extra_movements)}")

    return extra_movements


def create_daily_sales(orders):
    """
    Genera la colección daily_sales a partir de las órdenes pagadas.
    Varios días tienen múltiples órdenes, por lo que el reporte es
    más realista y defendible.
    """

    daily = defaultdict(lambda: {"total_orders": 0, "total_revenue": 0.0})

    for order in orders:
        if order["status"] != "paid":
            continue

        date_key = order["created_at"].strftime("%Y-%m-%d")
        daily[date_key]["total_orders"] += 1
        daily[date_key]["total_revenue"] += decimal_to_float(order["total_amount"])

    daily_sales = []

    for date_key, values in sorted(daily.items()):
        daily_sales.append({
            "_id": ObjectId(),
            "date": date_key,
            "total_orders": values["total_orders"],
            "total_revenue": Decimal128(f"{values['total_revenue']:.2f}"),
            "currency": "USD",
            "updated_at": datetime.now(timezone.utc)
        })

    db.daily_sales.insert_many(daily_sales)
    print(f"Daily sales insertadas: {len(daily_sales)}")
    return daily_sales


def create_indexes():
    """
    Crea índices principales para consultas críticas.
    """

    db.products.create_index([("category", 1), ("status", 1), ("price", -1)])
    db.products.create_index([("specs.k", 1), ("specs.v", 1)])
    db.orders.create_index([("user_email", 1), ("created_at", -1)])
    db.orders.create_index([("status", 1), ("created_at", 1)])
    db.orders.create_index([("user_id", 1), ("created_at", -1)])
    db.payments.create_index([("order_id", 1)])
    db.inventory_movements.create_index([("product_id", 1), ("created_at", -1)])

    print("Índices principales creados correctamente.")


def validate_seed():
    """
    Muestra la cantidad de documentos por colección.
    """

    print("\n================ VALIDACIÓN FINAL ================")
    print(f"Users: {db.users.count_documents({})}")
    print(f"Products: {db.products.count_documents({})}")
    print(f"Orders: {db.orders.count_documents({})}")
    print(f"Payments: {db.payments.count_documents({})}")
    print(f"Inventory movements: {db.inventory_movements.count_documents({})}")
    print(f"Daily sales: {db.daily_sales.count_documents({})}")
    print("==================================================")


if __name__ == "__main__":

    reset_database()

    users = create_users()
    products = create_products()
    orders, payments, movements = create_orders_payments_movements(users, products)

    extra_movements = create_extra_inventory_movements(products)

    daily_sales = create_daily_sales(orders)
    create_indexes()
    validate_seed()

    print("\nSeed ejecutado correctamente.")
