import MetaTrader5 as mt5
import pandas as pd

def sl_dynamic(stop_loss, min_pip_win):
    positions = mt5.positions_get()

    # Si no hay posiciones abiertas se anula el resto de la lógica.
    if positions is None or len(positions) == 0:
        return None

    # Convertir la tupla de posiciones en un DataFrame.
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())

    # Obtener una lista con los tickets abiertos.
    lista_tickets = df['ticket'].to_list()

    new_stop_loss =

    for ticket in lista_tickets:
        # Obtenemos el type de la posición.
        # 0 - BUY, 1 - SELL.
        ticket_type = mt5.symbol_info(ticket).type

        if price_current > price_open + stop_loss

    return lista_tickets
