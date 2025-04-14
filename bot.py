from lib_bot.mt5_connector import MT5Connector
from log.log_loader import setup_logging  # Importar la configuración de logging
import logging
from lib_bot.menu import Menu
from colorama import Fore, Style


# Configurar logging desde log_loader
setup_logging()

try:
    # Crear una instancia de MT5Connector
    mt5C = MT5Connector()

    # Aquí puedes agregar lógica para realizar operaciones con MetaTrader 5
    logging.info("Conexión establecida con MetaTrader 5")

    # Ejecutar menú principal del bot.
    robot = Menu()
    robot.ejecutar()

    # Cerrar la conexión al finalizar
    mt5C.shutdown()

except ConnectionError as e:
    logging.error(f"Error de conexión: {e}")