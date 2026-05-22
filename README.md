\# Trabajo Práctico Integrador — Diseño de Sistemas NoSQL de Alto Rendimiento



\## Descripción general



Este proyecto implementa una plataforma de e-commerce de alto rendimiento utilizando MongoDB y Redis.



MongoDB se utiliza como fuente de verdad persistente para almacenar usuarios, productos, órdenes, pagos, movimientos de inventario y reportes de ventas. Redis se utiliza como capa de velocidad para manejar datos temporales o de alta frecuencia, como sesiones, carritos activos, rankings de productos más vistos y eventos recientes.



El objetivo del trabajo es demostrar el diseño de una arquitectura NoSQL moderna, aplicando modelado documental, integración con PyMongo, pipelines de agregación, índices ESR, transacciones multi-documento, análisis CAP, estrategia de sharding y aceleración con Redis.



\---



\## Tecnologías utilizadas



\- Python

\- PyMongo

\- MongoDB

\- MongoDB Compass

\- Redis

\- Git / GitHub



\---



\## Estructura del proyecto



```txt

ecommerce\_tp/

│

├── README.md

├── requirements.txt

├── .gitignore

│

├── src/

│   ├── seed\_ecommerce.py

│   ├── app\_connection.py

│   ├── aggregation\_pipelines.py

│   ├── optimization\_indexes.py

│   ├── checkout\_transaction.py

│   ├── redis\_structures.py

│   └── redis\_cache\_policy.py

│

├── docs/

└── exports/



Instalación de dependencias



Para instalar las dependencias necesarias:



pip install -r requirements.txt



El archivo requirements.txt contiene:



pymongo

redis

Configuración de MongoDB



Para ejecutar transacciones multi-documento, MongoDB debe estar configurado como un Replica Set.



En este proyecto se configuró un Replica Set local de un solo nodo llamado:



rs0



La URI utilizada por PyMongo es:



mongodb://localhost:27017/?replicaSet=rs0

Configuración de Redis



Redis debe estar levantado localmente en:



localhost:6379



Para verificar que Redis está funcionando:



redis-cli ping



Resultado esperado:



PONG

Scripts principales

1\. Seed inicial de MongoDB



Carga datos iniciales en la base ecommerce\_tp.



python src/seed\_ecommerce.py



Este script crea datos de prueba en las colecciones:



users

products

orders

payments

inventory\_movements

daily\_sales

2\. Conexión con PyMongo



Valida la conexión entre Python y MongoDB.



python src/app\_connection.py



Este script consulta productos activos, órdenes por usuario y productos por atributos variables.



3\. Pipelines de agregación



Ejecuta tres pipelines usando Aggregation Framework.



python src/aggregation\_pipelines.py



Pipelines implementados:



Ventas totales por día.

Productos más vendidos por categoría.

Ranking de clientes por gasto total.

4\. Optimización con índices ESR



Crea índices compuestos y multikey para consultas críticas.



python src/optimization\_indexes.py



Índices principales:



db.products.createIndex({ category: 1, status: 1, price: -1 })

db.products.createIndex({ "specs.k": 1, "specs.v": 1 })

db.orders.createIndex({ user\_email: 1, created\_at: -1 })

db.orders.createIndex({ status: 1, created\_at: 1 })

db.payments.createIndex({ order\_id: 1 })

db.inventory\_movements.createIndex({ product\_id: 1, created\_at: -1 })

5\. Transacción de checkout



Implementa una transacción multi-documento en MongoDB.



python src/checkout\_transaction.py



El proceso de checkout incluye:



validación de usuario;

validación de stock;

creación de orden;

creación de pago;

descuento de stock;

registro de movimientos de inventario;

actualización de vista materializada.

6\. Estructuras Redis



Implementa distintas estructuras de datos en Redis.



python src/redis\_structures.py



Estructuras utilizadas:



Hashes para sesiones y carritos activos.

Sorted Sets para ranking de productos más vistos.

Lists para eventos recientes.

7\. Gestión de caché con Redis



Implementa TTL e invalidación de caché.



python src/redis\_cache\_policy.py



Políticas aplicadas:



sesiones con TTL de 30 minutos;

carritos con TTL de 1 hora;

ranking de productos con TTL de 1 hora;

invalidación del carrito después del checkout;

invalidación de sesión al cerrar sesión.

Decisiones técnicas principales

MongoDB como fuente de verdad



MongoDB almacena los datos persistentes y críticos del sistema: usuarios, productos, órdenes, pagos e inventario.



Redis como capa de velocidad



Redis se utiliza para datos temporales o de alta frecuencia, evitando sobrecargar MongoDB con operaciones volátiles.



Prioridad CP para operaciones críticas



El sistema prioriza consistencia y tolerancia a particiones en el checkout, pagos e inventario. Ante una partición de red, se prefiere rechazar temporalmente una compra antes que permitir inconsistencias de stock o pagos.



Sharding propuesto



Para la colección orders, se propone la shard key:



{ user\_id: "hashed" }



Esta clave permite distribuir las órdenes entre shards y evitar hotspots generados por campos secuenciales como created\_at u order\_number.



Integrantes

Agustín Peña

Matías Roberti

