import MetaTrader5 as mt5
import pandas as pd
import logging
import time

def sl_dynamic(pips_sl): #todo falta hacer que el sl no se vuelva atrás.
    positions = mt5.positions_get()

    # Si no hay posiciones abiertas se anula el resto de la lógica.
    if positions is None or len(positions) == 0:
        return None

    # Convertir la tupla de posiciones en un DataFrame.
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    # Obtener una lista con los tickets abiertos.
    lista_tickets = df['ticket'].to_list()

    for ticket in lista_tickets:
        # Obtenemos información de la posición.
        # 0 - BUY, 1 - SELL.
        posicion = mt5.positions_get(ticket=ticket)[0]
        new_sl = 0

        #print(ticket_type, price_current, position_profit, symbol)
        print(f'El stop loss actual es: {posicion.sl}')

        # Obtener el symbol de la posición.
        symbol_info = mt5.symbol_info(posicion.symbol)
        # Obtener el punto del símbolo.
        point = symbol_info.point

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

        request = {
            'action': mt5.TRADE_ACTION_SLTP,
            'position': ticket,
            'sl': new_sl,
        }
        print(request)

        if new_sl == 0:
            print(">>> No es necesario actualizar el STOP LOSS.")
        else:
            try:
                result = mt5.order_send(request)
                if result is not None:
                    logging.info(f"SL_DYNAMIC - Orden enviada: {posicion.ticket}->{result.comment}")
                else:
                    logging.error(f"SL_DYNAMIC - Falló el envío de la orden.")
            except Exception as error:
                logging.error(f"SL_DYNAMIC - Error al actualizar SL: {error}")

    return None

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
                sl_dynamic(PIP_SL_PARAM)
                # Opcional: añadir una pausa entre iteraciones
                time.sleep(1)  # Pausa de 60 segundos entre cada ejecución
            except Exception as e:
                logging.error(f"Error en el bucle principal: {e}")
                time.sleep(1)  # Pausa breve antes de reintentar en caso de error
                continue

    finally:
        # Cerrar conexión con MetaTrader5
        mt5.shutdown()


