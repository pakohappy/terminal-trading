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
PIPS_SL = 50
PIPS_TP = 70
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


def run():  #todo hacer que no cierre las posiciones en el cambio de tendencia, a no ser que se salga
            #todo del espacio de overbought/oversold.

    mtq.initialize_mt5()

    while True:
        positions = mt5.positions_get(symbol=SYMBOL)
        print(f">>> Hay {len(positions)} posiciones abiertas.")
        
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
                print(">>> No hay signal.")

        # elif len(positions) == 1:
        #     for position in positions:
        #         df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
        #         indicator = Oscillator(df)
        #         signal = indicator.stochastic(K_PERIOD, D_PERIOD, SMOOTH_K, OVERBOUGHT_LEVEL, OVERSOLD_LEVEL, MODE)
        #
        #         if position.type == 0 and signal == 2 or position.type == 1 and signal == 1:
        #             print(">>> No hay señal para abrir una segunda posición.")
        #
        #         if position.type == 0 and signal == 1:
        #             mtq.open_order_sell(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
        #
        #         if position.type == 1 and signal == 2:
        #             mtq.open_order_buy(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)

        # elif len(positions) > 0:
        #     for position in positions:
        #
        #         df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
        #         indicator = Oscillator(df)
        #         signal = indicator.stochastic(K_PERIOD, D_PERIOD, SMOOTH_K, OVERBOUGHT_LEVEL, OVERSOLD_LEVEL, MODE)
        #
        #         if position.type == 0 and signal == 1 or position.type == 1 and signal == 2:
        #             mtq.close_position(position)
        #         else:
        #             print ("No hay signal que marque el cierre de la posición.")

        else:
            print("No hay posiciones abiertas.")

        time.sleep(1)

if __name__ == "__main__":
    run()