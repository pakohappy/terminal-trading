import MetaTrader5 as mt5
import pandas as pd

def sl_dynamic():
    positions = mt5.positions_get()

    # Si no hay posiciones abiertas se anula el resto de la lógica.
    if positions is None or len(positions) == 0:
        return None

    # Convertir la tupla de posiciones en un DataFrame.
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())

    return None
