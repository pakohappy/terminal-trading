import logging
import os
from logging.handlers import TimedRotatingFileHandler

def setup_logging(log_folder="logs", log_file="bot.log", when="midnight", interval=1, backup_count=15):
    """
    Configura un sistema de logging exhaustivo con múltiples manejadores.
    Incluye rotación de archivos de log cuando alcanzan un tamaño máximo.

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

    Parámetros:
    - log_folder: Carpeta donde se guardarán los logs.
    - log_file: Nombre base del archivo de log.
    - max_bytes: Tamaño máximo del archivo de log en bytes antes de rotar (por defecto 5 MB).
    - backup_count: Número máximo de archivos de respaldo que se mantendrán.
    """
    
    # Obtener la ruta absoluta del directorio base del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construir la ruta completa de la carpeta de logs
    log_folder_path = os.path.join(base_dir, log_folder)

    # Crear la carpeta de logs si no existe
    os.makedirs(log_folder_path, exist_ok=True)
    
    # Ruta completa del archivo de log
    log_path = os.path.join(log_folder_path, log_file)
    
    # Crear un logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Nivel global del logger
    
    # Verificar si ya hay handlers configurados para evitar duplicación
    if logger.hasHandlers():
        # Si ya hay handlers configurados, no hacer nada
        return

    # Formato detallado para los logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # # Manejador para archivo con rotación
    # rotating_file_handler = RotatingFileHandler(
    #     log_path, maxBytes=max_bytes, backupCount=backup_count
    # )
    # rotating_file_handler.setLevel(logging.DEBUG)  # Nivel de detalle para el archivo
    # rotating_file_handler.setFormatter(formatter)
    # logger.addHandler(rotating_file_handler)
    
    # Manejador para archivo con rotación diaria
    timed_file_handler = TimedRotatingFileHandler(
        log_path, when=when, interval=interval, backupCount=backup_count
    )
    timed_file_handler.setLevel(logging.DEBUG)  # Nivel de detalle para el archivo
    timed_file_handler.setFormatter(formatter)
    logger.addHandler(timed_file_handler)

    # Manejador para consola (salida estándar)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Nivel de detalle para la consola
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Mensaje inicial
    logger.info(">>> Sistema de logging configurado.")