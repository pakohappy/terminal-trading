"""
-*- coding: utf-8 -*-
"""
# Robot - 1.
# MACD - Moving Average Convergence Divergence.

import MetaTrader5 as mt5
import pandas as pd
import time
from indicadores.tendencia import Tendencia
import logging

def initialize_mt5():
    """
    Inicializa la conexión con MetaTrader 5.
    """
    if not mt5.initialize():
        error_code = mt5.last_error()
        logging.error(f"Failed to initialize MetaTrader 5, error code = {error_code}")
        quit()

def obterner_df(symbol: str, timeframe: int, ult_velas: int) -> pd.DataFrame:
    """
    Obiene el DataFrame de las últimas velas(ult_velas).
    """
    # Obtener los precios de las últimas velas.
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, ult_velas)
    rates_df = pd.DataFrame(rates)

    # Convertir la columna 'time' a formato datetime.
    rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')
    rates_df['time'] = rates_df['time'].dt.tz_localize('UTC').dt.tz_convert('Europe/Madrid')
    rates_df['time'] = rates_df['time'].dt.strftime('%d-%m-%Y %H:%M:%S')

    return rates_df

class Robot1:
    """
    Clase Robot 1.
    """
    DEFAULT_CONFIG_PATH = 'configuracion/config.ini'

    def __init__(self, cofig_path=DEFAULT_CONFIG_PATH):
        """
        Inicializa el robot con la configuración y parámetros necesarios.
        """
        # Inicializa la conexión con MetaTrader 5.
        initialize_mt5()

        self.config_path = cofig_path
        self.symbol = 'EURUSD'
        self.timeframe = mt5.TIMEFRAME_M1
        self.volumen = 0.1
        self.desviation = 20

        self.max_posiciones = 1               # Máximo de posiciones abiertas.
        self.posiciones_abiertas = 0

        self.ult_velas = 30                     # Número de velas a obtener.
        self.periodo_rapido = 6
        self.periodo_lento = 14
        self.periodo_senyal = 9
        self.df = None

    def abrir_orden(self, symbol: str, volumen: float, senyal: str):
        """
        Función para abrir una orden.
        """
        tick = mt5.symbol_info_tick(symbol)

        order_dict = {'buy': 0, 'sell': 1}
        price_dict = {'buy': tick.ask, 'sell': tick.bid}

        point = mt5.symbol_info(symbol).point

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volumen,
            "type": order_dict[senyal],
            "price": price_dict[senyal],
            "sl": price_dict[senyal] - 15 * point,
            "tp": price_dict[senyal] + 15 * point,
            "deviation": self.desviation,
            "magic": 235711,
            "comment": "python market order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        order_result = mt5.order_send(request)
        print(order_result)

        return order_result

    def ejecutar(self) -> None:
        """
        Bucle principal del Robot 1.
        """
        while True:
            senyal = None

            try:
                # Comprobar si hay posiciones abiertas o se ha alcanzado el máximo de posiciones.
                self.posiciones_abiertas = mt5.positions_total()
                logging.info(f"ROBOT1 - Posiciones abiertas: {self.posiciones_abiertas}")
            except Exception as e:
                logging.error(f"ROBOT1 - Error al obtener las posiciones abiertas: {e}")

            if self.posiciones_abiertas >= self.max_posiciones:
                logging.info("ROBOT1 - Máximo de posiciones abiertas alcanzado.")
            else:
                try:
                    # Obtener el DataFrame de precios.
                    self.df = obterner_df(
                        self.symbol,
                        self.timeframe,
                        self.ult_velas
                    )
                    logging.info("ROBOT1 - Datos obtenidos desde MetaTrader 5.")
                except Exception as e:
                    logging.error(f"ROBOT1 - Error al obtener datos: {e}")

                try:
                    # Creamos objeto tendencia y calculamos la senyal con MACD.
                    tendencia = Tendencia(
                        self.periodo_rapido,
                        self.periodo_lento,
                        self.periodo_senyal,
                        self.df
                    )
                    senyal = tendencia.macd()
                    logging.info(f"ROBOT1 - Señal obtenida: {senyal}")
                except Exception as e:
                    logging.error(f"ROBOT1 - Error al obtener la tendencia: {e}")

                if senyal == 'buy':
                    logging.info("ROBOT1 - Señal de compra detectada.")
                    # Ejecutar lógica de compra.
                    self.abrir_orden(
                        symbol=self.symbol,
                        volumen=self.volumen,
                        senyal=senyal
                    )
                elif senyal == 'sell':
                    logging.info("ROBOT1 - Señal de venta detectada.")
                    # Ejecutar lógica de venta.
                    self.abrir_orden(
                        symbol=self.symbol,
                        volumen=self.volumen,
                        senyal=senyal
                    )

            time.sleep(5)  # Espera x segundos entre cada iteración.