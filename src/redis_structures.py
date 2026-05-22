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


# ============================================================
# 1. CONEXIÓN A REDIS
# ============================================================

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


# ============================================================
# 2. HASH — SESIÓN DE USUARIO
# ============================================================

def create_user_session(r, user_email):
    """
    Crea una sesión de usuario en Redis usando un Hash.

    Redis Key:
    session:{user_email}

    Campos:
    - user_email
    - status
    - created_at
    - last_activity

    Se aplica TTL para que la sesión expire automáticamente.
    """

    key = f"session:{user_email}"

    r.hset(key, mapping={
        "user_email": user_email,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat()
    })

    # La sesión expira en 30 minutos
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


# ============================================================
# 3. HASH — CARRITO ACTIVO
# ============================================================

def add_product_to_cart(r, user_email, sku, quantity):
    """
    Agrega un producto al carrito activo del usuario usando un Hash.

    Redis Key:
    cart:{user_email}

    Cada campo del Hash representa un SKU y su cantidad.
    """

    key = f"cart:{user_email}"

    # Incrementa la cantidad del producto dentro del carrito
    r.hincrby(key, sku, quantity)

    # El carrito expira en 1 hora si el usuario no completa la compra
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


# ============================================================
# 4. SORTED SET — PRODUCTOS MÁS VISTOS
# ============================================================

def register_product_view(r, sku):
    """
    Registra una visualización de producto usando un Sorted Set.

    Redis Key:
    top_products:last_hour

    Cada producto tiene un score que representa la cantidad de vistas.
    """

    key = "top_products:last_hour"

    # Incrementa en 1 el score del producto
    r.zincrby(key, 1, sku)

    # El ranking expira cada 1 hora
    r.expire(key, 3600)

    print(f"Visualización registrada para producto: {sku}")


def get_top_products(r, limit=10):
    """
    Devuelve el ranking de productos más vistos.
    """

    key = "top_products:last_hour"

    ranking = r.zrevrange(
        key,
        0,
        limit - 1,
        withscores=True
    )

    print("\n========== TOP PRODUCTOS MÁS VISTOS ==========")

    for sku, score in ranking:
        print(f"{sku}: {int(score)} vistas")


# ============================================================
# 5. LIST — EVENTOS RECIENTES
# ============================================================

def register_event(r, event):
    """
    Registra un evento reciente usando una List.

    Redis Key:
    recent_events

    Se usa LPUSH para insertar al inicio de la lista.
    Se usa LTRIM para conservar solo los últimos 20 eventos.
    """

    key = "recent_events"

    event_text = f"{datetime.now().isoformat()} | {event}"

    r.lpush(key, event_text)

    # Mantiene solo los 20 eventos más recientes
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


# ============================================================
# 6. PROGRAMA PRINCIPAL
# ============================================================

if __name__ == "__main__":

    r = get_redis_client()

    if r is not None:

        # Limpiamos datos previos de prueba
        r.delete(
            "session:agustin@example.com",
            "cart:agustin@example.com",
            "top_products:last_hour",
            "recent_events"
        )

        # --------------------------------------------
        # HASH: sesión
        # --------------------------------------------
        create_user_session(r, "agustin@example.com")
        get_user_session(r, "agustin@example.com")

        # --------------------------------------------
        # HASH: carrito activo
        # --------------------------------------------
        add_product_to_cart(r, "agustin@example.com", "NOTE-THINK-X1", 1)
        add_product_to_cart(r, "agustin@example.com", "MOUSE-LOGI-MX", 2)
        get_cart(r, "agustin@example.com")

        # --------------------------------------------
        # SORTED SET: ranking de productos vistos
        # --------------------------------------------
        register_product_view(r, "NOTE-THINK-X1")
        register_product_view(r, "NOTE-THINK-X1")
        register_product_view(r, "MOUSE-LOGI-MX")
        register_product_view(r, "PHONE-SAMSUNG-S24")
        register_product_view(r, "NOTE-THINK-X1")
        get_top_products(r)

        # --------------------------------------------
        # LIST: eventos recientes
        # --------------------------------------------
        register_event(r, "agustin@example.com inició sesión")
        register_event(r, "agustin@example.com vio NOTE-THINK-X1")
        register_event(r, "agustin@example.com agregó MOUSE-LOGI-MX al carrito")
        register_event(r, "agustin@example.com consultó el ranking de productos")
        get_recent_events(r)

        print("\nEstructuras Redis ejecutadas correctamente.")