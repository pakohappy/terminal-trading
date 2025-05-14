"""
-*- coding: utf-8 -*-
"""
import MetaTrader5 as mt5
import logging
import pandas as pd

class Metaquotes:

    @staticmethod
    def initialize_mt5():
        """
        Inicializa la conexión con MetaTrader 5.
        """
        if not mt5.initialize():
            error_code = mt5.last_error()
            logging.error(f"ROBOT1 - Failed to initialize MetaTrader 5, error code = {error_code}")
            quit()

    @staticmethod
    def obterner_df(symbol: str, timeframe: int, ult_velas: int) -> pd.DataFrame:
        """
        Obiene el DataFrame de las últimas velas(ult_velas) desde MetaTrader 5.
        """
        # Obtener los precios de las últimas velas.
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, ult_velas)
        rates_df = pd.DataFrame(rates)

        # Convertir la columna 'time' a formato datetime.
        rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')
        rates_df['time'] = rates_df['time'].dt.tz_localize('UTC').dt.tz_convert('Europe/Madrid')
        rates_df['time'] = rates_df['time'].dt.strftime('%d-%m-%Y %H:%M:%S')

        return rates_df

    @staticmethod
    def abrir_orden(symbol: str, volumen: float, senyal: str):
        """
        Función para abrir una orden.
        """
        # Obtener la información del último tick del símbolo.
        tick = mt5.symbol_info_tick(symbol)
        # Obtener la información total del símbolo.
        symbol_info = mt5.symbol_info(symbol)

        order_dict = {'buy': mt5.ORDER_TYPE_BUY, 'sell': mt5.ORDER_TYPE_SELL}
        price_dict = {'buy': tick.ask, 'sell': tick.bid}

        # Obtener el punto del símbolo.
        point = symbol_info.point

        # Detectar dirección del stopLoss y takeProfit.
        stop_loss = 0
        take_profit = 0

        if order_dict[senyal] == mt5.ORDER_TYPE_BUY:
            stop_loss = price_dict[senyal] - PIPS_SL * point
            take_profit = price_dict[senyal] + PIPS_TP * point

        if order_dict[senyal] == mt5.ORDER_TYPE_SELL:
            stop_loss = price_dict[senyal] + PIPS_SL * point
            take_profit = price_dict[senyal] - PIPS_TP * point

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volumen,
            "type": order_dict[senyal],
            "price": price_dict[senyal],
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": DESVIATION,
            "magic": 235711,
            "comment": "python market order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        order_result = mt5.order_send(request)
        print(order_result)

        return order_result