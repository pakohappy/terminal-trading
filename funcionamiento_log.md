# Sistema de Logging

## Introducción

El sistema de logging implementado en este proyecto de trading proporciona un mecanismo robusto para registrar eventos, mensajes y errores durante la ejecución de los robots de trading. Este documento describe cómo está configurado el sistema de logging, cómo utilizarlo y las mejores prácticas para su implementación.

## Configuración del Sistema

El sistema de logging se configura a través de la función `setup_logging()` ubicada en el módulo `log.log_loader`. Esta función establece:

- **Múltiples manejadores (handlers)**:
  - **Archivo**: Registra todos los eventos (DEBUG y superiores) en un archivo.
  - **Consola**: Muestra solo eventos importantes (INFO y superiores) en la consola.

- **Formato detallado**:
  - Incluye la fecha, el nombre del logger, el nivel del log y el mensaje.
  - Formato: `YYYY-MM-DD HH:MM:SS - nombre_logger - NIVEL - mensaje`

- **Rotación de archivos**:
  - Los archivos de log rotan automáticamente a medianoche.
  - Se mantienen hasta 15 archivos de respaldo.

### Parámetros de Configuración

La función `setup_logging()` acepta los siguientes parámetros:

- `log_folder`: Carpeta donde se guardarán los logs (por defecto "logs").
- `log_file`: Nombre base del archivo de log (por defecto "bot.log").
- `when`: Cuándo rotar los archivos (por defecto "midnight").
- `interval`: Intervalo de rotación (por defecto 1).
- `backup_count`: Número máximo de archivos de respaldo (por defecto 15).

## Niveles de Log

El sistema utiliza los niveles estándar de logging de Python:

1. **DEBUG**: Información detallada para depuración.
   ```python
   logging.debug("Este es un mensaje de DEBUG")
   ```

2. **INFO**: Información general sobre el flujo del programa.
   ```python
   logging.info("Este es un mensaje de INFO")
   ```

3. **WARNING**: Advertencias sobre posibles problemas.
   ```python
   logging.warning("Este es un mensaje de WARNING")
   ```

4. **ERROR**: Errores que afectan la ejecución.
   ```python
   logging.error("Este es un mensaje de ERROR")
   ```

5. **CRITICAL**: Errores graves que requieren atención inmediata.
   ```python
   logging.critical("Este es un mensaje de CRITICAL")
   ```

## Uso del Sistema de Logging

### Inicialización

Para utilizar el sistema de logging, primero debe inicializarse llamando a la función `setup_logging()`:

```python
from log.log_loader import setup_logging

# Configurar el sistema de logging
setup_logging()
```

### Registro de Mensajes

Una vez configurado, puede utilizar las funciones estándar de logging de Python:

```python
import logging

# Registrar mensajes de diferentes niveles
logging.debug("Mensaje de depuración detallado")
logging.info("Información general sobre el flujo del programa")
logging.warning("Advertencia sobre un posible problema")
logging.error("Error que afecta la ejecución")
logging.critical("Error grave que requiere atención inmediata")
```

### Logging desde Clases de Robots

Para los robots de trading, se recomienda incluir el nombre de la clase en los mensajes de log para facilitar la identificación del origen del mensaje:

```python
logging.info(f"{self.__class__.__name__} - Mensaje específico del robot")
```

Ejemplo de implementación en la clase `AdvancedRobot`:

```python
logging.info(f"{self.__class__.__name__} - No hay signal que marque el cierre de la posición.")
```

## Ejemplos de Uso

### Ejemplo Básico

```python
import logging
from log.log_loader import setup_logging

# Configurar el sistema de logging
setup_logging()

# Registrar mensajes
logging.debug("Este es un mensaje de DEBUG")
logging.info("Este es un mensaje de INFO")
logging.warning("Este es un mensaje de WARNING")
logging.error("Este es un mensaje de ERROR")
logging.critical("Este es un mensaje de CRITICAL")
```

### Ejemplo con Robots de Trading

```python
import logging
from log.log_loader import setup_logging
from utils.robots.robot_advanced import AdvancedRobot
from utils.robots.robot_stochastic import StochasticRobot
from utils.robots.robot_triple_sma import TripleSMARobot

# Configurar el sistema de logging
setup_logging()

# Crear instancias de robots
robot_advanced = AdvancedRobot()
robot_stochastic = StochasticRobot()
robot_triple_sma = TripleSMARobot()

# Registrar mensajes desde robots
logging.info("=== Probando mensajes de log desde robots ===")
logging.info(f"{robot_advanced.__class__.__name__} - No hay signal que marque el cierre de la posición.")
logging.info(f"{robot_stochastic.__class__.__name__} - No hay señal para abrir una segunda posición.")
logging.info(f"{robot_triple_sma.__class__.__name__} - No hay signal que marque el cierre de la posición.")
```

## Ubicación de los Archivos de Log

Los archivos de log se almacenan en la carpeta `log/logs/` del proyecto. El archivo principal es `bot.log`, y los archivos rotados tendrán nombres como `bot.log.YYYY-MM-DD`.

## Mejores Prácticas

1. **Inicializar el logging al principio**: Llame a `setup_logging()` al inicio de su aplicación.
2. **Usar el nivel adecuado**: Utilice el nivel de log apropiado según la importancia del mensaje.
3. **Incluir contexto**: Añada información contextual en los mensajes para facilitar la depuración.
4. **Identificar la fuente**: Para clases, incluya el nombre de la clase en los mensajes.
5. **Ser conciso pero informativo**: Los mensajes deben ser claros y proporcionar información útil.

## Pruebas del Sistema de Logging

El archivo `test_logging.py` proporciona un ejemplo completo de cómo probar el sistema de logging:

```python
def test_logging():
    """
    Prueba el sistema de logging mejorado.
    """
    # Configurar el sistema de logging
    setup_logging()
    
    # Probar logging directo
    logging.debug("Este es un mensaje de DEBUG")
    logging.info("Este es un mensaje de INFO")
    logging.warning("Este es un mensaje de WARNING")
    logging.error("Este es un mensaje de ERROR")
    logging.critical("Este es un mensaje de CRITICAL")
    
    # Probar logging desde robots
    robot_advanced = AdvancedRobot()
    robot_stochastic = StochasticRobot()
    robot_triple_sma = TripleSMARobot()
    
    # Simular mensajes de log desde cada robot
    logging.info("=== Probando mensajes de log desde robots ===")
    
    # Estos mensajes deberían usar el formato estandarizado con el nombre de la clase
    logging.info(f"{robot_advanced.__class__.__name__} - No hay signal que marque el cierre de la posición.")
    logging.info(f"{robot_stochastic.__class__.__name__} - No hay señal para abrir una segunda posición.")
    logging.info(f"{robot_triple_sma.__class__.__name__} - No hay signal que marque el cierre de la posición.")
    
    logging.info("=== Prueba de logging completada ===")
```

Para ejecutar esta prueba, simplemente ejecute el script `test_logging.py`:

```
python test_logging.py
```

## Conclusión

El sistema de logging implementado proporciona una forma robusta y flexible de registrar eventos durante la ejecución de los robots de trading. Siguiendo las mejores prácticas descritas en este documento, puede aprovechar al máximo este sistema para facilitar la depuración y el monitoreo de sus aplicaciones de trading.