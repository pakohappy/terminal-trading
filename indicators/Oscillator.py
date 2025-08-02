# -*- coding: utf-8 -*-
"""
Módulo de indicadores técnicos de tipo oscilador.

Este módulo implementa indicadores técnicos de tipo oscilador, que fluctúan entre
valores extremos para identificar condiciones de sobrecompra o sobreventa en el mercado.
Actualmente incluye el Oscilador Estocástico, que mide la posición del precio actual
en relación con su rango de precios durante un período determinado.

Los osciladores son especialmente útiles en mercados sin tendencia clara (laterales),
donde pueden ayudar a identificar puntos de reversión potenciales. También pueden
utilizarse para detectar divergencias entre el precio y el indicador, lo que
puede señalar posibles cambios en la tendencia actual.

Características principales de los osciladores:
- Fluctúan entre valores extremos (normalmente 0-100 o -100 a +100)
- Identifican condiciones de sobrecompra (posible venta) y sobreventa (posible compra)
- Funcionan mejor en mercados laterales o rangos de trading
- Pueden generar señales falsas en mercados con tendencia fuerte
"""
import logging
import pandas as pd


class Oscillator:
    """
    Clase que implementa indicadores técnicos de tipo oscilador.
    
    Esta clase proporciona métodos para calcular osciladores como el Estocástico,
    que ayudan a identificar condiciones de sobrecompra o sobreventa y posibles
    puntos de reversión en el mercado. Los osciladores son herramientas valiosas
    para determinar cuándo un activo puede estar sobrevaluado o infravaluado
    temporalmente.
    
    Los osciladores pueden utilizarse de varias formas:
    - Identificar niveles extremos (sobrecompra/sobreventa)
    - Detectar cruces de líneas (como %K y %D en el Estocástico)
    - Encontrar divergencias entre el precio y el oscilador
    - Confirmar la fuerza de una tendencia
    
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
        
        Desarrollado por George Lane en los años 50, el Estocástico se basa en la observación
        de que durante tendencias alcistas, los precios tienden a cerrar cerca de sus máximos,
        y durante tendencias bajistas, tienden a cerrar cerca de sus mínimos.
        
        El indicador consta de dos líneas:
        - %K: La línea principal que mide la posición relativa del precio dentro del rango
              alto-bajo del período. Se calcula como:
              %K = 100 * ((Cierre - Mínimo(n)) / (Máximo(n) - Mínimo(n)))
              donde n es el número de períodos.
        - %D: Una media móvil de %K que actúa como línea de señal y ayuda a identificar
              cambios en la dirección del %K.
        
        Interpretación:
        - Valores por encima de 80 indican sobrecompra (posible señal de venta)
        - Valores por debajo de 20 indican sobreventa (posible señal de compra)
        - Cruces de %K por encima de %D generan señales alcistas
        - Cruces de %K por debajo de %D generan señales bajistas
        - Las divergencias entre el precio y el Estocástico pueden indicar posibles reversiones
        
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
                 0: Sin señal clara
        
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
        # Obtener los últimos valores para generar señales
        ultimo_cruce_a_la_baja_sobrecompra = self.df['cruce_a_la_baja_en_sobrecompra'].iloc[-1]
        ultimo_cruce_al_alza_sobreventa = self.df['cruce_al_alza_en_sobreventa'].iloc[-1]
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
                return 0

        # Detectamos zona de sobrecompra/sobreventa.
        if mode == 1:
            if ultima_sobreventa:
                return 2
            elif ultima_sobrecompra:
                return 1
            else:
                return 0

        return 0  # Sin señal clara