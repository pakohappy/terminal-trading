# -*- coding: utf-8 -*-
"""
Módulo de estrategias de stop loss dinámico.

Este módulo implementa diversas estrategias para gestionar stops dinámicos que se
ajustan automáticamente a medida que el precio se mueve. Los stops dinámicos ayudan
a proteger las ganancias mientras permiten que las operaciones rentables continúen
desarrollándose.

Las estrategias implementadas incluyen:
- Stop Loss Follower: Mantiene el stop loss a una distancia fija del precio actual
- Stop Loss SMA: Utiliza una media móvil simple como nivel de stop loss

Este módulo puede ejecutarse como un script independiente para aplicar la estrategia
de stop loss follower o la estrategia de stop loss SMA a todas las posiciones abiertas.

Ejemplo de uso como módulo:
    ```python
    from strategy.StopsDynamic import StopsDynamic
    
    # Crear instancia
    stops = StopsDynamic()
    
    # Aplicar estrategia follower con 50 pips
    stops.sl_follower(50)
    
    # O aplicar estrategia SMA con 20 periodos y 30 pips
    stops.sl_sma(30, 20)
    ```

Ejemplo de uso como script:
    ```
    python StopsDynamic.py
    ```
"""
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import logging
import time
import argparse
import sys
from typing import Optional, List, Union, Dict, Any, Tuple

# Constantes
LOG_PREFIX = "SL_DYNAMIC"
DEFAULT_TIMEFRAME = mt5.TIMEFRAME_H1  # Timeframe por defecto para datos históricos
DEFAULT_PIPS_SL = 50                  # Distancia en pips por defecto para el stop loss
DEFAULT_SMA_PERIODS = 20              # Periodos por defecto para la SMA
DEFAULT_SLEEP_TIME = 60               # Tiempo de espera entre iteraciones (segundos)
DEFAULT_ERROR_SLEEP_TIME = 5          # Tiempo de espera tras error (segundos)


def get_tickets() -> Optional[List[int]]:
    """
    Obtiene los tickets (identificadores) de todas las posiciones abiertas.
    
    Returns:
        Optional[List[int]]: Lista de tickets de las posiciones abiertas, o None si no hay posiciones
                           o si ocurre un error al obtener la información.
    """
    # Obtener el DataFrame de posiciones abiertas.
    positions = mt5.positions_get()

    # Si no hay posiciones abiertas se anula el resto de la lógica.
    if positions is None or len(positions) == 0:
        logging.info(f"{LOG_PREFIX} - No hay posiciones abiertas.")
        return None

    try:
        # Convertir la tupla de posiciones en un DataFrame.
        df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
        # Obtener una lista con los tickets abiertos.
        tickets = df['ticket'].to_list()
        logging.info(f"{LOG_PREFIX} - Se encontraron {len(tickets)} posiciones abiertas.")
        return tickets
    except Exception as ex:
        logging.error(f"{LOG_PREFIX} - Error al convertir la tupla de posiciones a DataFrame: {ex}")
        return None

def send_order(ticket: int, sl: float, tp: Optional[float] = None) -> bool:
    """
    Envía una orden para modificar el stop loss y/o take profit de una posición.
    
    Args:
        ticket: Identificador de la posición
        sl: Nuevo nivel de stop loss
        tp: Nuevo nivel de take profit (opcional)
        
    Returns:
        bool: True si la orden se envió correctamente, False en caso contrario
    """
    request = {
        'action': mt5.TRADE_ACTION_SLTP,
        'position': ticket,
        'sl': sl,
        'tp': tp,
    }
    logging.debug(f"{LOG_PREFIX} - Enviando orden: {request}")

    try:
        result = mt5.order_send(request)
        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info(f"{LOG_PREFIX} - Orden enviada correctamente: {ticket} -> SL={sl}")
            return True
        else:
            error_code = result.retcode if result is not None else "desconocido"
            logging.error(f"{LOG_PREFIX} - Falló el envío de la orden. Código de error: {error_code}")
            return False
    except Exception as error:
        logging.error(f"{LOG_PREFIX} - Error al actualizar SL: {error}")
        return False

def get_point(posicion: Any) -> float:
    """
    Obtiene el valor del punto (point) para el símbolo de la posición.
    
    El valor del punto es la unidad mínima de cambio en el precio del símbolo.
    Se utiliza para calcular distancias en el gráfico, como la distancia del stop loss.
    
    Args:
        posicion: Objeto posición de MetaTrader5 que contiene el atributo 'symbol'
        
    Returns:
        float: Valor del punto para el símbolo
        
    Raises:
        Exception: Si no se puede obtener la información del símbolo
    """
    symbol_info = mt5.symbol_info(posicion.symbol)
    if symbol_info is None:
        error_msg = f"No se pudo obtener información para el símbolo {posicion.symbol}"
        logging.error(f"{LOG_PREFIX} - {error_msg}")
        raise Exception(error_msg)
    
    return symbol_info.point

