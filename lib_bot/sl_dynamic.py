import MetaTrader5 as mt5
import pandas as pd

def sl_dynamic():
    positions = mt5.positions_get()

    # Si no hay posiciones abiertas se anula el resto de la lógica.
    if positions is None or len(positions) == 0:
        return None

    # Convertir la tupla de posiciones en un DataFrame.
    '''
    El DataFrame resultante incluirá todas las columnas disponibles en las posiciones, como:
    - `ticket` (número de ticket de la posición)
    - `time` (tiempo de apertura)
    - `type` (tipo de orden: compra/venta)
    - `volume` (volumen de la operación)
    - `symbol` (símbolo del instrumento)
    - `price_open` (precio de apertura)
    - `sl` (stop loss)
    - `tp` (take profit)
    - Y otros datos relevantes
    '''
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())

    # Obtener una lista con los tickets abiertos.
    lista_tickets = df['ticket'].to_list()

    return None
