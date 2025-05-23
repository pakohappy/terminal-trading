"""
-*- coding: utf-8 -*-
"""
import time
import MetaTrader5 as mt5
from log.log_loader import setup_logging
from trading_platform.Metaquotes import Metaquotes as mtq
from indicators.Oscillator import Oscillator

"""
Configuración de Robot 1.
"""
SYMBOL = 'USDJPY'
TIMEFRAME = mt5.TIMEFRAME_M5
VOLUME = 0.01
LAST_CANDLES = 30
PIPS_SL = 100
PIPS_TP = 150
DEVIATION = 100
COMMENT = "Robot 1 Order"

# Stochastic.
K_PERIOD = 5
D_PERIOD = 3
SMOOTH_K = 3
OVERBOUGHT_LEVEL = 70
OVERSOLD_LEVEL = 30
MODE = 0

# Importamos la configuración del logging.
setup_logging()


def run():

    mtq.initialize_mt5()

    while True:
        positions = mt5.positions_get(symbol=SYMBOL)
        print(len(positions))
        if positions is None or len(positions) == 0:
            df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
            #print(df)
            print(f"ROBOT1 - Datos obtenidos desde MetaTrader 5.")
            indicator = Oscillator(df)
            signal = indicator.stochastic(K_PERIOD, D_PERIOD, SMOOTH_K, OVERBOUGHT_LEVEL, OVERSOLD_LEVEL, MODE)

            if signal == 2:
                mtq.open_order_buy(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
            elif signal == 1:
                mtq.open_order_sell(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
            else:
                print("No hay signal.")

        elif len(positions) > 0:
            print(f"Total positions on {SYMBOL}: ", len(positions))
            # display all open positions
            for position in positions:
                print(position)#todo gestinar cierre de órdenes.

                # df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
                # indicator = Oscillator(df)
                # signal = indicator.stochastic(K_PERIOD, D_PERIOD, SMOOTH_K, OVERBOUGHT_LEVEL, OVERSOLD_LEVEL, MODE)
                #
                # if position.type == mt5.ORDER_TYPE_BUY and signal == 1:
                #     mt5.Close(position.ticket)
                # elif position.type == mt5.POSITION_TYPE_SELL and signal == 2:
                #     mt5.Close(position.ticket)
                # else:
                #     print("No hay signal que marque el cierre de la posición.")

        else:
            print("No hay posiciones abiertas.")

        time.sleep(1)

if __name__ == "__main__":
    run()