# ============================================================
# FASE 4 — ACELERACIÓN CON REDIS
# Proyecto: E-commerce de Alto Rendimiento
# Estructuras usadas:
# 1. Hashes
# 2. Sorted Sets
# 3. Lists
# ============================================================

import redis
from datetime import datetime


def get_redis_client():
    """
    Crea la conexión con Redis local.
    decode_responses=True permite trabajar con strings normales
    en lugar de bytes.
    """

    client = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True
    )

    try:
        client.ping()
        print("Conexión exitosa a Redis.")
        return client

    except redis.ConnectionError:
        print("Error: no se pudo conectar a Redis.")
        print("Verificar que el servidor Redis esté levantado.")
        return None


def create_user_session(r, user_email):
    """
    Crea una sesión de usuario en Redis usando un Hash.
    """

    key = f"session:{user_email}"

    r.hset(key, mapping={
        "user_email": user_email,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat()
    })

    r.expire(key, 1800)

    print(f"Sesión creada: {key}")


def get_user_session(r, user_email):
    """
    Recupera la sesión del usuario desde Redis.
    """

    key = f"session:{user_email}"
    session = r.hgetall(key)

    print("\n========== SESIÓN DE USUARIO ==========")
    print(session)


def add_product_to_cart(r, user_email, sku, quantity):
    """
    Agrega un producto electrónico al carrito activo del usuario usando un Hash.
    """

    key = f"cart:{user_email}"

    r.hincrby(key, sku, quantity)
    r.expire(key, 3600)

    print(f"Producto agregado al carrito: {sku} x{quantity}")


def get_cart(r, user_email):
    """
    Recupera el carrito activo del usuario.
    """

    key = f"cart:{user_email}"
    cart = r.hgetall(key)

    print("\n========== CARRITO ACTIVO ==========")
    print(cart)


def register_product_view(r, sku):
    """
    Registra una visualización de producto usando un Sorted Set.
    """

    key = "top_products:last_hour"

    r.zincrby(key, 1, sku)
    r.expire(key, 3600)

    print(f"Visualización registrada para producto: {sku}")


def get_top_products(r, limit=10):
    """
    Devuelve el ranking de productos electrónicos más vistos.
    """

    key = "top_products:last_hour"

    ranking = r.zrevrange(
        key,
        0,
        limit - 1,
        withscores=True
    )

    print("\n========== TOP PRODUCTOS ELECTRÓNICOS MÁS VISTOS ==========")

    for sku, score in ranking:
        print(f"{sku}: {int(score)} vistas")


def register_event(r, event):
    """
    Registra un evento reciente usando una List.
    """

    key = "recent_events"
    event_text = f"{datetime.now().isoformat()} | {event}"

    r.lpush(key, event_text)
    r.ltrim(key, 0, 19)

    print(f"Evento registrado: {event}")


def get_recent_events(r):
    """
    Recupera los eventos recientes del sistema.
    """

    key = "recent_events"
    events = r.lrange(key, 0, 9)

    print("\n========== EVENTOS RECIENTES ==========")

    for event in events:
        print(event)


if __name__ == "__main__":

    r = get_redis_client()

    if r is not None:

        user_email = "agustin@example.com"

        r.delete(
            f"session:{user_email}",
            f"cart:{user_email}",
            "top_products:last_hour",
            "recent_events"
        )

        create_user_session(r, user_email)
        get_user_session(r, user_email)

        add_product_to_cart(r, user_email, "ELEC-COMPUTER", 1)
        add_product_to_cart(r, user_email, "ELEC-MOUSE", 2)
        get_cart(r, user_email)

        register_product_view(r, "ELEC-COMPUTER")
        register_product_view(r, "ELEC-COMPUTER")
        register_product_view(r, "ELEC-MOUSE")
        register_product_view(r, "ELEC-PHONE")
        register_product_view(r, "ELEC-COMPUTER")
        get_top_products(r)

        register_event(r, f"{user_email} inició sesión")
        register_event(r, f"{user_email} vio ELEC-COMPUTER")
        register_event(r, f"{user_email} agregó ELEC-MOUSE al carrito")
        register_event(r, f"{user_email} consultó el ranking de productos")
        get_recent_events(r)

        print("\nEstructuras Redis ejecutadas correctamente.")
