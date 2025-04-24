import MetaTrader5 as mt5
import pandas as pd
import logging

def sl_dynamic(pips_sl):
    positions = mt5.positions_get()

    # Si no hay posiciones abiertas se anula el resto de la lógica.
    if positions is None or len(positions) == 0:
        return None
    else:
        # Convertir la tupla de posiciones en un DataFrame.
        df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())\
        # Obtener una lista con los tickets abiertos.
        lista_tickets = df['ticket'].to_list()

        for ticket in lista_tickets:
            # Obtenemos información de la posición.
            # 0 - BUY, 1 - SELL.
            posicion = mt5.positions_get(ticket=ticket)[0]
            ticket_type = posicion.type
            price_current = posicion.price_current
            position_profit = posicion.profit
            new_sl = 0

            if ticket_type == 0:
                if position_profit > 0:
                    new_sl = price_current - pips_sl
                print(ticket)
            elif ticket_type == 1:
                if position_profit > 0:
                    new_sl = price_current + pips_sl
                print(ticket)
            else:
                logging.info("SL_DYNAMIC - ERROR al obtener el 'type' del ticket.")

            request = {
                'action': mt5.TRADE_ACTION_SLTP,
                'position': ticket,
                'sl': new_sl,
            }
            try:
                result = mt5.order_send(request)
                print(result)
            except Exception as e:
                logging.error(f"SL_DYNAMIC - Error al actualizar SL: {e}")

            return None

        return None
