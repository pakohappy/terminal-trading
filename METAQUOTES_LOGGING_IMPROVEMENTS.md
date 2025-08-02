# Mejoras en el Sistema de Logging de Metaquotes.py

## Resumen de Cambios

Se han implementado mejoras significativas en el sistema de logging del módulo `Metaquotes.py` para proporcionar un registro más detallado, consistente y útil de las operaciones realizadas a través de la interfaz de MetaTrader 5.

## Cambios Implementados

### 1. Estandarización de Mensajes

- Se ha añadido el prefijo `"Metaquotes - "` a todos los mensajes de log para identificar fácilmente el origen del mensaje.
- Se ha mejorado la consistencia en el formato de los mensajes de log en todos los métodos.

### 2. Mejora en la Granularidad del Logging

- Se han añadido mensajes de log de nivel `DEBUG` al inicio y fin de cada método para facilitar el seguimiento del flujo de ejecución.
- Se incluyen ahora los valores de los parámetros clave en los mensajes de log para facilitar la depuración.

### 3. Mejora en los Mensajes de Error

- Los mensajes de error ahora incluyen más detalles sobre la causa del error.
- Se han añadido mensajes de log de nivel `DEBUG` con información completa sobre los errores para facilitar la depuración.

### 4. Mejora en los Mensajes de Éxito

- Los mensajes de éxito ahora incluyen información relevante sobre el resultado de la operación.
- Se han añadido mensajes de log de nivel `DEBUG` con información completa sobre los resultados exitosos.

## Detalles por Método

### Método `is_initialized`
- Añadido log de entrada y salida con el estado de inicialización.

### Método `initialize_mt5`
- Mejorado el log de inicialización con más detalles.
- Añadido log de nivel DEBUG al inicio del método.

### Método `shutdown_mt5`
- Añadido log de nivel DEBUG al inicio del método.
- Mejorado el mensaje de cierre de conexión.

### Método `get_df`
- Añadido log de entrada con detalles de los parámetros (símbolo, timeframe, número de velas).
- Añadido log de salida con el número de velas obtenidas.
- Mejorado el mensaje de error al obtener datos.

### Método `get_account_info`
- Añadido log de entrada y salida con detalles de la información de la cuenta.
- Mejorado el mensaje de error.

### Método `get_positions`
- Añadido log de entrada con detalles del símbolo (si se proporciona).
- Añadido log de salida con el número de posiciones encontradas.
- Mejorado el mensaje de error.

### Método `_prepare_order_request`
- Añadido log de entrada con detalles de los parámetros de la orden.
- Añadido log de salida confirmando la preparación correcta de la solicitud.

### Método `open_order`
- Añadido log de entrada con detalles de la orden (tipo, símbolo, volumen, SL, TP).
- Añadido log de los cálculos de precio, SL y TP.
- Mejorado el mensaje de éxito con detalles del ticket, volumen y precio.
- Mejorado el mensaje de error con código y comentario.
- Añadido log de nivel DEBUG con detalles completos del resultado.

### Método `close_position`
- Añadido log de entrada con detalles de la posición a cerrar.
- Añadido log de los cálculos de precio de cierre.
- Mejorado el mensaje de éxito con detalles del ticket, precio y beneficio.
- Mejorado el mensaje de error con código y comentario.
- Añadido log de nivel DEBUG con detalles completos del resultado.

### Método `modify_position`
- Añadido log de entrada con detalles de la posición a modificar.
- Añadido log de los valores actuales y nuevos de SL y TP.
- Mejorado el mensaje de éxito con detalles de los nuevos valores de SL y TP.
- Mejorado el mensaje de error con código y comentario.
- Añadido log de nivel DEBUG con detalles completos del resultado.

### Método `get_symbol_info`
- Añadido log de entrada con el símbolo solicitado.
- Añadido log de salida con detalles clave del símbolo (point, digits, spread).
- Mejorado el mensaje de error.

## Beneficios de las Mejoras

1. **Mayor Trazabilidad**: Facilita el seguimiento del flujo de ejecución y la identificación de problemas.
2. **Mejor Depuración**: Proporciona más información para identificar y resolver problemas.
3. **Monitoreo Mejorado**: Permite un mejor monitoreo de las operaciones de trading.
4. **Consistencia**: Mantiene un formato consistente en todos los mensajes de log.
5. **Identificación de Origen**: El prefijo "Metaquotes -" facilita la identificación del origen de los mensajes en logs compartidos.

## Ejemplo de Uso

Para aprovechar al máximo estas mejoras, se recomienda configurar el nivel de log apropiado:

- Para desarrollo y depuración: Nivel `DEBUG` para ver todos los detalles.
- Para producción: Nivel `INFO` para ver solo información importante.

```python
import logging
from log.log_loader import setup_logging

# Configurar el sistema de logging
setup_logging()

# Para desarrollo, establecer nivel DEBUG
logging.getLogger().setLevel(logging.DEBUG)

# Para producción, establecer nivel INFO
# logging.getLogger().setLevel(logging.INFO)
```

## Conclusión

Estas mejoras en el sistema de logging de `Metaquotes.py` proporcionan una herramienta más potente para el desarrollo, depuración y monitoreo de las operaciones de trading a través de MetaTrader 5, facilitando la identificación y resolución de problemas, así como el seguimiento de las operaciones realizadas.