class StopsDynamic:
    """
    Clase que implementa estrategias de stop loss dinámico.
    
    Esta clase proporciona diferentes métodos para gestionar stops dinámicos
    que se ajustan automáticamente según el movimiento del precio. Las estrategias
    implementadas ayudan a proteger las ganancias mientras permiten que las 
    operaciones rentables continúen desarrollándose.
    
    Estrategias disponibles:
        - sl_follower: Mantiene el stop loss a una distancia fija del precio actual
        - sl_sma: Utiliza una media móvil simple como nivel de stop loss
        
    Ejemplo de uso:
        ```python
        # Crear instancia
        stops = StopsDynamic()
        
        # Usar estrategia follower con 50 pips de distancia
        stops.sl_follower(50)
        
        # Usar estrategia SMA con 20 periodos y 30 pips de margen
        stops.sl_sma(30, 20)
        ```
    """
    @staticmethod
    def sl_follower(pips_sl: int) -> None:
        """
        Estrategia de Stop Loss Follower.
        
        Mantiene el stop loss a una distancia fija (en pips) del precio actual,
        permitiendo que el stop loss "siga" al precio cuando este se mueve favorablemente.
        El stop loss nunca retrocede, solo avanza en la dirección favorable.
        
        Args:
            pips_sl: Distancia en pips a mantener entre el precio actual y el stop loss
        """
        tickets = get_tickets()
        if not tickets:
            return
            
        for ticket in tickets:
            try:
                # Obtenemos información de la posición
                posiciones = mt5.positions_get(ticket=ticket)
                if not posiciones:
                    logging.warning(f"{LOG_PREFIX} - No se pudo obtener información para el ticket {ticket}")
                    continue
                    
                posicion = posiciones[0]
                point = get_point(posicion)
                
                logging.debug(f"{LOG_PREFIX} - Procesando ticket {ticket}, SL actual: {posicion.sl}")
                
                # Calcular nuevo stop loss según el tipo de operación (compra/venta)
                if posicion.type == 0:  # Compra (BUY)
                    # Calcular nuevo SL a la distancia especificada por debajo del precio actual
                    new_sl = posicion.price_current - pips_sl * point
                    
                    # Si no hay SL establecido, usar precio de apertura como referencia
                    if posicion.sl == 0.0:
                        new_sl = posicion.price_open - pips_sl * point
                        
                    # No retroceder el SL (solo avanzar)
                    if posicion.sl > 0 and new_sl < posicion.sl:
                        new_sl = posicion.sl
                        
                elif posicion.type == 1:  # Venta (SELL)
                    # Calcular nuevo SL a la distancia especificada por encima del precio actual
                    new_sl = posicion.price_current + pips_sl * point
                    
                    # Si no hay SL establecido, usar precio de apertura como referencia
                    if posicion.sl == 0.0:
                        new_sl = posicion.price_open + pips_sl * point
                        
                    # No retroceder el SL (solo avanzar)
                    if posicion.sl > 0 and new_sl > posicion.sl:
                        new_sl = posicion.sl
                else:
                    logging.error(f"{LOG_PREFIX} - Tipo de posición desconocido: {posicion.type}")
                    continue
                
                # Enviar la orden para actualizar el stop loss
                if new_sl != posicion.sl:
                    send_order(ticket, new_sl)
                else:
                    logging.debug(f"{LOG_PREFIX} - No es necesario actualizar el SL para el ticket {ticket}")
                    
            except Exception as e:
                logging.error(f"{LOG_PREFIX} - Error al procesar el ticket {ticket}: {e}")

    @staticmethod
    def sl_sma(pips_sl: int, periodos_sma: int) -> None:
        """
        Estrategia de Stop Loss basada en Media Móvil Simple (SMA).
        
        Utiliza una media móvil simple como nivel de stop loss, añadiendo un margen
        adicional en pips. Esta estrategia permite que el stop loss se ajuste según
        la tendencia del mercado.
        
        Args:
            pips_sl: Margen adicional en pips para el stop loss
            periodos_sma: Número de periodos para calcular la SMA
        """
        tickets = get_tickets()
        if not tickets:
            return
            
        for ticket in tickets:
            try:
                # Obtenemos información de la posición
                posiciones = mt5.positions_get(ticket=ticket)
                if not posiciones:
                    logging.warning(f"{LOG_PREFIX} - No se pudo obtener información para el ticket {ticket}")
                    continue
                    
                posicion = posiciones[0]
                point = get_point(posicion)
                symbol = posicion.symbol
                
                # Obtener datos históricos para calcular la SMA
                rates = mt5.copy_rates_from_pos(symbol, DEFAULT_TIMEFRAME, 0, periodos_sma + 10)
                
                if rates is None or len(rates) < periodos_sma:
                    logging.error(f"{LOG_PREFIX} - No se pudieron obtener suficientes datos históricos para {symbol}")
                    continue
                    
                # Convertir a DataFrame y calcular la SMA
                rates_df = pd.DataFrame(rates)
                sma_value = rates_df['close'].rolling(window=periodos_sma).mean().iloc[-1]
                
                if np.isnan(sma_value):
                    logging.error(f"{LOG_PREFIX} - Error al calcular la SMA para {symbol}")
                    continue
                
                # Calcular nuevo stop loss según el tipo de operación (compra/venta)
                if posicion.type == 0:  # Compra (BUY)
                    # Para compras, el SL se coloca por debajo de la SMA con un margen
                    new_sl = sma_value - pips_sl * point
                    
                    # No retroceder el SL (solo avanzar)
                    if posicion.sl > 0 and new_sl < posicion.sl:
                        new_sl = posicion.sl
                        
                elif posicion.type == 1:  # Venta (SELL)
                    # Para ventas, el SL se coloca por encima de la SMA con un margen
                    new_sl = sma_value + pips_sl * point
                    
                    # No retroceder el SL (solo avanzar)
                    if posicion.sl > 0 and new_sl > posicion.sl:
                        new_sl = posicion.sl
                else:
                    logging.error(f"{LOG_PREFIX} - Tipo de posición desconocido: {posicion.type}")
                    continue
                
                logging.info(f"{LOG_PREFIX} - SMA({periodos_sma}) para {symbol}: {sma_value}, nuevo SL: {new_sl}")
                
                # Enviar la orden para actualizar el stop loss
                if new_sl != posicion.sl:
                    send_order(ticket, new_sl)
                else:
                    logging.debug(f"{LOG_PREFIX} - No es necesario actualizar el SL para el ticket {ticket}")
                    
            except Exception as e:
                logging.error(f"{LOG_PREFIX} - Error al procesar el ticket {ticket}: {e}")

