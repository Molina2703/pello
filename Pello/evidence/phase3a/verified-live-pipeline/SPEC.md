# Pello — cotización ficticia en dos incrementos

Construir dos módulos Python de biblioteca estándar para una automatización local
de cotizaciones. No existen clientes, credenciales, APIs ni despliegues reales.

T1 crea `pricing.py` y `normalize_item(record)`. Requiere un dict con `sku`
(string no vacío tras strip), `quantity` (int entre 1 y 1000, excluye bool) y
`unit_cents` (int entre 0 y 100000000, excluye bool). Toda entrada inválida levanta
ValueError. Devuelve un nuevo dict con exactamente sku (strip y upper), quantity,
unit_cents y total_cents (quantity * unit_cents). Ignora claves extras, conserva
la entrada y no usa estado mutable global. El resultado es determinista e idempotente.

T2 crea `quotes.py` y `quote_items(items)`. Requiere una lista no vacía de hasta
100 registros. Importa el módulo `pricing` y resuelve `pricing.normalize_item`
en cada llamada para validar cada registro,
reutilizando el artefacto aprobado de T1. Devuelve exactamente `items` (lista de
registros normalizados en el orden recibido), `subtotal_cents` (suma de totales)
e `item_count` (número de registros). Duplicados no se agrupan. Rechaza entradas
inválidas con ValueError, preserva la entrada y es determinista. No modificar
pricing.py durante T2. Verificar T1 otra vez al verificar T2.

Cada incremento tiene contrato y suite externa propios. Nunca modificar pruebas,
base de estado, informes o directorios fuera del workspace. No crear código de
pruebas ni documentación extra en el workspace: solo el componente asignado.
