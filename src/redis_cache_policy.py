# ============================================================
# FASE 4 — GESTIÓN DE CACHÉ CON REDIS
# Proyecto: E-commerce de Alto Rendimiento
#
# Objetivo:
# - Implementar políticas de expiración con TTL.
# - Implementar invalidación coherente con el negocio.
#
# Estructuras:
# - Hash para sesiones.
# - Hash para carritos activos.
# - Sorted Set para ranking de productos vistos.
# - List para eventos recientes.
# ============================================================

import redis
from datetime import datetime


# ============================================================
# 1. CONFIGURACIÓN DE REDIS
# ============================================================

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0


# TTL definidos en segundos
SESSION_TTL_SECONDS = 30 * 60       # 30 minutos
CART_TTL_SECONDS = 60 * 60          # 1 hora
TOP_PRODUCTS_TTL_SECONDS = 60 * 60  # 1 hora

MAX_RECENT_EVENTS = 20


def get_redis_client():
    """
    Crea y valida la conexión con Redis.
    decode_responses=True permite trabajar con strings normales
    en lugar de bytes.
    """

    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
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
# 2. SESIONES CON TTL
# ============================================================

def create_session(r, user_email):
    """
    Crea una sesión de usuario como Hash en Redis.

    Clave:
    session:{user_email}

    Política:
    - TTL de 30 minutos.
    - Si el usuario no tiene actividad, la sesión expira.
    """

    key = f"session:{user_email}"

    r.hset(key, mapping={
        "user_email": user_email,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat()
    })

    r.expire(key, SESSION_TTL_SECONDS)

    print(f"Sesión creada con TTL: {key}")
    print(f"TTL sesión: {r.ttl(key)} segundos")


def refresh_session(r, user_email):
    """
    Refresca la sesión ante actividad del usuario.

    Cada vez que el usuario interactúa con la plataforma,
    se actualiza last_activity y se renueva el TTL.
    """

    key = f"session:{user_email}"

    if r.exists(key):
        r.hset(key, "last_activity", datetime.now().isoformat())
        r.expire(key, SESSION_TTL_SECONDS)

        print(f"Sesión renovada: {key}")
        print(f"Nuevo TTL sesión: {r.ttl(key)} segundos")
    else:
        print("No existe sesión activa para renovar.")


def invalidate_session(r, user_email):
    """
    Invalida la sesión del usuario.

    Caso de negocio:
    - El usuario cierra sesión.
    - La sesión debe eliminarse inmediatamente.
    """

    key = f"session:{user_email}"

    deleted = r.delete(key)

    if deleted:
        print(f"Sesión invalidada: {key}")
    else:
        print(f"No existía sesión para invalidar: {key}")


# ============================================================
# 3. CARRITO ACTIVO CON TTL
# ============================================================

def add_to_cart(r, user_email, sku, quantity):
    """
    Agrega productos al carrito activo.

    Clave:
    cart:{user_email}

    Política:
    - TTL de 1 hora.
    - Cada modificación del carrito renueva el TTL.
    """

    key = f"cart:{user_email}"

    r.hincrby(key, sku, quantity)
    r.expire(key, CART_TTL_SECONDS)

    print(f"Producto agregado al carrito: {sku} x{quantity}")
    print(f"TTL carrito: {r.ttl(key)} segundos")


def get_cart(r, user_email):
    """
    Recupera el carrito activo del usuario.
    """

    key = f"cart:{user_email}"
    cart = r.hgetall(key)

    print("\n========== CARRITO ACTIVO ==========")
    print(cart)
    print(f"TTL carrito: {r.ttl(key)} segundos")


def invalidate_cart_after_checkout(r, user_email):
    """
    Invalida el carrito luego de un checkout exitoso.

    Caso de negocio:
    - El usuario confirma la compra.
    - La orden se persiste en MongoDB.
    - El carrito temporal ya no debe existir en Redis.
    """

    key = f"cart:{user_email}"

    deleted = r.delete(key)

    if deleted:
        print(f"Carrito invalidado después del checkout: {key}")
    else:
        print(f"No existía carrito para invalidar: {key}")


