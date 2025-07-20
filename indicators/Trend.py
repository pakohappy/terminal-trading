# -*- coding: utf-8 -*-
"""
Módulo de indicadores técnicos de tendencia.

Este módulo implementa indicadores técnicos que ayudan a identificar la dirección
y fuerza de la tendencia en el mercado. Incluye indicadores como:
- MACD (Moving Average Convergence Divergence)
- SMA (Simple Moving Average)
- Triple SMA (Triple Simple Moving Average)

Los indicadores de tendencia son especialmente útiles en mercados direccionales,
donde pueden ayudar a identificar y seguir la tendencia predominante.
"""
import logging
import pandas as pd


class Trend:
    """
    Clase que implementa indicadores técnicos de tendencia.
    
    Esta clase proporciona métodos para calcular indicadores como MACD, SMA y Triple SMA,
    que ayudan a identificar la dirección y fuerza de la tendencia en el mercado.
    
    Attributes:
        df (pd.DataFrame): DataFrame con los datos de precios. Debe contener al menos
                          una columna 'close' con los precios de cierre.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def macd(self,
             periodo_rapido: int = 12,
             periodo_lento: int = 26,
             periodo_senyal: int = 9) -> int:
        """
        Calcula el indicador MACD (Moving Average Convergence Divergence) y genera señales de trading.
        
        El MACD es un indicador de tendencia que muestra la relación entre dos medias móviles
        exponenciales (EMA) del precio. Se calcula restando la EMA de período más largo de la
        EMA de período más corto. La línea de señal es una EMA del MACD.
        
        Args:
            periodo_rapido: Período para la EMA rápida. Por defecto 12.
            periodo_lento: Período para la EMA lenta. Por defecto 26.
            periodo_senyal: Período para la línea de señal (EMA del MACD). Por defecto 9.
            
        Returns:
            int: Señal de trading:
                 0: Señal de compra (cruce alcista: MACD cruza por encima de la línea de señal)
                 1: Señal de venta (cruce bajista: MACD cruza por debajo de la línea de señal)
                -1: Sin señal clara
                
        Raises:
            ValueError: Si el DataFrame no contiene la columna 'close'.
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

    def sma(self, periodo: int = 20) -> int:
        """
        Calcula la tendencia utilizando la SMA (Simple Moving Average) y genera señales de trading.
        
        La SMA es un indicador de tendencia que calcula el precio promedio durante un período
        específico. Se utiliza para suavizar las fluctuaciones de precios y ayudar a identificar
        la dirección de la tendencia.
        
        Args:
            periodo: Número de períodos para calcular la media móvil simple. Por defecto 20.
            
        Returns:
            int: Señal de trading:
                 0: Señal de compra (tendencia alcista: precio por encima de la SMA)
                 1: Señal de venta (tendencia bajista: precio por debajo de la SMA)
                
        Raises:
            ValueError: Si el DataFrame no contiene la columna 'close'.
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
                   periodo_lento: int = 8,
                   periodo_medio: int = 6,
                   periodo_rapido: int = 4,
                   mode: int = 0) -> int:
        """
        Calcula la tendencia utilizando la Triple SMA (Triple Simple Moving Average) y genera señales de trading.
        
        La Triple SMA utiliza tres medias móviles simples con diferentes períodos para identificar
        tendencias en el mercado. La estrategia busca oportunidades de compra cuando las medias móviles
        están alineadas en orden ascendente (rápida > media > lenta) y oportunidades de venta cuando
        están alineadas en orden descendente (rápida < media < lenta).
        
        Args:
            periodo_lento: Número de períodos para la media móvil lenta. Por defecto 8.
            periodo_medio: Número de períodos para la media móvil media. Por defecto 6.
            periodo_rapido: Número de períodos para la media móvil rápida. Por defecto 4.
            mode: Modo de operación que determina cómo se generan las señales:
                 0: Basado en alineación de las medias móviles (tendencia alcista/bajista)
                 1: Basado en cambios de dirección que indican fin de tendencia
                 Por defecto 0.
                 
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra (alineación alcista o cambio a tendencia alcista)
                 1: Señal de venta (alineación bajista o cambio a tendencia bajista)
                -1: Sin señal clara
                 
        Raises:
            ValueError: Si el DataFrame no contiene la columna 'close'.
        """
        # Validar que el DataFrame tenga la columna 'close'.
        if 'close' not in self.df.columns:
            logging.error("TRIPLE SMA - El DataFrame no contiene la columna 'close'.")
            raise ValueError("El DataFrame debe contener una columna 'close' para calcular la SMA.")

        # Calcular las SMA_lento, SMA_medio y SMA_rapido.
        self.df['sma_lento'] = self.df['close'].rolling(window=periodo_lento).mean()
        self.df['sma_medio'] = self.df['close'].rolling(window=periodo_medio).mean()
        self.df['sma_rapido'] = self.df['close'].rolling(window=periodo_rapido).mean()

        # Eliminar filas con NaN
        self.df = self.df.dropna().copy()

        # Detectar cruces y alineación de las medias
        ultima_fila = self.df.iloc[-1]

        # Verificar alineación alcista (rápida > media > lenta)
        alineacion_alcista = (ultima_fila['sma_rapido'] > ultima_fila['sma_medio'] > ultima_fila['sma_lento'])

        # Verificar alineación bajista (rápida < media < lenta)
        alineacion_bajista = (ultima_fila['sma_rapido'] < ultima_fila['sma_medio'] < ultima_fila['sma_lento'])

        # Nota: El código comentado a continuación es una implementación alternativa
        # que detecta cruces entre las diferentes medias móviles. Se mantiene como referencia
        # para posibles mejoras futuras del indicador.
        #
        # # Detectar cruces alcistas entre todas las líneas
        # # self.df['cruce_rapido_medio'] = (
        # #         (self.df['sma_rapido'].shift(1) <= self.df['sma_medio'].shift(1)) &
        # #         (self.df['sma_rapido'] > self.df['sma_medio'])
        # # )
        # #
        # # self.df['cruce_medio_lento'] = (
        # #         (self.df['sma_medio'].shift(1) <= self.df['sma_lento'].shift(1)) &
        # #         (self.df['sma_medio'] > self.df['sma_lento'])
        # # )
        # #
        # # self.df['cruce_rapido_lento'] = (
        # #         (self.df['sma_rapido'].shift(1) <= self.df['sma_lento'].shift(1)) &
        # #         (self.df['sma_rapido'] > self.df['sma_lento'])
        # # )
        # #
        # # # Detectar cruces bajistas entre todas las líneas
        # # self.df['cruce_rapido_medio_bajista'] = (
        # #         (self.df['sma_rapido'].shift(1) >= self.df['sma_medio'].shift(1)) &
        # #         (self.df['sma_rapido'] < self.df['sma_medio'])
        # # )
        # #
        # # self.df['cruce_medio_lento_bajista'] = (
        # #         (self.df['sma_medio'].shift(1) >= self.df['sma_lento'].shift(1)) &
        # #         (self.df['sma_medio'] < self.df['sma_lento'])
        # # )
        # #
        # # self.df['cruce_rapido_lento_bajista'] = (
        # #         (self.df['sma_rapido'].shift(1) >= self.df['sma_lento'].shift(1)) &
        # #         (self.df['sma_rapido'] < self.df['sma_lento'])
        # # )
        # #
        # # # Verificar últimos cruces
        # # ultimo_cruce_alcista = (
        # #         self.df['cruce_rapido_medio'].iloc[-1] or
        # #         self.df['cruce_medio_lento'].iloc[-1] or
        # #         self.df['cruce_rapido_lento'].iloc[-1]
        # # )
        # #
        # # ultimo_cruce_bajista = (
        # #         self.df['cruce_rapido_medio_bajista'].iloc[-1] or
        # #         self.df['cruce_medio_lento_bajista'].iloc[-1] or
        # #         self.df['cruce_rapido_lento_bajista'].iloc[-1]
        # # )

        # Detectar si, durante una alineación alcista, la media rápida cae por debajo de la media
        # Esto indica un posible fin de la tendencia alcista o una corrección temporal
        self.df['caida_rapido_respecto_medio'] = (
                (self.df['sma_rapido'] < self.df['sma_medio']) &  # Rápido cae debajo de medio
                (self.df['sma_rapido'].shift(1) > self.df['sma_medio'].shift(1)) &  # Antes estaba por encima
                (self.df['sma_medio'] > self.df['sma_lento'])  # Se mantiene la condición de alcista previa
        )

        # Detectar último caso de esta condición
        ultimo_caida_rapido_respecto_medio = self.df['caida_rapido_respecto_medio'].iloc[-1]

        # Registrar evento en el log si se detecta esta condición
        if ultimo_caida_rapido_respecto_medio:
            logging.debug(
                "Triple SMA - Durante la alineación alcista, la media rápida cayó por debajo de la media intermedia.")

        # Detectar si, durante una alineación bajista, la media rápida sube por encima de la media
        # Esto indica un posible fin de la tendencia bajista o un rebote temporal
        self.df['subida_rapido_respecto_medio'] = (
                (self.df['sma_rapido'] > self.df['sma_medio']) &  # Rápido sube por encima de medio
                (self.df['sma_rapido'].shift(1) < self.df['sma_medio'].shift(1)) &  # Antes estaba por debajo
                (self.df['sma_medio'] < self.df['sma_lento'])  # Se mantiene la condición de bajista previa
        )

        # Detectar último caso de esta condición
        ultima_subida_rapido_respecto_medio = self.df['subida_rapido_respecto_medio'].iloc[-1]

        # Registrar evento en el log si se detecta esta condición
        if ultima_subida_rapido_respecto_medio:
            logging.debug(
                "Triple SMA - Durante la alineación bajista, la media rápida subió por encima de la media intermedia.")

        if mode == 0:
            if alineacion_alcista:
                return 2
            elif alineacion_bajista:
                return 1
            else:
                return -1

        if mode == 1:
            if ultimo_caida_rapido_respecto_medio or alineacion_bajista:
                return 1
            if ultima_subida_rapido_respecto_medio or alineacion_alcista:
                return 2
            else:
                return -1

        return 0

