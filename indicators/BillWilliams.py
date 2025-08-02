# -*- coding: utf-8 -*-
"""
Módulo de indicadores técnicos desarrollados por Bill Williams.

Este módulo implementa los indicadores técnicos desarrollados por Bill Williams,
un reconocido trader y autor de varios libros sobre trading. Actualmente incluye
el indicador Alligator, que utiliza tres medias móviles suavizadas y desplazadas
para identificar tendencias y momentos de "despertar" del mercado.

El Alligator es una herramienta poderosa para identificar tendencias y evitar
operar en mercados laterales. Cuando las tres líneas se entrelazan (el "Alligator
duerme"), es mejor evitar operar. Cuando las líneas se separan (el "Alligator
despierta y comienza a cazar"), es momento de considerar entrar al mercado.

Referencias:
    - Bill Williams, "Trading Chaos: Maximize Profits with Proven Technical Techniques"
    - Bill Williams, "New Trading Dimensions: How to Profit from Chaos in Stocks, Bonds, and Commodities"
"""
import logging
import pandas as pd


class BillWilliams:
    """
    Clase que implementa los indicadores técnicos desarrollados por Bill Williams.
    
    Esta clase proporciona métodos para calcular indicadores como el Alligator,
    que ayudan a identificar tendencias y puntos de entrada/salida en el mercado.
    Los indicadores de Bill Williams se basan en la teoría del caos y buscan
    identificar la estructura fractal de los mercados.
    
    El Alligator utiliza tres medias móviles desplazadas para representar:
    - Mandíbula (Jaw): Media móvil más lenta, representada en azul
    - Dientes (Teeth): Media móvil intermedia, representada en rojo
    - Labios (Lips): Media móvil más rápida, representada en verde
    
    Attributes:
        df (pd.DataFrame): DataFrame con los datos de precios. Debe contener al menos
                          una columna 'close' con los precios de cierre.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def alligator(self,
                  jaw_period: int=13,       # Periodo para 'jaw'.
                  jaw_offset: int=8,        # Desplazamiento para 'jaw'.
                  teeth_period: int=8,      # Periodo para 'teeth'.
                  teeth_offset: int=5,      # Desplazamiento para 'teeth'.
                  lips_period: int=5,       # Periodo para 'lips'.
                  lips_offset: int=3,       # Desplazamiento para 'lips'.
                  drop_nan: bool=True,      # True para eliminar NaN resultantes.
                  percentage: int=100,      # Umbral para comparación de porcentaje.
                  mode: int=0) -> int:      # Modo de operación.
        """
        Calcula el indicador Alligator de Bill Williams y genera señales de trading.
        
        El Alligator utiliza tres medias móviles suavizadas y desplazadas para identificar
        tendencias en el mercado. Según Bill Williams, estas líneas representan la mandíbula,
        los dientes y los labios de un "cocodrilo" que "duerme" durante períodos laterales
        y "despierta hambriento" cuando comienza una tendencia.
        
        Componentes del Alligator:
        - Jaw (Mandíbula): Media móvil de período más largo, representada en azul.
          Es la línea más lenta y actúa como soporte/resistencia en tendencias.
        - Teeth (Dientes): Media móvil de período intermedio, representada en rojo.
          Confirma la dirección de la tendencia.
        - Lips (Labios): Media móvil de período más corto, representada en verde.
          Es la línea más sensible a los cambios de precio recientes.
        
        Interpretación:
        - Cuando las tres líneas se entrelazan: El Alligator "duerme" (mercado lateral).
          Se recomienda no operar o hacerlo con precaución.
        - Cuando las líneas se separan: El Alligator "despierta" (comienza una tendencia).
          Es momento de considerar entrar al mercado.
        
        Condiciones de tendencia:
        - Alcista: lips(verde) > teeth(rojo) > jaw(azul)
        - Bajista: lips(verde) < teeth(rojo) < jaw(azul)
        
        Args:
            jaw_period: Número de períodos para calcular Jaw (Mandíbula). Por defecto 13.
            jaw_offset: Cantidad de períodos de desplazamiento para Jaw. Por defecto 8.
            teeth_period: Número de períodos para calcular Teeth (Dientes). Por defecto 8.
            teeth_offset: Cantidad de períodos de desplazamiento para Teeth. Por defecto 5.
            lips_period: Número de períodos para calcular Lips (Labios). Por defecto 5.
            lips_offset: Cantidad de períodos de desplazamiento para Lips. Por defecto 3.
            drop_nan: Si es True, elimina las filas con valores NaN resultantes del cálculo. Por defecto True.
            percentage: Umbral de porcentaje para comparación en el modo 3. Por defecto 100.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Basado en alineación de las líneas (tendencia alcista/bajista)
                  1: Basado en si la línea de los labios se aproxima a la línea de los dientes
                  2: Basado en si tanto la mandíbula como los labios se aproximan a los dientes
                  3: Basado en cambio porcentual entre dientes y labios
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra (tendencia alcista)
                 1: Señal de venta (tendencia bajista) o señal específica según el modo
                 0: Sin señal clara (cuando no hay alineación alcista ni bajista)
        
        Raises:
            ValueError: Si el DataFrame no contiene la columna 'close'.
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
                return 0

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