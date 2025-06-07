import logging
import pandas as pd

class Trend:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def alligator(self,
                  jaw_period: int=13,
                  jaw_offset: int=8,
                  teeth_period: int=8,
                  teeth_offset: int=5,
                  lips_period: int=5,
                  lips_offset: int=3):
        """
        Calcula las tres líneas del indicador Alligator.
        Los parámetros por defecto son los establecidos por Bill Williams.

        Alcista: lips > teeth > jaw.
        Bajista: lips < teeth < jaw.

        Parámetros:
        - jaw_period: Número de períodos para calcular Jaw (Mandíbula).
        - jaw_offset: Cantidad de períodos de desplazamiento para Jaw.
        - teeth_period: Número de períodos para calcular Teeth (Dientes).
        - teeth_offset: Cantidad de períodos de desplazamiento para Teeth.
        - lips_period: Número de períodos para calcular Lips (Labios).
        - lips_offset: Cantidad de períodos de desplazamiento para Lips.
        """
        # Cálculo de las medias móviles suavizadas (SMA)
        self.df['jaw'] = self.df['close'].rolling(window=jaw_period).mean().shift(jaw_offset)
        self.df['teeth'] = self.df['close'].rolling(window=teeth_period).mean().shift(teeth_offset)
        self.df['lips'] = self.df['close'].rolling(window=lips_period).mean().shift(lips_offset)

        return self.df
