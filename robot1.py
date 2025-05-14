"""
-*- coding: utf-8 -*-
"""
import MetaTrader5 as mt5
from log.log_loader import setup_logging
import logging
from platform.Metaquotes import Metaquotes as mtq

"""
Configuración de Robot 1.
"""
SYMBOL = 'USDJPY'
TIMEFRAME = mt5.TIMEFRAME_M5
ULT_VELAS = 30
PIPS_SL = 50
PIPS_TP = 100
DEVIATION = 100

# Importamos la configuración del logging.
setup_logging()


def ejecutar_robot1():

    mtq.initialize_mt5()
    df = mtq.get_df(SYMBOL, TIMEFRAME, ULT_VELAS)
    print(df)
    logging.info(f"ROBOT1 - Datos obtenidos desde MetaTrader 5.")

    return None