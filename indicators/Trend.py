import logging
import pandas as pd

class Trend:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def macd(self,
             periodo_rapido=int,
             periodo_lento=int,
             periodo_senyal=int) -> int:
        """
        Calcula la tendencia utilizando el MACD (Moving Average Convergence Divergence).
        """
        # Validar que el DataFrame tenga la columna 'close'.
        if 'close' not in self.df.columns:
            logging.error("MACD - El DataFrame no contiene la columna 'Close'.")
            raise ValueError("El DataFrame debe contener una columna 'Close' para calcular el MACD.")

        # Cálculo de las medias móviles.
        df_ema12 = self.df['close'].ewm(span=periodo_rapido, adjust=False).mean()
        df_ema26 = self.df['close'].ewm(span=periodo_lento, adjust=False).mean()

        # Cálculo del MACD.
        self.df['macd'] = df_ema12 - df_ema26

        # Cálculo de la señal (EMA de 9 periodos del MACD)
        self.df['signal'] = self.df['macd'].ewm(span=periodo_senyal, adjust=False).mean()

        # Detectar cruces alcistas. (posición larga)
        # La señal se considera alcista cuando el MACD cruza por encima de la señal.
        self.df['cruce_alcista'] = (self.df['macd'].shift(1) <= self.df['signal'].shift(1)) & (self.df['macd'] > self.df['signal'])

        # Detectar cruces bajistas. (posición corta)
        # La señal se considera bajista cuando el MACD cruza por debajo de la señal.
        self.df['cruce_bajista'] = (self.df['macd'].shift(1) >= self.df['signal'].shift(1)) & (self.df['macd'] < self.df['signal'])

        ultimo_cruce_alcista = self.df['cruce_alcista'].iloc[-1]
        ultimo_cruce_bajista = self.df['cruce_bajista'].iloc[-1]
        
        # Imprimir el último cruce alcista y bajista.
        if ultimo_cruce_alcista:
            logging.info("MACD - Se detectó un cruce alcista.")
            return 0
        elif ultimo_cruce_bajista:
            logging.info("MACD - Se detectó un cruce bajista.")
            return 1
        else:
            logging.info("MACD - No se detectaron cruces alcistas o bajistas.")
            return -1

    def sma(self, periodo=int):
        """
        Calcula la tendencia utilizando la SMA (Simple Moving Average).
        """
        # Validar que el DataFrame tenga la columna 'close'
        if 'close' not in self.df.columns:
            logging.error("SMA - El DataFrame no contiene la columna 'close'.")
            raise ValueError("El DataFrame debe contener una columna 'close' para calcular la SMA.")

        # Calcular la SMA
        self.df['sma'] = self.df['close'].rolling(window=periodo).mean()

        # Eliminar filas con NaN
        self.df = self.df.dropna()

        # Determinar la tendencia
        self.df['tendencia'] = self.df['close'] > self.df['sma']

        # Reset index del DataFrame.
        # df_sin_nan = df_sin_nan.reset_index(drop=True)

        # Obtener la última tendencia
        ultima_tendencia = self.df['tendencia'].iloc[-1]

        if ultima_tendencia:
            logging.info("SMA - Tendencia alcista detectada.")
            return 0  # Tendencia alcista
        else:
            logging.info("SMA - Tendencia bajista detectada.")
            return 1  # Tendencia bajista

    def triple_sma(self,
                   periodo_lento: int=8,
                   periodo_medio: int=6,
                   periodo_rapido: int=4):
        """
        Calcula la tendencia utilizando la TRIPE SMA (Triple Moving Average).
        """
        # Validar que el DataFrame tenga la columna 'close'.
        if 'close' not in self.df.columns:
            logging.error("SMA - El DataFrame no contiene la columna 'close'.")
            raise ValueError("El DataFrame debe contener una columna 'close' para calcular la SMA.")

        # Calcular las SMA_lento, SMA_medio y SMA_rapido.
        self.df['sma_lento'] = self.df['close'].rolling(window=periodo_lento).mean()
        self.df['sma_medio'] = self.df['close'].rolling(window=periodo_medio).mean()
        self.df['sma_rapido'] = self.df['close'].rolling(window=periodo_rapido).mean()

        # Eliminar filas con NaN
        self.df = self.df.dropna()