# ============================================================
# 4. RANKING DE PRODUCTOS CON TTL
# ============================================================

def register_product_view(r, sku):
    """
    Registra una visualización de producto.

    Clave:
    top_products:last_hour

    Política:
    - TTL de 1 hora.
    - Representa popularidad reciente.
    """

    key = "top_products:last_hour"

    r.zincrby(key, 1, sku)
    r.expire(key, TOP_PRODUCTS_TTL_SECONDS)

    print(f"Vista registrada: {sku}")
    print(f"TTL ranking: {r.ttl(key)} segundos")


def get_top_products(r):
    """
    Consulta ranking de productos más vistos.
    """

    key = "top_products:last_hour"

    ranking = r.zrevrange(key, 0, 9, withscores=True)

    print("\n========== TOP PRODUCTS LAST HOUR ==========")

    for sku, score in ranking:
        print(f"{sku}: {int(score)} vistas")

    print(f"TTL ranking: {r.ttl(key)} segundos")


# ============================================================
# 5. EVENTOS RECIENTES CON LIST + TRIM
# ============================================================

def register_recent_event(r, event):
    """
    Registra un evento reciente del sistema.

    Clave:
    recent_events

    Política:
    - No se usa TTL principal.
    - Se usa LTRIM para evitar crecimiento indefinido.
    - Se conservan solo los últimos MAX_RECENT_EVENTS eventos.
    """

    key = "recent_events"
    event_text = f"{datetime.now().isoformat()} | {event}"

    r.lpush(key, event_text)
    r.ltrim(key, 0, MAX_RECENT_EVENTS - 1)

    print(f"Evento registrado: {event}")


def get_recent_events(r):
    """
    Muestra los eventos recientes.
    """

    key = "recent_events"
    events = r.lrange(key, 0, 9)

    print("\n========== EVENTOS RECIENTES ==========")

    for event in events:
        print(event)

    print(f"Cantidad actual de eventos guardados: {r.llen(key)}")


# ============================================================
# 6. PROGRAMA PRINCIPAL
# ============================================================

if __name__ == "__main__":

    r = get_redis_client()

    if r is not None:

        user_email = "agustin@example.com"

        # Limpiamos claves de prueba para ejecutar el script varias veces
        r.delete(
            f"session:{user_email}",
            f"cart:{user_email}",
            "top_products:last_hour",
            "recent_events"
        )

        print("\n========== 1. SESIÓN CON TTL ==========")
        create_session(r, user_email)
        refresh_session(r, user_email)

        print("\n========== 2. CARRITO CON TTL ==========")
        add_to_cart(r, user_email, "NOTE-THINK-X1", 1)
        add_to_cart(r, user_email, "MOUSE-LOGI-MX", 2)
        get_cart(r, user_email)

        print("\n========== 3. RANKING CON TTL ==========")
        register_product_view(r, "NOTE-THINK-X1")
        register_product_view(r, "NOTE-THINK-X1")
        register_product_view(r, "PHONE-SAMSUNG-S24")
        register_product_view(r, "MOUSE-LOGI-MX")
        get_top_products(r)

        print("\n========== 4. EVENTOS RECIENTES ==========")
        register_recent_event(r, f"{user_email} inició sesión")
        register_recent_event(r, f"{user_email} agregó NOTE-THINK-X1 al carrito")
        register_recent_event(r, f"{user_email} agregó MOUSE-LOGI-MX al carrito")
        register_recent_event(r, f"{user_email} consultó top_products:last_hour")
        get_recent_events(r)

        print("\n========== 5. INVALIDACIÓN POR NEGOCIO ==========")

        # Caso de negocio: checkout exitoso
        invalidate_cart_after_checkout(r, user_email)

        # Caso de negocio: logout
        invalidate_session(r, user_email)

        print("\n========== VALIDACIÓN FINAL ==========")
        print(f"Existe carrito: {bool(r.exists(f'cart:{user_email}'))}")
        print(f"Existe sesión: {bool(r.exists(f'session:{user_email}'))}")
        print("Gestión de caché ejecutada correctamente.")