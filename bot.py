# -*- coding: utf-8 -*-
from log.log_loader import setup_logging  # Importar la configuración de logging
import logging
from lib_bot.menu import Menu
from colorama import Fore, Style


# Configurar logging desde log_loader
setup_logging()

try:
    # Ejecutar menú principal del bot.
    robot = Menu()
    robot.ejecutar()

except Exception as e:
    logging.error(f"Error al ejecutar el menú: {e}")