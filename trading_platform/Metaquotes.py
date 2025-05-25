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
        if not (mt5.initialize()):
            error_code = mt5.last_error()
            logging.error(f"ROBOT1 - Failed to initialize MetaTrader 5, error code = {error_code}")
            quit()

    @staticmethod
    def get_df(symbol: str, timeframe: int, ult_velas: int) -> pd.DataFrame:
        """
        Obtiene el DataFrame de las últimas velas(ult_velas) desde MetaTrader 5.
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
    def open_order_buy(symbol: str, volumen: float, signal: int, pips_sl: int, pips_tp: int, deviation: int, comment: str):
        """
        Función para abrir una orden.
        """
        # Obtener la información del último tick del símbolo.
        tick = mt5.symbol_info_tick(symbol)
        # Obtener la información total del símbolo.
        symbol_info = mt5.symbol_info(symbol)
        price_dict = {2: tick.ask, 1: tick.bid}

        # Obtener el punto del símbolo.
        point = symbol_info.point

        # Detectar dirección del stopLoss y takeProfit.
        stop_loss = price_dict[signal] - pips_sl * point
        take_profit = price_dict[signal] + pips_tp * point

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volumen,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price_dict[signal],
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": deviation,
            "magic": 235711,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        order_result = mt5.order_send(request)
        print(order_result)

        return order_result

    @staticmethod
    def open_order_sell(symbol: str, volumen: float, signal: int, pips_sl: int, pips_tp: int, deviation: int, comment: str):
        """
        Función para cerrar una orden.
        """
        # Obtener la información del último tick del símbolo.
        tick = mt5.symbol_info_tick(symbol)
        # Obtener la información total del símbolo.
        symbol_info = mt5.symbol_info(symbol)
        price_dict = {2: tick.ask, 1: tick.bid}

        # Obtener el punto del símbolo.
        point = symbol_info.point

        # Detectar dirección del stopLoss y takeProfit.
        stop_loss = price_dict[signal] + pips_sl * point
        take_profit = price_dict[signal] - pips_tp * point

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volumen,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price_dict[signal],
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": deviation,
            "magic": 235712,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        order_result = mt5.order_send(request)
        print(order_result)

        return order_result

    @staticmethod
    def close_position(position):
        tick = mt5.symbol_info_tick(position.symbol)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
            "price": tick.ask if position.type == 1 else tick.bid,
            "deviation": 20,
            "magic": 2357,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        return result