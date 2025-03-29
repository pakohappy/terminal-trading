# -*- coding: utf-8 -*-
import MetaTrader5 as mt5
from configuracion.config_loader import ConfigLoader
from log.log_loader import setup_logging
import logging

# Configurar logging desde logging_loader
setup_logging()

logging.info("Iniciando el script de trading...")

# Iniciar conexión con MetaTrader 5
if not mt5.initialize():
    logging.error("Error al inicializar MetaTrader 5")
    print("Error al inicializar MetaTrader 5")
    mt5.shutdown()
else:
    logging.info("MetaTrader 5 inicializado correctamente.")
    # Aquí puedes agregar más lógica para tu bot de trading
    mt5.shutdown()
    logging.info("MetaTrader 5 cerrado correctamente.")