# Trabajo Práctico Integrador — Diseño de Sistemas NoSQL de Alto Rendimiento

## Descripción general

El dominio del proyecto se enfoca en un e-commerce de productos electrónicos simples, como computadora, celular, mouse, teclado, monitor, auriculares, router, cable HDMI y otros accesorios tecnológicos. Esta decisión permite mantener el caso de negocio claro y coherente durante todo el trabajo.

Este proyecto implementa una plataforma de **e-commerce de alto rendimiento** utilizando **MongoDB** y **Redis**.

MongoDB se utiliza como fuente de verdad persistente para almacenar usuarios, productos electrónicos, órdenes, pagos, movimientos de inventario y reportes de ventas. Redis se utiliza como capa de velocidad para manejar datos temporales o de alta frecuencia, como sesiones, carritos activos, rankings de productos más vistos y eventos recientes.

El objetivo del trabajo es demostrar el diseño de una arquitectura NoSQL moderna, aplicando modelado documental, integración con PyMongo, pipelines de agregación, índices ESR, transacciones multi-documento, análisis CAP, estrategia de sharding y aceleración con Redis.

---

## Tecnologías utilizadas

- Python
- PyMongo
- MongoDB
- MongoDB Compass
- Redis
- Git / GitHub

---

## Estructura del proyecto

```txt
ecommerce_tp/
│
├── README.md
├── requirements.txt
├── .gitignore
│
└── src/
    ├── seed_ecommerce.py
    ├── app_connection.py
    ├── aggregation_pipelines.py
    ├── optimization_indexes.py
    ├── checkout_transaction.py
    ├── redis_structures.py
    └── redis_cache_policy.py
```

---

## Instalación de dependencias

Para instalar las dependencias necesarias:

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene:

```txt
pymongo
redis
```

---

## Configuración de MongoDB

Para ejecutar transacciones multi-documento, MongoDB debe estar configurado como un **Replica Set**.

En este proyecto se configuró un Replica Set local de un solo nodo llamado:

```txt
rs0
```

La URI utilizada por PyMongo es:

```txt
mongodb://localhost:27017/?replicaSet=rs0
```

---

## Configuración de Redis

Redis debe estar levantado localmente en:

```txt
localhost:6379
```

Para verificar que Redis está funcionando:

```bash
redis-cli ping
```

Resultado esperado:

```txt
PONG
```

## Orden recomendado de ejecución

```bash
python src/seed_ecommerce.py
python src/app_connection.py
python src/aggregation_pipelines.py
python src/optimization_indexes.py
python src/checkout_transaction.py
python src/redis_structures.py
python src/redis_cache_policy.py

```

---

## Scripts principales

### 1. Seed inicial de MongoDB

Carga datos iniciales en la base `ecommerce_tp`.

```bash
python src/seed_ecommerce.py
```

Este script crea datos de prueba en las colecciones:

- `users`
- `products`
- `orders`
- `payments`
- `inventory_movements`
- `daily_sales`

Resultado esperado del seed:

- 12 usuarios
- 24 productos electrónicos
- 48 órdenes
- 48 pagos
- 109 movimientos de inventario
- 11 días con ventas agregadas

El seed genera múltiples órdenes por día para simular un comportamiento más realista de un e-commerce.

---

### 2. Conexión con PyMongo

Valida la conexión entre Python y MongoDB.

```bash
python src/app_connection.py
```

Este script consulta productos activos, órdenes por usuario y productos por atributos variables.

---

### 3. Pipelines de agregación

Ejecuta tres pipelines usando **Aggregation Framework**.

```bash
python src/aggregation_pipelines.py
```

Pipelines implementados:

1. Ventas totales por día.
2. Productos electrónicos más vendidos.
3. Ranking de clientes por gasto total.

---

### 4. Optimización con índices ESR

Crea índices compuestos y multikey para consultas críticas.

```bash
python src/optimization_indexes.py
```

Índices principales:

```js
db.products.createIndex({ category: 1, status: 1, price: -1 })
db.products.createIndex({ "specs.k": 1, "specs.v": 1 })
db.orders.createIndex({ user_email: 1, created_at: -1 })
db.orders.createIndex({ status: 1, created_at: 1 })
db.payments.createIndex({ order_id: 1 })
db.inventory_movements.createIndex({ product_id: 1, created_at: -1 })
```

---

### 5. Transacción de checkout

Implementa una transacción multi-documento en MongoDB.

```bash
python src/checkout_transaction.py
```

El proceso de checkout incluye:

- validación de usuario;
- validación de stock;
- creación de orden;
- creación de pago;
- descuento de stock;
- registro de movimientos de inventario;
- actualización de vista materializada.

---

### 6. Estructuras Redis

Implementa distintas estructuras de datos en Redis.

```bash
python src/redis_structures.py
```

Estructuras utilizadas:

- Hashes para sesiones y carritos activos.
- Sorted Sets para ranking de productos más vistos.
- Lists para eventos recientes.

---

### 7. Gestión de caché con Redis

Implementa TTL e invalidación de caché.

```bash
python src/redis_cache_policy.py
```

Políticas aplicadas:

- sesiones con TTL de 30 minutos;
- carritos con TTL de 1 hora;
- ranking de productos con TTL de 1 hora;
- invalidación del carrito después del checkout;
- invalidación de sesión al cerrar sesión.

---

## Decisiones técnicas principales

### MongoDB como fuente de verdad

MongoDB almacena los datos persistentes y críticos del sistema: usuarios, productos, órdenes, pagos e inventario.

### Redis como capa de velocidad

Redis se utiliza para datos temporales o de alta frecuencia, evitando sobrecargar MongoDB con operaciones volátiles.

### Prioridad CP para operaciones críticas

El sistema prioriza **consistencia** y **tolerancia a particiones** en el checkout, pagos e inventario. Ante una partición de red, se prefiere rechazar temporalmente una compra antes que permitir inconsistencias de stock o pagos.

### Sharding propuesto

Para la colección `orders`, se propone la shard key:

```js
{ user_id: "hashed" }
```

Esta clave permite distribuir las órdenes entre shards y evitar hotspots generados por campos secuenciales como `created_at` u `order_number`.

---

## Repositorio

https://github.com/agustinpena20/ecommerce-nosql-mongodb-redis

## Integrantes

- Agustín Peña
- Matías Roberti
