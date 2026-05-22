# ============================================================
# SEED INICIAL — TP E-commerce de Alto Rendimiento
# MongoDB + Redis
# Base de datos: ecommerce_tp
# Driver: PyMongo
# ============================================================

from pymongo import MongoClient
from bson import ObjectId, Decimal128
from datetime import datetime, timezone


# ============================================================
# 1. CONEXIÓN A MONGODB
# ============================================================

# Conexión local a MongoDB.
# En MongoDB Compass normalmente usamos mongodb://localhost:27017
client = MongoClient("mongodb://localhost:27017/?replicaSet=rs0")

# Seleccionamos la base de datos del TP.
db = client["ecommerce_tp"]


# ============================================================
# 2. LIMPIEZA DE COLECCIONES
# ============================================================

# Borramos datos previos para poder ejecutar el seed varias veces
# sin duplicar información.
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


# ============================================================
# 3. CARGA DE USUARIOS
# ============================================================

users = [
    {
        "_id": ObjectId(),
        "name": "Agustín Peña",
        "email": "agustin@example.com",
        "status": "active",
        "created_at": datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc),
        "default_address": {
            "street": "Av. Corrientes 1500",
            "city": "Buenos Aires",
            "country": "Argentina",
            "zip_code": "C1042"
        }
    },
    {
        "_id": ObjectId(),
        "name": "Lucía Fernández",
        "email": "lucia@example.com",
        "status": "active",
        "created_at": datetime(2026, 5, 2, 11, 30, tzinfo=timezone.utc),
        "default_address": {
            "street": "Av. Santa Fe 2500",
            "city": "Buenos Aires",
            "country": "Argentina",
            "zip_code": "C1425"
        }
    },
    {
        "_id": ObjectId(),
        "name": "Mateo Rodríguez",
        "email": "mateo@example.com",
        "status": "active",
        "created_at": datetime(2026, 5, 3, 9, 15, tzinfo=timezone.utc),
        "default_address": {
            "street": "Bv. Oroño 900",
            "city": "Rosario",
            "country": "Argentina",
            "zip_code": "S2000"
        }
    },
    {
        "_id": ObjectId(),
        "name": "Sofía Lann",
        "email": "sofia@example.com",
        "status": "inactive",
        "created_at": datetime(2026, 5, 4, 16, 45, tzinfo=timezone.utc),
        "default_address": {
            "street": "San Martín 120",
            "city": "Córdoba",
            "country": "Argentina",
            "zip_code": "X5000"
        }
    }
]

db.users.insert_many(users)

agustin_id = users[0]["_id"]
lucia_id = users[1]["_id"]
mateo_id = users[2]["_id"]
sofia_id = users[3]["_id"]

print("Usuarios insertados:", db.users.count_documents({}))


# ============================================================
# 4. CARGA DE PRODUCTOS
# ============================================================
# En products aplicamos Attribute Pattern.
# Las características variables se guardan en specs como pares {k, v}.