if __name__ == "__main__":
    """
    Ejemplo de uso del módulo como script independiente.
    
    Este bloque se ejecuta cuando el archivo se ejecuta directamente como script.
    Configura el logging, inicializa la conexión con MetaTrader5 y ejecuta la
    estrategia de stop loss seleccionada en un bucle continuo.
    
    Uso desde línea de comandos:
        python StopsDynamic.py --estrategia follower --pips 50
        python StopsDynamic.py --estrategia sma --pips 30 --periodos 20
        python StopsDynamic.py --help
    """
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Script de stops dinámicos para MetaTrader5')
    parser.add_argument('--estrategia', type=str, choices=['follower', 'sma'], default='follower',
                        help='Estrategia a utilizar: follower o sma')
    parser.add_argument('--pips', type=int, default=DEFAULT_PIPS_SL,
                        help=f'Distancia en pips para el stop loss (default: {DEFAULT_PIPS_SL})')
    parser.add_argument('--periodos', type=int, default=DEFAULT_SMA_PERIODS,
                        help=f'Periodos para la SMA (default: {DEFAULT_SMA_PERIODS}, solo para estrategia sma)')
    parser.add_argument('--intervalo', type=int, default=DEFAULT_SLEEP_TIME,
                        help=f'Intervalo en segundos entre iteraciones (default: {DEFAULT_SLEEP_TIME})')
    parser.add_argument('--debug', action='store_true',
                        help='Activar modo debug (logging más detallado)')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Configurar el logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info(f"{LOG_PREFIX} - Iniciando script de stops dinámicos")
    
    # Mostrar configuración
    logging.info(f"{LOG_PREFIX} - Configuración: estrategia={args.estrategia}, pips={args.pips}, "
                f"periodos={args.periodos}, intervalo={args.intervalo}")

    # Inicializar conexión con MetaTrader5
    if not mt5.initialize():
        logging.error(f"{LOG_PREFIX} - Error al inicializar MetaTrader5")
        sys.exit(1)
    
    logging.info(f"{LOG_PREFIX} - Conexión con MetaTrader5 establecida. Versión: {mt5.version()}")

    try:
        # Bucle infinito
        while True:
            try:
                # Crear instancia de StopsDynamic
                stops = StopsDynamic()
                
                # Ejecutar la estrategia seleccionada
                if args.estrategia == "follower":
                    logging.info(f"{LOG_PREFIX} - Ejecutando estrategia SL Follower con {args.pips} pips")
                    stops.sl_follower(args.pips)
                elif args.estrategia == "sma":
                    logging.info(f"{LOG_PREFIX} - Ejecutando estrategia SL SMA con {args.periodos} periodos y {args.pips} pips")
                    stops.sl_sma(args.pips, args.periodos)
                else:
                    logging.error(f"{LOG_PREFIX} - Estrategia desconocida: {args.estrategia}")
                    break
                
                # Pausa entre iteraciones
                logging.debug(f"{LOG_PREFIX} - Esperando {args.intervalo} segundos para la próxima iteración...")
                time.sleep(args.intervalo)
                
            except Exception as e:
                logging.error(f"{LOG_PREFIX} - Error en el bucle principal: {e}")
                time.sleep(DEFAULT_ERROR_SLEEP_TIME)  # Pausa breve antes de reintentar en caso de error
                continue

    finally:
        # Cerrar conexión con MetaTrader5
        logging.info(f"{LOG_PREFIX} - Cerrando conexión con MetaTrader5")
        mt5.shutdown()


