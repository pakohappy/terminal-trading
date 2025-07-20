# -*- coding: utf-8 -*-
"""
Robot de Trading 1: Estrategia basada en el Oscilador Estocástico

Este robot implementa una estrategia de trading basada en el indicador estocástico,
que es un oscilador que mide la posición del precio actual en relación con su rango
de precios durante un período determinado. El robot busca oportunidades de compra
cuando el estocástico sale de la zona de sobreventa y oportunidades de venta cuando
sale de la zona de sobrecompra.
"""
import time
import MetaTrader5 as mt5
from log.log_loader import setup_logging
from trading_platform.Metaquotes import Metaquotes as mtq
from indicators.Oscillator import Oscillator

# Configuración del par de divisas y parámetros de trading
SYMBOL = 'USDJPY'          # Par de divisas a operar
TIMEFRAME = mt5.TIMEFRAME_M5  # Marco temporal (M5 = 5 minutos)
VOLUME = 0.01              # Tamaño de la posición en lotes
LAST_CANDLES = 30          # Número de velas a analizar
PIPS_SL = 50               # Stop Loss en pips
PIPS_TP = 70               # Take Profit en pips
DEVIATION = 100            # Desviación máxima permitida del precio
COMMENT = "Robot 1 Order"  # Comentario para identificar las órdenes

# Parámetros del indicador estocástico
K_PERIOD = 5               # Período para calcular %K (línea principal)
D_PERIOD = 3               # Período para calcular %D (línea de señal)
SMOOTH_K = 3               # Suavizado de la línea %K
OVERBOUGHT_LEVEL = 80      # Nivel de sobrecompra
OVERSOLD_LEVEL = 20        # Nivel de sobreventa
MODE = 0                   # Modo de operación (0 = señal en cruces en zonas de sobrecompra/sobreventa)

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
       - Si hay posiciones, monitorea las condiciones para cerrarlas (código comentado)
    
    Returns:
        None
        
    # TODO: 
    #   - Mejorar la lógica para que no cierre las posiciones en el cambio de tendencia,
    #     a no ser que se salga del espacio de sobrecompra/sobreventa.
    #   - Implementar gestión de riesgo dinámica basada en la volatilidad del mercado.
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
            print(f"ROBOT1 - Datos obtenidos desde MetaTrader 5.")
            
            # Crear una instancia del indicador Oscillator y calcular el estocástico
            indicator = Oscillator(df)
            signal = indicator.stochastic(K_PERIOD, D_PERIOD, SMOOTH_K, OVERBOUGHT_LEVEL, OVERSOLD_LEVEL, MODE)

            # Interpretar la señal y abrir órdenes según corresponda
            if signal == 2:  # Señal de compra (cruce al alza en zona de sobreventa)
                mtq.open_order_buy(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
            elif signal == 1:  # Señal de venta (cruce a la baja en zona de sobrecompra)
                mtq.open_order_sell(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
            else:  # No hay señal clara
                print(">>> No hay signal.")

        # Código comentado para gestionar una posición abierta
        # elif len(positions) == 1:
        #     for position in positions:
        #         # Obtener datos actualizados y calcular el indicador
        #         df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
        #         indicator = Oscillator(df)
        #         signal = indicator.stochastic(K_PERIOD, D_PERIOD, SMOOTH_K, OVERBOUGHT_LEVEL, OVERSOLD_LEVEL, MODE)
        #
        #         # Si la señal coincide con la posición actual, no hacer nada
        #         if position.type == 0 and signal == 2 or position.type == 1 and signal == 1:
        #             print(">>> No hay señal para abrir una segunda posición.")
        #
        #         # Si tenemos una posición de compra y hay señal de venta, abrir una posición de venta
        #         if position.type == 0 and signal == 1:
        #             mtq.open_order_sell(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
        #
        #         # Si tenemos una posición de venta y hay señal de compra, abrir una posición de compra
        #         if position.type == 1 and signal == 2:
        #             mtq.open_order_buy(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)

        # Código comentado para gestionar múltiples posiciones abiertas
        # elif len(positions) > 0:
        #     for position in positions:
        #         # Obtener datos actualizados y calcular el indicador
        #         df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
        #         indicator = Oscillator(df)
        #         signal = indicator.stochastic(K_PERIOD, D_PERIOD, SMOOTH_K, OVERBOUGHT_LEVEL, OVERSOLD_LEVEL, MODE)
        #
        #         # Cerrar posiciones cuando la señal es contraria a la posición
        #         # (compra -> señal de venta, venta -> señal de compra)
        #         if position.type == 0 and signal == 1 or position.type == 1 and signal == 2:
        #             mtq.close_position(position)
        #         else:
        #             print ("No hay signal que marque el cierre de la posición.")

        else:
            # Este bloque no debería ejecutarse normalmente, ya que está cubierto por la condición anterior
            print("No hay posiciones abiertas.")

        # Pausa para evitar sobrecarga de solicitudes a MetaTrader 5
        time.sleep(1)

# Punto de entrada del programa
if __name__ == "__main__":
    # Ejecutar la función principal
    run()