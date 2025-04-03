import logging
import pandas as pd

class Tendencia:
    # Puedo optimizar pasando solo la columna close, pero no es necesario.
    def __init__(self, df: pd.DataFrame, ): 
        self.df = df

    def macd(self) -> pd.DataFrame:
        """
        Calcula la tendencia utilizando el MACD (Moving Average Convergence Divergence).
        El MACD es un indicador de tendencia que muestra la relación entre dos medias móviles de un activo.
        Se considera una señal de compra cuando el MACD cruza por encima de la señal (EMA de 9 periodos del MACD).
        Se considera una señal de venta cuando el MACD cruza por debajo de la señal.
        El MACD se calcula restando la EMA de 26 periodos de la EMA de 12 periodos.
        Luego, se calcula la señal como la EMA de 9 periodos del MACD.
        Finalmente, se detectan los cruces alcistas y bajistas del MACD con respecto a la señal.
        Se añaden las columnas 'macd', 'signal', 'cruce_alcista' y 'cruce_bajista' al DataFrame original.
        """
        # Validar que el DataFrame tenga la columna 'Close'.
        if 'Close' not in self.df.columns:
            logging.error("MACD - El DataFrame no contiene la columna 'Close'.")
            raise ValueError("El DataFrame debe contener una columna 'Close' para calcular el MACD.")

        # Cálculo de las medias móviles.
        df_ema12 = self.df['Close'].ewm(span=12, adjust=False).mean()
        df_ema26 = self.df['Close'].ewm(span=26, adjust=False).mean()

        # Cálculo del MACD.
        self.df['macd'] = df_ema12 - df_ema26

        # Cálculo de la señal (EMA de 9 periodos del MACD)
        self.df['signal'] = self.df['macd'].ewm(span=9, adjust=False).mean()

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
            return "Cruce alcista detectado. Abrir posición larga."
        elif ultimo_cruce_bajista:
            return "Cruce bajista detectado. Abrir posición corta."
        else:
            return "No se detectaron cruces."