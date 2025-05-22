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
VOLUME = 0.01
LAST_CANDLES = 30
PIPS_SL = 50
PIPS_TP = 100
DEVIATION = 100
COMMENT = "Robot 1 Order"

# Stochastic.
K_PERIOD = 5
D_PERIOD = 3
SMOOTH_K = 3
OVERBOUGHT_LEVEL = 80
OVERSOLD_LEVEL = 20
MODE = 0

# Importamos la configuración del logging.
setup_logging()


def run():

    mtq.initialize_mt5()


    df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
    print(df)
    logging.info(f"ROBOT1 - Datos obtenidos desde MetaTrader 5.")
    indicator = Oscillator(df)
    signal = indicator.stochastic(K_PERIOD, D_PERIOD, SMOOTH_K, OVERBOUGHT_LEVEL, OVERSOLD_LEVEL, MODE)

    if signal == 0 or signal == 1:
        mtq.open_order(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
    else:
        print("No hay signal.")
    return None