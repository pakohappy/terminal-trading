"""
-*- coding: utf-8 -*-
"""
import time
import MetaTrader5 as mt5
from log.log_loader import setup_logging
from trading_platform.Metaquotes import Metaquotes as mtq
from indicators.Trend import Trend

"""
Configuración de Robot 2.
    Opera usando la comparativa entre tres SMA.
"""
SYMBOL = 'BTCUSD'
TIMEFRAME = mt5.TIMEFRAME_H1
VOLUME = 0.01
LAST_CANDLES = 20
PIPS_SL = 100000
PIPS_TP = 100000
DEVIATION = 100
COMMENT = "Robot 2 Order"

# Trend Triple SMA.
PERIODO_LENTO = 8
PERIODO_MEDIO = 6
PERIODO_RAPIDO = 4
MODE = 0

# Importamos la configuración del logging.
setup_logging()

def run():

    mtq.initialize_mt5()

    while True:
        positions = mt5.positions_get(symbol=SYMBOL)
        print(f">>> Hay {len(positions)} posiciones abiertas.")

        if positions is None or len(positions) == 0:
            df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
            #print(df)
            print(f"ROBOT1 - Datos obtenidos desde MetaTrader 5.")
            indicator = Trend(df)
            signal = indicator.triple_sma(PERIODO_LENTO, PERIODO_MEDIO, PERIODO_RAPIDO, MODE)

            if signal == 2:
                mtq.open_order_buy(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
            elif signal == 1:
                mtq.open_order_sell(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
            else:
                print(">>> No hay signal.")

        elif len(positions) > 0:
            for position in positions:

                df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
                indicator_close = Trend(df)
                signal_close = indicator_close.triple_sma(PERIODO_LENTO, PERIODO_MEDIO, PERIODO_RAPIDO, 1)

                if position.type == 0 and signal_close == 1 or position.type == 1 and signal_close == 2:
                    mtq.close_position(position)
                else:
                    print ("No hay signal que marque el cierre de la posición.")

        else:
            print("No hay posiciones abiertas.")

        time.sleep(1)

if __name__ == "__main__":
    run()