products = [
    {
        "_id": ObjectId(),
        "sku": "NOTE-THINK-X1",
        "name": "Lenovo ThinkPad X1",
        "category": "electronics",
        "subcategory": "laptops",
        "brand": "Lenovo",
        "status": "active",
        "price": Decimal128("1299.99"),
        "currency": "USD",
        "stock": 42,
        "specs": [
            {"k": "ram", "v": "16GB"},
            {"k": "cpu", "v": "Intel i7"},
            {"k": "storage", "v": "512GB SSD"},
            {"k": "screen", "v": "14 inch"}
        ],
        "created_at": datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "sku": "MOUSE-LOGI-MX",
        "name": "Mouse Logitech MX Master",
        "category": "electronics",
        "subcategory": "accessories",
        "brand": "Logitech",
        "status": "active",
        "price": Decimal128("85.00"),
        "currency": "USD",
        "stock": 120,
        "specs": [
            {"k": "connection", "v": "Bluetooth"},
            {"k": "dpi", "v": "8000"},
            {"k": "color", "v": "black"}
        ],
        "created_at": datetime(2026, 5, 1, 10, 10, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 5, 1, 10, 10, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "sku": "KEY-MECH-RED",
        "name": "Teclado Mecánico Redragon",
        "category": "electronics",
        "subcategory": "keyboards",
        "brand": "Redragon",
        "status": "active",
        "price": Decimal128("50.00"),
        "currency": "USD",
        "stock": 75,
        "specs": [
            {"k": "switch", "v": "red"},
            {"k": "layout", "v": "QWERTY"},
            {"k": "backlight", "v": "RGB"}
        ],
        "created_at": datetime(2026, 5, 1, 10, 20, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 5, 1, 10, 20, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "sku": "MON-24-SAMSUNG",
        "name": "Monitor Samsung 24 pulgadas",
        "category": "electronics",
        "subcategory": "monitors",
        "brand": "Samsung",
        "status": "active",
        "price": Decimal128("150.00"),
        "currency": "USD",
        "stock": 60,
        "specs": [
            {"k": "size", "v": "24 inch"},
            {"k": "resolution", "v": "Full HD"},
            {"k": "refresh_rate", "v": "75Hz"}
        ],
        "created_at": datetime(2026, 5, 2, 9, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 5, 2, 9, 0, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "sku": "TSHIRT-UCA-BLUE",
        "name": "Remera UCA Azul",
        "category": "apparel",
        "subcategory": "tshirts",
        "brand": "UCA Store",
        "status": "active",
        "price": Decimal128("25.00"),
        "currency": "USD",
        "stock": 200,
        "specs": [
            {"k": "size", "v": "M"},
            {"k": "color", "v": "blue"},
            {"k": "fabric", "v": "cotton"}
        ],
        "created_at": datetime(2026, 5, 2, 12, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 5, 2, 12, 0, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "sku": "PHONE-SAMSUNG-S24",
        "name": "Samsung Galaxy S24",
        "category": "electronics",
        "subcategory": "smartphones",
        "brand": "Samsung",
        "status": "active",
        "price": Decimal128("899.99"),
        "currency": "USD",
        "stock": 30,
        "specs": [
            {"k": "storage", "v": "256GB"},
            {"k": "camera", "v": "50MP"},
            {"k": "battery", "v": "4000mAh"}
        ],
        "created_at": datetime(2026, 5, 3, 8, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 5, 3, 8, 0, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "sku": "HEAD-SONY-XM5",
        "name": "Sony WH-1000XM5",
        "category": "electronics",
        "subcategory": "headphones",
        "brand": "Sony",
        "status": "active",
        "price": Decimal128("399.99"),
        "currency": "USD",
        "stock": 15,
        "specs": [
            {"k": "noise_cancelling", "v": "true"},
            {"k": "connection", "v": "Bluetooth"},
            {"k": "battery_life", "v": "30h"}
        ],
        "created_at": datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "sku": "OLD-CAMERA-001",
        "name": "Cámara Digital Antigua",
        "category": "electronics",
        "subcategory": "cameras",
        "brand": "Generic",
        "status": "discontinued",
        "price": Decimal128("120.00"),
        "currency": "USD",
        "stock": 0,
        "specs": [
            {"k": "resolution", "v": "12MP"},
            {"k": "storage", "v": "SD Card"}
        ],
        "created_at": datetime(2026, 4, 1, 8, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 4, 15, 8, 0, tzinfo=timezone.utc)
    }
]

db.products.insert_many(products)

thinkpad_id = products[0]["_id"]
mouse_id = products[1]["_id"]
keyboard_id = products[2]["_id"]
monitor_id = products[3]["_id"]
tshirt_id = products[4]["_id"]
phone_id = products[5]["_id"]
headphones_id = products[6]["_id"]

print("Productos insertados:", db.products.count_documents({}))


# ============================================================
# 5. CARGA DE ÓRDENES
# ============================================================
# En orders embebemos los items comprados.
# Esto permite conservar un snapshot histórico del producto.

orders = [
    {
        "_id": ObjectId(),
        "order_number": "ORD-2026-000001",
        "user_id": agustin_id,
        "user_email": "agustin@example.com",
        "status": "paid",
        "items": [
            {
                "product_id": thinkpad_id,
                "sku": "NOTE-THINK-X1",
                "name": "Lenovo ThinkPad X1",
                "category": "electronics",
                "quantity": 1,
                "unit_price": Decimal128("1299.99"),
                "subtotal": Decimal128("1299.99")
            },
            {
                "product_id": mouse_id,
                "sku": "MOUSE-LOGI-MX",
                "name": "Mouse Logitech MX Master",
                "category": "electronics",
                "quantity": 1,
                "unit_price": Decimal128("85.00"),
                "subtotal": Decimal128("85.00")
            }
        ],
        "total_amount": Decimal128("1384.99"),
        "currency": "USD",
        "shipping_address": users[0]["default_address"],
        "created_at": datetime(2026, 5, 10, 10, 30, tzinfo=timezone.utc),
        "paid_at": datetime(2026, 5, 10, 10, 31, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "order_number": "ORD-2026-000002",
        "user_id": lucia_id,
        "user_email": "lucia@example.com",
        "status": "paid",
        "items": [
            {
                "product_id": monitor_id,
                "sku": "MON-24-SAMSUNG",
                "name": "Monitor Samsung 24 pulgadas",
                "category": "electronics",
                "quantity": 1,
                "unit_price": Decimal128("150.00"),
                "subtotal": Decimal128("150.00")
            },
            {
                "product_id": keyboard_id,
                "sku": "KEY-MECH-RED",
                "name": "Teclado Mecánico Redragon",
                "category": "electronics",
                "quantity": 1,
                "unit_price": Decimal128("50.00"),
                "subtotal": Decimal128("50.00")
            }
        ],
        "total_amount": Decimal128("200.00"),
        "currency": "USD",
        "shipping_address": users[1]["default_address"],
        "created_at": datetime(2026, 5, 11, 15, 0, tzinfo=timezone.utc),
        "paid_at": datetime(2026, 5, 11, 15, 2, tzinfo=timezone.utc)
    }
]

db.orders.insert_many(orders)

order1_id = orders[0]["_id"]
order2_id = orders[1]["_id"]

print("Órdenes insertadas:", db.orders.count_documents({}))


# ============================================================
# 6. CARGA DE PAGOS
# ============================================================

payments = [
    {
        "_id": ObjectId(),
        "order_id": order1_id,
        "user_id": agustin_id,
        "provider": "stripe",
        "payment_method": "credit_card",
        "status": "approved",
        "amount": Decimal128("1384.99"),
        "currency": "USD",
        "transaction_id": "txn_000001",
        "created_at": datetime(2026, 5, 10, 10, 31, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "order_id": order2_id,
        "user_id": lucia_id,
        "provider": "mercadopago",
        "payment_method": "debit_card",
        "status": "approved",
        "amount": Decimal128("200.00"),
        "currency": "USD",
        "transaction_id": "txn_000002",
        "created_at": datetime(2026, 5, 11, 15, 2, tzinfo=timezone.utc)
    }
]

db.payments.insert_many(payments)

print("Pagos insertados:", db.payments.count_documents({}))


# ============================================================
# 7. CARGA DE MOVIMIENTOS DE INVENTARIO
# ============================================================

inventory_movements = [
    {
        "_id": ObjectId(),
        "product_id": thinkpad_id,
        "order_id": order1_id,
        "movement_type": "sale",
        "quantity": -1,
        "reason": "checkout",
        "created_at": datetime(2026, 5, 10, 10, 31, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "product_id": mouse_id,
        "order_id": order1_id,
        "movement_type": "sale",
        "quantity": -1,
        "reason": "checkout",
        "created_at": datetime(2026, 5, 10, 10, 31, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "product_id": monitor_id,
        "order_id": order2_id,
        "movement_type": "sale",
        "quantity": -1,
        "reason": "checkout",
        "created_at": datetime(2026, 5, 11, 15, 2, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId(),
        "product_id": keyboard_id,
        "order_id": order2_id,
        "movement_type": "sale",
        "quantity": -1,
        "reason": "checkout",
        "created_at": datetime(2026, 5, 11, 15, 2, tzinfo=timezone.utc)
    }
]

db.inventory_movements.insert_many(inventory_movements)

print("Movimientos de inventario insertados:", db.inventory_movements.count_documents({}))


# ============================================================
# 8. CARGA DE DAILY SALES
# ============================================================
# Esta colección funciona como una vista materializada inicial.

daily_sales = [
    {
        "_id": "2026-05-10",
        "date": datetime(2026, 5, 10, 0, 0, tzinfo=timezone.utc),
        "total_orders": 1,
        "total_revenue": Decimal128("1384.99"),
        "by_category": [
            {
                "category": "electronics",
                "orders": 1,
                "revenue": Decimal128("1384.99")
            }
        ],
        "updated_at": datetime(2026, 5, 10, 23, 59, tzinfo=timezone.utc)
    },
    {
        "_id": "2026-05-11",
        "date": datetime(2026, 5, 11, 0, 0, tzinfo=timezone.utc),
        "total_orders": 1,
        "total_revenue": Decimal128("200.00"),
        "by_category": [
            {
                "category": "electronics",
                "orders": 1,
                "revenue": Decimal128("200.00")
            }
        ],
        "updated_at": datetime(2026, 5, 11, 23, 59, tzinfo=timezone.utc)
    }
]

db.daily_sales.insert_many(daily_sales)

print("Daily sales insertadas:", db.daily_sales.count_documents({}))


# ============================================================
# 9. VALIDACIÓN FINAL
# ============================================================

print("\n================ VALIDACIÓN FINAL ================")
print("Users:", db.users.count_documents({}))
print("Products:", db.products.count_documents({}))
print("Orders:", db.orders.count_documents({}))
print("Payments:", db.payments.count_documents({}))
print("Inventory movements:", db.inventory_movements.count_documents({}))
print("Daily sales:", db.daily_sales.count_documents({}))
print("==================================================")
print("Seed ejecutado correctamente.")