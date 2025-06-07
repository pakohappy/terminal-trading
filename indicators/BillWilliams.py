import logging
import pandas as pd

class BillWilliams:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def alligator(self,
                  jaw_period: int=13,
                  jaw_offset: int=8,
                  teeth_period: int=8,
                  teeth_offset: int=5,
                  lips_period: int=5,
                  lips_offset: int=3,
                  drop_nan: bool=True,
                  percentage: int=100,
                  mode: int=0):
        """
        Calcula las tres líneas del indicador Alligator.
        Los parámetros por defecto son los establecidos por Bill Williams.

        Alcista: lips(green) > teeth(red) > jaw(blue).
        Bajista: lips < teeth < jaw.

        Parámetros:
        - jaw_period: Número de períodos para calcular Jaw (Mandíbula).
        - jaw_offset: Cantidad de períodos de desplazamiento para Jaw.
        - teeth_period: Número de períodos para calcular Teeth (Dientes).
        - teeth_offset: Cantidad de períodos de desplazamiento para Teeth.
        - lips_period: Número de períodos para calcular Lips (Labios).
        - lips_offset: Cantidad de períodos de desplazamiento para Lips.
        """
        # Validar que el DataFrame tenga la columna 'close'.
        if 'close' not in self.df.columns:
            logging.error("ALLIGATOR - El DataFrame no contiene la columna 'close'.")
            raise ValueError("El DataFrame debe contener una columna 'close' para calcular la ALLIGATOR.")

        # Cálculo de las medias móviles suavizadas (SMA)
        self.df['jaw'] = self.df['close'].rolling(window=jaw_period).mean().shift(jaw_offset)
        self.df['teeth'] = self.df['close'].rolling(window=teeth_period).mean().shift(teeth_offset)
        self.df['lips'] = self.df['close'].rolling(window=lips_period).mean().shift(lips_offset)

        # Eliminar filas con NaN
        if drop_nan:
            self.df = self.df.dropna(subset=['jaw', 'teeth', 'lips']).copy()

        # Cálculo de la tendencia alcista (Lips > Teeth > Jaw).
        self.df['tendencia_alcista'] = (self.df['lips'] > self.df['teeth']) & (self.df['teeth'] > self.df['jaw'])
        tendencia_alcista = self.df['tendencia_alcista'].iloc[-1]

        # Cálculo de la tendencia bajista (Lips < Teeth < Jaw).
        self.df['tendencia_bajista'] = (self.df['lips'] < self.df['teeth']) & (self.df['teeth'] < self.df['jaw'])
        tendencia_bajista = self.df['tendencia_bajista'].iloc[-1]

        # Calcular las distancias:
        self.df['dist_jaw_teeth'] = abs(self.df['jaw'] - self.df['teeth'])  # Distancia entre Jaw y Teeth
        self.df['dist_teeth_lips'] = abs(self.df['teeth'] - self.df['lips'])  # Distancia entre Teeth y Lips
        self.df['dist_jaw_lips'] = abs(self.df['jaw'] - self.df['lips'])  # Jaw - Lips (opcional)

        # Calcular el cambio porcentual en las distancias
        self.df['perc_change_jaw_teeth'] = self.df['dist_jaw_teeth'].pct_change() * 100  # % cambio Jaw-Teeth
        self.df['perc_change_teeth_lips'] = self.df['dist_teeth_lips'].pct_change() * 100  # % cambio Teeth-Lips
        self.df['perc_change_jaw_lips'] = self.df['dist_jaw_lips'].pct_change() * 100  # % cambio Jaw-Lips

        # Comparar distancias con períodos anteriores (e.g., 1 período atrás)
        self.df['change_jaw_teeth'] = self.df['dist_jaw_teeth'].diff()  # Diferencia de Jaw-Teeth vs. período anterior
        self.df['change_teeth_lips'] = self.df['dist_teeth_lips'].diff()  # Diferencia de Teeth-Lips vs. período anterior

        # Comparar si la distancia actual es mayor o menor al período anterior.
        self.df['is_jaw_teeth_growing'] = self.df['change_jaw_teeth'] > 0  # True si aumenta
        self.df['is_teeth_lips_growing'] = self.df['change_teeth_lips'] > 0  # True si aumenta

        # Detectamos tendencia alcista/bajista.
        if mode == 0:
            if tendencia_alcista:
                return 2
            elif tendencia_bajista:
                return 1
            else:
                return -1

        # Detectamos si la línea de los labios(verde) se aproxima a la línea de los dientes(rojo).
        if mode == 1:
            if self.df['is_teeth_lips_growing'].iloc[-1]:
                return 1

        # Detectamos si la línea de los labios(verde) y la línea de la mandíbula(azul)
        # se aproximan a la línea de los dientes(rojo).
        if mode == 2:
            if self.df['is_jaw_teeth_growing'].iloc[-1] and self.df['is_teeth_lips_growing'].iloc[-1]:
                return 1

        # Detectamos si la línea de los labios(verde) se aproxima a la línea de los dientes(rojo).
        # Pero ahora de forma percentual.
        if mode == 3:
            if self.df['perc_change_teeth_lips'].iloc[-1] > percentage:
                return 1

        return 0