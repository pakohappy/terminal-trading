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
                   periodo_rapido: int=4,
                   mode: int=0) -> int:
        """
        Calcula la tendencia utilizando la TRIPLE SMA (Triple Moving Average).

            Default mode = 0.
                Devuelve la alineación alcista(R>M>L)/bajista(L>M>R).
            Mode = 1.
                Devuelve el fin de la tendencia.
                Fin tendencia, alcista(R<M), bajista(L<M).
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

        # Detectar cruces y alineación de las medias
        ultima_fila = self.df.iloc[-1]

        # Verificar alineación alcista (rápida > media > lenta)
        alineacion_alcista = (ultima_fila['sma_rapido'] > ultima_fila['sma_medio'] > ultima_fila['sma_lento'])

        # Verificar alineación bajista (rápida < media < lenta)
        alineacion_bajista = (ultima_fila['sma_rapido'] < ultima_fila['sma_medio'] < ultima_fila['sma_lento'])

        # Detectar cruces alcistas entre todas las líneas
        self.df['cruce_rapido_medio'] = (
                (self.df['sma_rapido'].shift(1) <= self.df['sma_medio'].shift(1)) &
                (self.df['sma_rapido'] > self.df['sma_medio'])
        )

        self.df['cruce_medio_lento'] = (
                (self.df['sma_medio'].shift(1) <= self.df['sma_lento'].shift(1)) &
                (self.df['sma_medio'] > self.df['sma_lento'])
        )

        self.df['cruce_rapido_lento'] = (
                (self.df['sma_rapido'].shift(1) <= self.df['sma_lento'].shift(1)) &
                (self.df['sma_rapido'] > self.df['sma_lento'])
        )

        # Detectar cruces bajistas entre todas las líneas
        self.df['cruce_rapido_medio_bajista'] = (
                (self.df['sma_rapido'].shift(1) >= self.df['sma_medio'].shift(1)) &
                (self.df['sma_rapido'] < self.df['sma_medio'])
        )

        self.df['cruce_medio_lento_bajista'] = (
                (self.df['sma_medio'].shift(1) >= self.df['sma_lento'].shift(1)) &
                (self.df['sma_medio'] < self.df['sma_lento'])
        )

        self.df['cruce_rapido_lento_bajista'] = (
                (self.df['sma_rapido'].shift(1) >= self.df['sma_lento'].shift(1)) &
                (self.df['sma_rapido'] < self.df['sma_lento'])
        )

        # Verificar últimos cruces
        ultimo_cruce_alcista = (
                self.df['cruce_rapido_medio'].iloc[-1] or
                self.df['cruce_medio_lento'].iloc[-1] or
                self.df['cruce_rapido_lento'].iloc[-1]
        )

        ultimo_cruce_bajista = (
                self.df['cruce_rapido_medio_bajista'].iloc[-1] or
                self.df['cruce_medio_lento_bajista'].iloc[-1] or
                self.df['cruce_rapido_lento_bajista'].iloc[-1]
        )

        # Verificar últimos cruces
        ultimo_cruce_alcista = (
                self.df['cruce_rapido_medio'].iloc[-1] or
                self.df['cruce_medio_lento'].iloc[-1]
        )

        ultimo_cruce_bajista = (
                self.df['cruce_rapido_medio_bajista'].iloc[-1] or
                self.df['cruce_medio_lento_bajista'].iloc[-1]
        )

        # Detectar si, durante una alineación alcista, rápido está por debajo de medio
        self.df['caida_rapido_respecto_medio'] = (
                (self.df['sma_rapido'] < self.df['sma_medio']) &  # Rápido cae debajo de medio
                (self.df['sma_rapido'].shift(1) > self.df['sma_medio'].shift(1)) &  # Antes estaba por encima
                (self.df['sma_medio'] > self.df['sma_lento'])  # Se mantiene la condición de alcista previa
        )

        # Detectar último caso de esta condición
        ultimo_caida_rapido_respecto_medio = self.df['caida_rapido_respecto_medio'].iloc[-1]

        # Log extra: Si durante una alineación alcista ocurre esta condición
        if ultimo_caida_rapido_respecto_medio:
            logging.info(
                "Triple SMA - Durante la alineación alcista, la media rápida cayó por debajo de la media intermedia.")

        # Detectar si, durante una alineación bajista, la media rápida está por encima de la media intermedia
        self.df['subida_rapido_respecto_medio'] = (
                (self.df['sma_rapido'] > self.df['sma_medio']) &  # Rápido sube por encima de medio
                (self.df['sma_rapido'].shift(1) < self.df['sma_medio'].shift(1)) &  # Antes estaba por debajo
                (self.df['sma_medio'] < self.df['sma_lento'])
        # Se mantiene la condición de alineación bajista previa
        )

        # Detectar último caso de esta condición
        ultima_subida_rapido_respecto_medio = self.df['subida_rapido_respecto_medio'].iloc[-1]

        # Log extra: Si durante una alineación bajista ocurre esta condición
        if ultima_subida_rapido_respecto_medio:
            logging.info(
                "Triple SMA - Durante la alineación bajista, la media rápida subió por encima de la media intermedia.")

        if mode == 0:
            if alineacion_alcista:
                return 2
            elif alineacion_bajista:
                return 1
            else:
                return -1

        if mode == 1:
            if alineacion_bajista:
                if ultima_subida_rapido_respecto_medio:
                    return 1
            elif alineacion_alcista:
                if ultimo_caida_rapido_respecto_medio:
                    return 2
            else:
                return -1


        return 0

