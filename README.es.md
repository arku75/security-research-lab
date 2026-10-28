# Laboratorio de investigación defensiva

Herramientas locales y notas de investigación de **Ema Curk / arku75**. [English](README.md)

Esta primera versión publica dos utilidades nuevas, ejemplos sintéticos y una revisión estática anonimizada. Se preparó con asistencia de IA durante la revisión de una colección local más amplia. No significa que se haya subido toda esa colección ni que los proyectos de terceros sean de autoría propia.

## Qué puedes usar

**Inventario sin nombres:** `tools/safe_inventory.py` cuenta archivos, tamaños y tipos sin abrir su contenido. El JSON no contiene rutas ni nombres de archivos. Omite enlaces simbólicos, carpetas habituales de dependencias y el historial Git. Indica si alcanzó un límite o tuvo errores.

```bash
python3 tools/safe_inventory.py ./proyecto-a-revisar
```

El inventario no detecta todos los secretos ni determina si un programa es seguro o tiene permiso de redistribución. Es una ayuda para organizar la revisión. Incluso los totales pueden ser privados; compruébalos antes de compartir el informe.

**Comparación de respuestas sintéticas:** `tools/auth_response_audit.py` analiza un CSV ya existente con cuatro columnas: `cohort`, `status_code`, `response_bytes` y `latency_ms`. Solo acepta las etiquetas `known` y `unknown`; no admite columnas de correos, nombres de usuario, tokens o cuerpos de respuesta.

```bash
python3 tools/auth_response_audit.py examples/consistent.csv
python3 tools/auth_response_audit.py examples/discrepant.csv
```

Los ejemplos tienen 20 observaciones ficticias por grupo. Uno presenta distribuciones y medianas iguales; el otro muestra diferencias deliberadas de código de estado, tamaño y tiempo. No proceden de cuentas ni servicios reales.

El análisis es descriptivo: no envía peticiones, no comprueba cuentas y no demuestra por sí solo la presencia o ausencia de una vulnerabilidad. Los resultados con pocas muestras se marcan como insuficientes. Las medidas y límites completos se explican en el [README principal](README.md).

## Requisitos y pruebas

Python 3.10 o posterior, sin paquetes externos:

```bash
python3 -m unittest discover -s tests -v
```

Las pruebas usan archivos temporales y datos sintéticos; no actúan sobre redes, dispositivos ni servicios de terceros.

## Investigación y atribución

- [Caso defensivo: separar observaciones de conclusiones sobre cuentas](docs/ACCOUNT_ENUMERATION_REVIEW.md).
- [Referencias oficiales de proyectos upstream](docs/UPSTREAM_REFERENCES.md).
- [Qué incluye esta publicación y qué queda pendiente](docs/PUBLICATION_SCOPE.md).

El código y la documentación nuevos usan [licencia MIT](LICENSE). Las referencias externas conservan sus propias licencias y su autoría. No se incluyen credenciales, datos de sesiones, listas de cuentas, material operativo de suplantación ni archivos privados de la colección original.
