# -*- coding: utf-8 -*-
"""
Módulo de indicadores técnicos de tipo oscilador.

Este módulo implementa indicadores técnicos de tipo oscilador, que fluctúan entre
valores extremos para identificar condiciones de sobrecompra o sobreventa en el mercado.
Actualmente incluye el Oscilador Estocástico, que mide la posición del precio actual
en relación con su rango de precios durante un período determinado.

Los osciladores son especialmente útiles en mercados sin tendencia clara (laterales),
donde pueden ayudar a identificar puntos de reversión potenciales.
"""
import logging
import pandas as pd


class Oscillator:
    """
    Clase que implementa indicadores técnicos de tipo oscilador.
    
    Esta clase proporciona métodos para calcular osciladores como el Estocástico,
    que ayudan a identificar condiciones de sobrecompra o sobreventa y posibles
    puntos de reversión en el mercado.
    
    Attributes:
        df (pd.DataFrame): DataFrame con los datos de precios. Debe contener al menos
                          columnas 'high', 'low' y 'close' con los precios correspondientes.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def stochastic(self,
                   k_period: int = 5,
                   d_period: int = 3,
                   smooth_k: int = 3,
                   overbought_level: int = 80,
                   oversold_level: int = 20,
                   mode: int = 0) -> int:
        """
        Calcula el Oscilador Estocástico y genera señales de trading.
        
        El Estocástico es un oscilador que mide la posición del precio actual en relación
        con su rango de precios durante un período determinado. Ayuda a identificar condiciones
        de sobrecompra o sobreventa, así como posibles divergencias y cruces de líneas.
        
        El indicador consta de dos líneas:
        - %K: La línea principal que mide la posición relativa del precio
        - %D: Una media móvil de %K que actúa como línea de señal
        
        Args:
            k_period: Número de periodos para calcular %K inicial. Por defecto 5.
            d_period: Número de periodos para calcular %D (media móvil de %K). Por defecto 3.
            smooth_k: Período de suavizado adicional aplicado a la línea %K. Por defecto 3.
            overbought_level: Nivel de sobrecompra personalizado. Por defecto 80.
            oversold_level: Nivel de sobreventa personalizado. Por defecto 20.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Señales basadas en cruces de %K y %D en zonas de sobrecompra/sobreventa
                  1: Señales basadas únicamente en zonas de sobrecompra/sobreventa
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra (cruce al alza en sobreventa o precio en sobreventa)
                 1: Señal de venta (cruce a la baja en sobrecompra o precio en sobrecompra)
                -1: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene las columnas necesarias o si los parámetros son inválidos.
        """
        # Validaciones generales.
        if not {'high', 'low', 'close'}.issubset(self.df.columns):
            logging.error("STOCHASTIC - El DataFrame debe contener las columnas 'High', 'Low' y 'Close'.")
            raise ValueError("STOCHASTIC - El DataFrame debe contener las columnas 'High', 'Low' y 'Close'.")
        if len(self.df) < k_period:
            logging.error("STOCHASTIC - El número de filas no es suficiente para calcular el Indicador Estocástico.")
            raise ValueError("STOCHASTIC - El número de filas no es suficiente para calcular el Indicador Estocástico.")
        if k_period <= 0 or d_period <= 0 or smooth_k <= 0:
            logging.error("STOCHASTIC - Los períodos deben ser mayores que 0.")
            raise ValueError("STOCHASTIC - Los períodos deben ser mayores que 0.")

        # Calcular valores mínimos y máximos (rango para %K).
        self.df['low_min'] = self.df['low'].rolling(window=k_period).min()
        self.df['high_max'] = self.df['high'].rolling(window=k_period).max()

        # Calcular %K inicial.
        self.df['%K'] = ((self.df['close'] - self.df['low_min']) /
                         (self.df['high_max'] - self.df['low_min'])) * 100

        # Suavizar %K.
        self.df['%K_suavizado'] = self.df['%K'].rolling(window=smooth_k).mean()

        # Calcular %D (media móvil de %K_suavizado).
        self.df['%D'] = self.df['%K_suavizado'].rolling(window=d_period).mean()

        # Eliminar valores NaN.
        self.df.dropna(subset=['%K_suavizado', '%D'], inplace=True)

        # Detectar sobrecompra/sobreventa.
        self.df['sobrecompra'] = self.df['%K_suavizado'] > overbought_level
        self.df['sobreventa'] = self.df['%K_suavizado'] < oversold_level

        # Detectar cruces de %K_suavizado y %D.
        self.df['cruce_al_alza'] = (self.df['%K_suavizado'].shift(1) < self.df['%D'].shift(1)) & \
                                   (self.df['%K_suavizado'] > self.df['%D'])
        self.df['cruce_a_la_baja'] = (self.df['%K_suavizado'].shift(1) > self.df['%D'].shift(1)) & \
                                     (self.df['%K_suavizado'] < self.df['%D'])

        # Detectar cruces en sobrecompra/sobreventa.
        self.df['cruce_al_alza_en_sobrecompra'] = self.df['sobrecompra'] & self.df['cruce_al_alza']
        self.df['cruce_a_la_baja_en_sobrecompra'] = self.df['sobrecompra'] & self.df['cruce_a_la_baja']
        self.df['cruce_al_alza_en_sobreventa'] = self.df['sobreventa'] & self.df['cruce_al_alza']
        self.df['cruce_a_la_baja_en_sobreventa'] = self.df['sobreventa'] & self.df['cruce_a_la_baja']

        # Detectar divergencias.
        self.df['divergencia_alcista'] = (
            (self.df['close'] < self.df['close'].shift(1)) &  # Mínimo más bajo en precio
            (self.df['%K_suavizado'] > self.df['%K_suavizado'].shift(1))  # Mínimo más alto en %K
        )
        self.df['divergencia_bajista'] = (
            (self.df['close'] > self.df['close'].shift(1)) &  # Máximo más alto en precio
            (self.df['%K_suavizado'] < self.df['%K_suavizado'].shift(1))  # Máximo más bajo en %K
        )

        # Señales basadas en cruces y divergencias.
        # ultimo_cruce_al_alza_sobrecompra = self.df['cruce_al_alza_en_sobrecompra'].iloc[-1]
        ultimo_cruce_a_la_baja_sobrecompra = self.df['cruce_a_la_baja_en_sobrecompra'].iloc[-1]
        ultimo_cruce_al_alza_sobreventa = self.df['cruce_al_alza_en_sobreventa'].iloc[-1]
        # ultimo_cruce_a_la_baja_sobreventa = self.df['cruce_a_la_baja_en_sobreventa'].iloc[-1]
        # ultima_divergencia_alcista = self.df['divergencia_alcista'].iloc[-1]
        # ultima_divergencia_bajista = self.df['divergencia_bajista'].iloc[-1]
        ultima_sobrecompra = self.df['sobrecompra'].iloc[-1]
        ultima_sobreventa = self.df['sobreventa'].iloc[-1]

        # Comentado para distribución abierta: código de depuración
        # columnas_print = ['time',
        #                   'cruce_a_la_baja_en_sobrecompra',
        #                   'cruce_al_alza_en_sobreventa',
        #                   'sobrecompra',
        #                   'sobreventa']
        # print(self.df[columnas_print])

        # Detectamos cruces en zonas de sobrecompra/sobreventa.
        if mode == 0:
            if ultimo_cruce_al_alza_sobreventa:
                return 2
            elif ultimo_cruce_a_la_baja_sobrecompra:
                return 1
            else:
                return -1

        # Detectamos zona de sobrecompra/sobreventa.
        if mode == 1:
            if ultima_sobreventa:
                return 2
            elif ultima_sobrecompra:
                return 1
            else:
                return -1

        return 0