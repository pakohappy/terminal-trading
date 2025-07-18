# -*- coding: utf-8 -*-
"""
Robot de Trading 2: Estrategia basada en Triple SMA

Este robot implementa una estrategia de trading basada en el indicador Triple SMA (Triple Simple Moving Average),
que utiliza tres medias móviles simples con diferentes períodos para identificar tendencias en el mercado.
La estrategia busca oportunidades de compra cuando las medias móviles están alineadas en orden ascendente
(rápida > media > lenta) y oportunidades de venta cuando están alineadas en orden descendente
(rápida < media < lenta).
"""
import time
from typing import Optional, List
import MetaTrader5 as mt5
from log.log_loader import setup_logging
from trading_platform.Metaquotes import Metaquotes as mtq
from indicators.Trend import Trend

# Configuración del par de divisas y parámetros de trading
SYMBOL = 'BTCUSD'           # Criptomoneda a operar
TIMEFRAME = mt5.TIMEFRAME_H1  # Marco temporal (H1 = 1 hora)
VOLUME = 0.01               # Tamaño de la posición en lotes
LAST_CANDLES = 20           # Número de velas a analizar
PIPS_SL = 100000            # Stop Loss en pips (valor alto para Bitcoin)
PIPS_TP = 100000            # Take Profit en pips (valor alto para Bitcoin)
DEVIATION = 100             # Desviación máxima permitida del precio
COMMENT = "Robot 2 Order"   # Comentario para identificar las órdenes

# Parámetros del indicador Triple SMA
PERIODO_LENTO = 8           # Período para la media móvil lenta
PERIODO_MEDIO = 6           # Período para la media móvil media
PERIODO_RAPIDO = 4          # Período para la media móvil rápida
MODE = 0                    # Modo de operación (0 = señal en alineación de medias móviles)

# Configuración del sistema de registro (logging)
setup_logging()

def run() -> None:
    """
    Función principal que ejecuta la lógica de trading del robot.
    
    Esta función:
    1. Inicializa la conexión con MetaTrader 5
    2. En un bucle continuo:
       - Verifica si hay posiciones abiertas
       - Si no hay posiciones, analiza el mercado y abre nuevas posiciones según las señales
       - Si hay posiciones, monitorea las condiciones para cerrarlas
       
    Returns:
        None
        
    # TODO:
    #   - Optimizar los períodos de las medias móviles mediante backtesting
    #   - Implementar filtros adicionales para reducir señales falsas
    """
    # Inicializar la conexión con MetaTrader 5
    mtq.initialize_mt5()

    # Bucle principal de trading
    while True:
        # Obtener las posiciones abiertas para el símbolo configurado
        positions = mt5.positions_get(symbol=SYMBOL)
        print(f">>> Hay {len(positions)} posiciones abiertas.")

        # Si no hay posiciones abiertas, buscar oportunidades para abrir nuevas
        if positions is None or len(positions) == 0:
            # Obtener los datos de precio del símbolo
            df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
            print(f"ROBOT2 - Datos obtenidos desde MetaTrader 5.")
            
            # Crear una instancia del indicador Trend y calcular el Triple SMA
            indicator = Trend(df)
            signal = indicator.triple_sma(PERIODO_LENTO, PERIODO_MEDIO, PERIODO_RAPIDO, MODE)

            # Interpretar la señal y abrir órdenes según corresponda
            if signal == 2:  # Señal de compra (alineación alcista: rápida > media > lenta)
                mtq.open_order_buy(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
            elif signal == 1:  # Señal de venta (alineación bajista: rápida < media < lenta)
                mtq.open_order_sell(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
            else:  # No hay señal clara
                print(">>> No hay signal.")

        # Si hay posiciones abiertas, verificar si deben cerrarse
        elif len(positions) > 0:
            for position in positions:
                # Obtener datos actualizados y calcular el indicador con modo 1 (fin de tendencia)
                df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
                indicator_close = Trend(df)
                signal_close = indicator_close.triple_sma(PERIODO_LENTO, PERIODO_MEDIO, PERIODO_RAPIDO, 1)

                # Cerrar posiciones cuando la señal indica fin de tendencia
                # (compra -> señal de fin de tendencia alcista, venta -> señal de fin de tendencia bajista)
                if position.type == 0 and signal_close == 1 or position.type == 1 and signal_close == 2:
                    mtq.close_position(position)
                else:
                    print ("No hay signal que marque el cierre de la posición.")

        else:
            # Este bloque no debería ejecutarse normalmente, ya que está cubierto por las condiciones anteriores
            print("No hay posiciones abiertas.")

        # Pausa para evitar sobrecarga de solicitudes a MetaTrader 5
        time.sleep(1)

# Punto de entrada del programa
if __name__ == "__main__":
    # Ejecutar la función principal
    run()