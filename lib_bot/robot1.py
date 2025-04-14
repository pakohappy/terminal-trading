# -*- coding: utf-8 -*-

# Robot - 1.
# MACD - Moving Average Convergence Divergence.

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time

from indicadores.tendencia import Tendencia
import logging

class Robot1:
    def __init__(self, cofigpath='configuracion/config.ini'):
        """
        Inicializa el robot con la configuración y parámetros necesarios.
        """
        self.config_path = cofigpath
        self.symbol = 'EURUSD'
        self.timeframe = mt5.TIMEFRAME_M1
        self.volume = 0.1
        self.deviation = 10

        self.velas = 30                     # Número de velas a obtener.
        self.periodo_rapido = 12
        self.periodo_lento = 26
        self.periodo_senyal = 9
        self.df = None

    def 

    def ejecutar(self):
        # Inicializa la conexión con MetaTrader 5.
        mt5.inizialize()
        logging.info("Conectando con MetaTrader 5...")
        if not mt5.initialize():
            logging.error("Error al inicializar MetaTrader 5.")
            return
        logging.info("Conectado con Metatrader 5.")

        while True:

            time.sleep(1)  # Espera 1 segundo entre cada iteración.