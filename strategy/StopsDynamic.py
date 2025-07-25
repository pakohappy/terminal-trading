# -*- coding: utf-8 -*-
"""
Módulo de estrategias de stop loss dinámico.

Este módulo implementa diversas estrategias para gestionar stops dinámicos que se
ajustan automáticamente a medida que el precio se mueve. Los stops dinámicos ayudan
a proteger las ganancias mientras permiten que las operaciones rentables continúen
desarrollándose.

Las estrategias implementadas incluyen:
- Stop Loss Follower: Mantiene el stop loss a una distancia fija del precio actual
- Stop Loss SMA: Utiliza una media móvil simple como nivel de stop loss (en desarrollo)

Este módulo puede ejecutarse como un script independiente para aplicar la estrategia
de stop loss follower a todas las posiciones abiertas.
"""
import MetaTrader5 as mt5
import pandas as pd
import logging
import time
from typing import Optional, List, Union, Dict, Any


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
        print("No hay posiciones abiertas.")
        return None

    try:
        # Convertir la tupla de posiciones en un DataFrame.
        df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
        # Obtener una lista con los tickets abiertos.
        tickets = df['ticket'].to_list()
    except Exception as ex:
        logging.error(f"SL_DYNAMIC - Error al convertir la tupla de posiciones a DataFrame: {ex}")
        return None

    return tickets

def send_order(ticket, sl, tp=None):
    """
    Función para enviar la orden SL/TP.
    """
    request = {
        'action': mt5.TRADE_ACTION_SLTP,
        'position': ticket,
        'sl': sl,
        'tp': tp,
    }
    print(request)

    try:
        result = mt5.order_send(request)
        if result is not None:
            logging.info(f"SL_DYNAMIC - Orden enviada: {ticket}->{result.comment}")
        else:
            logging.error(f"SL_DYNAMIC - Falló el envío de la orden.")
    except Exception as error:
        logging.error(f"SL_DYNAMIC - Error al actualizar SL: {error}")

def get_point(posicion):
    """
    Obtiene el point de la posición.
    """
    symbol_info = mt5.symbol_info(posicion.symbol)
    point = symbol_info.point
    return point

class StopsDynamic:
    """
    Clase que implementa las estrategias de SL/TP.
    """
    @staticmethod
    def sl_follower(pips_sl):
        """
        Estrategia SL follower.
        - Mantiene el SL a una cantidad de pips determinada.
        """
        tickets = get_tickets()

        for ticket in tickets:
            new_sl = 0

            # Obtenemos información de la posición.
            posicion = mt5.positions_get(ticket=ticket)[0]
            # print(ticket_type, price_current, position_profit, symbol)
            print(f'El stop loss actual es: {posicion.sl}')
            point = get_point(posicion)

            if posicion.type == 0:
                new_sl = posicion.price_current - pips_sl * point
                if posicion.sl == 0.0:
                    new_sl = posicion.price_open - pips_sl * point
                if new_sl < posicion.sl:
                    new_sl = posicion.sl
            elif posicion.type == 1:
                new_sl = posicion.price_current + pips_sl * point
                if posicion.sl == 0.0:
                    new_sl = posicion.price_open + pips_sl * point
                if new_sl > posicion.sl != 0:
                    new_sl = posicion.sl
            else:
                logging.info("SL_DYNAMIC - ERROR al obtener el 'type' del ticket.")

            send_order(ticket, new_sl,)

    @staticmethod
    def sl_sma(pip_sl, peridos_sma):
        tickets = get_tickets()

        for ticket in tickets:
            new_sl = 0

            # Obtenemos información de la posición.
            posicion = mt5.positions_get(ticket=ticket)[0]
            # print(ticket_type, price_current, position_profit, symbol)
            print(f'El stop loss actual es: {posicion.sl}')
            point = get_point(posicion)

            if posicion.type == 0:#todo comparar con 1
                print(posicion.type)#todo borrar
            elif posicion.type == 1:
                print(posicion.type)#todo borrar
            else:
                logging.info("SL_DYNAMIC - ERROR al obtener el 'type' del ticket.")

            send_order(ticket, new_sl,)

if __name__ == "__main__":
    # Configurar el logging
    logging.basicConfig(level=logging.INFO)

    # Inicializar conexión con MetaTrader5
    if not mt5.initialize():
        logging.error("SL_DYNAMIC - Error al inicializar MetaTrader5")
        quit()

    try:
        # Bucle infinito
        while True:
            try:
                PIP_SL_PARAM = 50
                sldyn = SlDynamic(PIP_SL_PARAM)
                sldyn.sl_follower()
                # Opcional: añadir una pausa entre iteraciones
                time.sleep(1)  # Pausa de 60 segundos entre cada ejecución
            except Exception as e:
                logging.error(f"Error en el bucle principal: {e}")
                time.sleep(1)  # Pausa breve antes de reintentar en caso de error
                continue

    finally:
        # Cerrar conexión con MetaTrader5
        mt5.shutdown()


