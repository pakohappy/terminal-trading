# -*- coding: utf-8 -*-
import MetaTrader5 as mt5
# Importar configuraciones y logging.
from configuracion.config_loader import ConfigLoader
from log.log_loader import setup_logging
import logging

# Cargar configuraciones desde config_loader.
config = ConfigLoader('configuracion\config.ini')

# Datos de conexión a MetaTrader 5.
login = config.get_int('metatrader', 'login')
password = config.get('metatrader', 'password')
server = config.get('metatrader', 'server')

# Configurar logging desde logging_loader
setup_logging()

logging.info("Iniciando el script de trading...")

# Iniciar conexión con MetaTrader 5
if not mt5.initialize(login=login, password=password, server=server):
    # Si no se puede conectar, registrar el error y cerrar la conexión.
    logging.error("Error al inicializar MetaTrader 5")
    mt5.shutdown()
else:
    logging.info("MetaTrader 5 inicializado correctamente.")
    # Aquí puedes agregar más lógica para tu bot de trading
    mt5.shutdown()
    logging.info("MetaTrader 5 cerrado correctamente.")