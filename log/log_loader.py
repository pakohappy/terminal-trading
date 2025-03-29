import logging
import os

def setup_logging(log_folder="c:/Users/pako_/Documents/GitHub/trading/logs", log_file="bot.log"):
    """
    Configura un sistema de logging exhaustivo con múltiples manejadores.

    Mejoras en el sistema de logging:
    Múltiples manejadores (handlers):

    Archivo: Registra todos los eventos (DEBUG y superiores) en un archivo.
    Consola: Muestra solo eventos importantes (INFO y superiores) en la consola.
    Formato detallado:

    Incluye la fecha, el nombre del logger, el nivel del log y el mensaje.
    Niveles de log:

    DEBUG: Información detallada para depuración.
    INFO: Información general sobre el flujo del programa.
    WARNING: Advertencias sobre posibles problemas.
    ERROR: Errores que afectan la ejecución.
    CRITICAL: Errores graves que requieren atención inmediata.

    """
    # Crear la carpeta de logs si no existe
    os.makedirs(log_folder, exist_ok=True)
    
    # Ruta completa del archivo de log
    log_path = os.path.join(log_folder, log_file)
    
    # Crear un logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Nivel global del logger

    # Formato detallado para los logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Manejador para archivo (archivo de log)
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)  # Nivel de detalle para el archivo
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Manejador para consola (salida estándar)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Nivel de detalle para la consola
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Mensaje inicial
    logger.info(">>> Sistema de logging configurado.")


## Ejemplo de uso:
# # -*- coding: utf-8 -*-
# import MetaTrader5 as mt5
# from configuracion.config_loader import ConfigLoader
# from logging.logging_loader import setup_logging
# import logging

# # Configurar logging desde logging_loader
# setup_logging()

# logging.info("Iniciando el script de trading...")

# # Iniciar conexión con MetaTrader 5
# if not mt5.initialize():
#     logging.error("Error al inicializar MetaTrader 5")
#     print("Error al inicializar MetaTrader 5")
#     mt5.shutdown()
# else:
#     logging.info("MetaTrader 5 inicializado correctamente.")
#     # Aquí puedes agregar más lógica para tu bot de trading
#     mt5.shutdown()
#     logging.info("MetaTrader 5 cerrado correctamente.")