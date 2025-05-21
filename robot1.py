"""
-*- coding: utf-8 -*-
"""
import MetaTrader5 as mt5
from log.log_loader import setup_logging
from platform.Metaquotes import Metaquotes as mtq
from indicators.Oscillator import Oscillator
import logging

"""
Configuración de Robot 1.
"""
SYMBOL = 'USDJPY'
TIMEFRAME = mt5.TIMEFRAME_M5
LAST_CANDLES = 30
PIPS_SL = 50
PIPS_TP = 100
DEVIATION = 100

# Importamos la configuración del logging.
setup_logging()


def run():

    mtq.initialize_mt5()
    df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
    print(df)
    logging.info(f"ROBOT1 - Datos obtenidos desde MetaTrader 5.")
    signal = Oscillator.stochastic(df)

    if signal == 0:
        mtq.open_order(SYMBOL, 1, signal, PIPS_SL, PIPS_TP, DEVIATION)#todo solucionar portabilidad Metaquotes.
    elif signal == 1:
        mtq.open_order(SYMBOL, 1, signal, PIPS_SL, PIPS_TP, DEVIATION)
    return None