# -*- coding: utf-8 -*-
"""
Robot de Trading 3: Estrategia avanzada con Triple SMA y Alligator

Este robot implementa una estrategia de trading avanzada que combina dos indicadores:
1. Triple SMA (Triple Simple Moving Average): Utiliza tres medias móviles simples con 
   diferentes períodos para identificar tendencias en el mercado.
2. Alligator (Bill Williams): Un indicador que utiliza tres medias móviles suavizadas 
   y desplazadas para identificar tendencias y momentos de "despertar" del mercado.

Aunque el robot importa ambos indicadores, actualmente solo utiliza el Triple SMA para
generar señales de trading. La implementación del Alligator está preparada para futuras
mejoras en la estrategia.
"""
import time
import MetaTrader5 as mt5
from log.log_loader import setup_logging
from trading_platform.Metaquotes import Metaquotes as mtq
from indicators.Trend import Trend
from indicators.BillWilliams import BillWilliams

# Configuración del par de divisas y parámetros de trading
SYMBOL = 'USDJPY'           # Par de divisas a operar
TIMEFRAME = mt5.TIMEFRAME_M5  # Marco temporal (M5 = 5 minutos)
VOLUME = 0.01               # Tamaño de la posición en lotes
LAST_CANDLES = 20           # Número de velas a analizar
PIPS_SL = 100               # Stop Loss en pips
PIPS_TP = 500               # Take Profit en pips (más amplio que el SL para mejor ratio riesgo/beneficio)
DEVIATION = 100             # Desviación máxima permitida del precio
COMMENT = "Robot 3 Order"   # Comentario para identificar las órdenes

# Parámetros del indicador Triple SMA
PERIODO_LENTO = 8           # Período para la media móvil lenta
PERIODO_MEDIO = 6           # Período para la media móvil media
PERIODO_RAPIDO = 4          # Período para la media móvil rápida
MODE_1 = 0                  # Modo de operación (0 = señal en alineación de medias móviles)

# Parámetros del indicador Alligator (Bill Williams)
JAW_PERIOD = 13             # Período para la línea Jaw (Mandíbula)
JAW_OFFSET = 8              # Desplazamiento para la línea Jaw
TEETH_PERIOD = 8            # Período para la línea Teeth (Dientes)
TEETH_OFFSET = 5            # Desplazamiento para la línea Teeth
LIPS_PERIOD = 5             # Período para la línea Lips (Labios)
LIPS_OFFSET = 3             # Desplazamiento para la línea Lips
DROP_NAN = True             # Eliminar valores NaN resultantes
PERCENTAGE = 20             # Umbral de porcentaje para comparación
MODE_2 = 3                  # Modo de operación para Alligator

# Configuración del sistema de registro (logging)
setup_logging()

def run() -> None:
    """
    Función principal que ejecuta la lógica de trading del robot.
    
    Esta función:
    1. Inicializa la conexión con MetaTrader 5
    2. En un bucle continuo:
       - Verifica si hay posiciones abiertas
       - Si no hay posiciones, analiza el mercado usando el indicador Triple SMA y abre nuevas posiciones según las señales
       - Si hay posiciones, monitorea las condiciones para cerrarlas usando el modo de fin de tendencia del Triple SMA
    
    Returns:
        None
    
    Nota: Aunque el robot importa el indicador Alligator, actualmente no lo utiliza en la lógica de trading.
    Está preparado para futuras mejoras que podrían combinar ambos indicadores.
    
    # TODO:
    #   - Implementar la integración del indicador Alligator en la lógica de trading
    #   - Crear un filtro que combine las señales de Triple SMA y Alligator
    #   - Optimizar los parámetros de ambos indicadores mediante backtesting
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
            print(f"ROBOT3 - Datos obtenidos desde MetaTrader 5.")
            
            # Crear una instancia del indicador Trend y calcular el Triple SMA
            indicator = Trend(df)
            signal = indicator.triple_sma(PERIODO_LENTO, PERIODO_MEDIO, PERIODO_RAPIDO, MODE_1)

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