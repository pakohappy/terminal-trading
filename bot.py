from lib_bot.mt5_connector import MT5Connector
from log.log_loader import setup_logging  # Importar la configuración de logging
import logging

# Configurar logging desde log_loader
setup_logging()

try:
    # Crear una instancia de MT5Connector
    mt5 = MT5Connector()

    # Aquí puedes agregar lógica para realizar operaciones con MetaTrader 5
    logging.info("Conexión establecida con MetaTrader 5")

    # Cerrar la conexión al finalizar
    mt5.shutdown()

except ConnectionError as e:
    logging.error(f"Error de conexión: {e}")