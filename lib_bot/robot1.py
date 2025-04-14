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

        self.max_posiciones = 1               # Máximo de posiciones abiertas.
        self.posiciones_abiertas = 0

        self.ult_velas = 30                     # Número de velas a obtener.
        self.periodo_rapido = 12
        self.periodo_lento = 26
        self.periodo_senyal = 9
        self.df = None


    def obterner_df(self, symbol, timeframe, ult_velas) -> pd.DataFrame:
        # Obtener los precios de las últimas velas.
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, ult_velas)
        rates_df = pd.DataFrame(rates)

        # Convertir la columna 'time' a formato datetime.
        rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')
        rates_df['time'] = rates_df['time'].dt.tz_localize('UTC').dt.tz_convert('Europe/Madrid')
        rates_df['time'] = rates_df['time'].dt.strftime('%d-%m-%Y %H:%M:%S')

        return rates_df
    

    def ejecutar(self):
        # Inicializa la conexión con MetaTrader 5.
        mt5.inizialize()
        logging.info("ROBOT1 - Conectando con MetaTrader 5...")
        if not mt5.initialize():
            logging.error("ROBOT1 - Error al inicializar MetaTrader 5.")
            return
        logging.info("ROBOT1 - Conectado con Metatrader 5.")

        while True:
            
            try:
                # Obtener el DataFrame de precios.
                self.df = self.obterner_df(self.symbol, self.timeframe, self.velas)
                logging.info("ROBOT1 - Datos obtenidos desde MetaTrader 5.")
            except Exception as e:
                logging.error(f"ROBOT1 - Error al obtener datos: {e}")
                continue

            try:
                # Creamos objeto tendencia y calculamos la señayl con MACD.
                tendencia = Tendencia(self.periodo_rapido, self.periodo_lento, self.periodo_senyal, self.df)
                senyal = tendencia.macd()
                logging.info(f"Señal obtenida: {senyal}")
            except Exception as e:
                logging.error(f"ROBOT1 - Error al obtener la tendencia: {e}")
                continue

            # Comprobar si hay posiciones abiertas o se ha alcanzado el máximo de posiciones.
            self.posiciones_abiertas = mt5.positions_total()
            if self.posiciones_abiertas >= self.max_posiciones:
                logging.info("ROBOT1 - Máximo de posiciones alcanzado.")
                continue

            if senyal == 'buy':
                logging.info("ROBOT1 - Señal de compra detectada.")
                # Ejecutar lógica de compra.
                self.orden_compra()
            elif senyal == 'sell':
                logging.info("ROBOT1 - Señal de venta detectada.")
                # Ejecutar lógica de venta.
                self.orden_venta()
            else:
                logging.info("ROBOT1 - No hay señal de tendencia.")

            time.sleep(1)  # Espera 1 segundo entre cada iteración.