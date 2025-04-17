import logging
import pandas as pd
from configuracion.config_loader import ConfigLoader

class Tendencia:
    def __init__(self, periodo_rapido, periodo_lento, periodo_senyal, df: pd.DataFrame):
        self.periodo_rapido = periodo_rapido
        self.periodo_lento = periodo_lento
        self.periodo_senyal = periodo_senyal
        self.df = df

    def macd(self):
        """
        Calcula la tendencia utilizando el MACD (Moving Average Convergence Divergence).
        """
        # Validar que el DataFrame tenga la columna 'close'.
        if 'close' not in self.df.columns:
            logging.error("MACD - El DataFrame no contiene la columna 'Close'.")
            raise ValueError("El DataFrame debe contener una columna 'Close' para calcular el MACD.")

        # Cálculo de las medias móviles.
        df_ema12 = self.df['close'].ewm(span=self.periodo_rapido, adjust=False).mean()
        df_ema26 = self.df['close'].ewm(span=self.periodo_lento, adjust=False).mean()

        # Cálculo del MACD.
        self.df['macd'] = df_ema12 - df_ema26

        # Cálculo de la señal (EMA de 9 periodos del MACD)
        self.df['signal'] = self.df['macd'].ewm(span=self.periodo_senyal, adjust=False).mean()

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
            return 'buy'
        elif ultimo_cruce_bajista:
            logging.info("MACD - Se detectó un cruce bajista.")
            return 'sell'
        else:
            logging.info("MACD - No se detectaron cruces alcistas o bajistas.")
            return 'flat'