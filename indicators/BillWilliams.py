# -*- coding: utf-8 -*-
"""
Módulo de indicadores técnicos desarrollados por Bill Williams.

Este módulo implementa los indicadores técnicos desarrollados por Bill Williams,
un reconocido trader y autor de varios libros sobre trading. Incluye varios indicadores:

1. Alligator: Utiliza tres medias móviles suavizadas y desplazadas para identificar
   tendencias y momentos de "despertar" del mercado.
2. Awesome Oscillator (AO): Mide la diferencia entre una media móvil de 5 períodos
   y una media móvil de 34 períodos, ambas calculadas sobre el punto medio de cada barra.
3. Fractals: Identifica patrones de cinco barras donde la barra central es un máximo o mínimo local.
4. Acceleration/Deceleration Oscillator (AC): Mide la aceleración o desaceleración del momentum.
5. Market Facilitation Index (MFI): Mide la eficiencia del mercado al relacionar el rango
   de precios con el volumen.

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
import numpy as np


class BillWilliams:
    """
    Clase que implementa los indicadores técnicos desarrollados por Bill Williams.
    
    Esta clase proporciona métodos para calcular indicadores como el Alligator,
    Awesome Oscillator, Fractals, Acceleration/Deceleration Oscillator y Market
    Facilitation Index, que ayudan a identificar tendencias y puntos de entrada/salida
    en el mercado. Los indicadores de Bill Williams se basan en la teoría del caos
    y buscan identificar la estructura fractal de los mercados.
    
    Indicadores implementados:
    - Alligator: Utiliza tres medias móviles desplazadas para representar:
      * Mandíbula (Jaw): Media móvil más lenta, representada en azul
      * Dientes (Teeth): Media móvil intermedia, representada en rojo
      * Labios (Lips): Media móvil más rápida, representada en verde
    
    - Awesome Oscillator (AO): Mide la diferencia entre una media móvil de 5 períodos
      y una media móvil de 34 períodos, ambas calculadas sobre el punto medio de cada barra.
    
    - Fractals: Identifica patrones de cinco barras donde la barra central es un máximo
      o mínimo local.
    
    - Acceleration/Deceleration Oscillator (AC): Mide la aceleración o desaceleración
      del momentum del mercado.
    
    - Market Facilitation Index (MFI): Mide la eficiencia del mercado al relacionar
      el rango de precios con el volumen.
    
    Attributes:
        df (pd.DataFrame): DataFrame con los datos de precios. Debe contener al menos
                          columnas 'high', 'low', 'close' y 'volume' para todos los indicadores.
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
        
    def awesome_oscillator(self, 
                          fast_period: int = 5, 
                          slow_period: int = 34, 
                          mode: int = 0) -> int:
        """
        Calcula el indicador Awesome Oscillator (AO) de Bill Williams y genera señales de trading.
        
        El Awesome Oscillator es un indicador de momentum que mide la diferencia entre una media
        móvil rápida y una media móvil lenta del punto medio de cada barra (high+low)/2.
        Muestra la fuerza del mercado y los posibles cambios de tendencia.
        
        Interpretación:
        - Cruce de cero: Cuando el AO cruza por encima de cero, indica una posible tendencia alcista.
          Cuando cruza por debajo de cero, indica una posible tendencia bajista.
        - Divergencia: Cuando el precio forma nuevos máximos/mínimos pero el AO no los confirma,
          puede indicar un posible cambio de tendencia.
        - Formación de dos picos: Dos picos consecutivos por encima o por debajo de la línea cero
          pueden indicar oportunidades de entrada.
        
        Args:
            fast_period: Número de períodos para la media móvil rápida. Por defecto 5.
            slow_period: Número de períodos para la media móvil lenta. Por defecto 34.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Basado en el valor actual del AO (positivo/negativo)
                  1: Basado en el cruce de cero
                  2: Basado en la formación de dos picos
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene las columnas 'high' y 'low'.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if 'high' not in self.df.columns or 'low' not in self.df.columns:
            logging.error("AWESOME OSCILLATOR - El DataFrame no contiene las columnas 'high' y/o 'low'.")
            raise ValueError("El DataFrame debe contener columnas 'high' y 'low' para calcular el Awesome Oscillator.")
        
        # Calcular el punto medio de cada barra
        self.df['median_price'] = (self.df['high'] + self.df['low']) / 2
        
        # Calcular las medias móviles simples
        self.df['ao_fast_sma'] = self.df['median_price'].rolling(window=fast_period).mean()
        self.df['ao_slow_sma'] = self.df['median_price'].rolling(window=slow_period).mean()
        
        # Calcular el Awesome Oscillator
        self.df['ao'] = self.df['ao_fast_sma'] - self.df['ao_slow_sma']
        
        # Calcular cambios en el AO para detectar cruces y formaciones
        self.df['ao_prev'] = self.df['ao'].shift(1)
        self.df['ao_change'] = self.df['ao'] - self.df['ao_prev']
        
        # Detectar cruces de cero
        self.df['ao_zero_cross_up'] = (self.df['ao'] > 0) & (self.df['ao_prev'] <= 0)
        self.df['ao_zero_cross_down'] = (self.df['ao'] < 0) & (self.df['ao_prev'] >= 0)
        
        # Detectar formación de dos picos (saucer pattern)
        # Para picos alcistas: tres barras consecutivas por encima de cero, con la del medio más baja
        self.df['ao_saucer_up'] = (self.df['ao'] > 0) & (self.df['ao_prev'] > 0) & (self.df['ao'].shift(2) > 0) & \
                                 (self.df['ao_prev'] < self.df['ao']) & (self.df['ao_prev'] < self.df['ao'].shift(2))
        
        # Para picos bajistas: tres barras consecutivas por debajo de cero, con la del medio más alta
        self.df['ao_saucer_down'] = (self.df['ao'] < 0) & (self.df['ao_prev'] < 0) & (self.df['ao'].shift(2) < 0) & \
                                   (self.df['ao_prev'] > self.df['ao']) & (self.df['ao_prev'] > self.df['ao'].shift(2))
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en el valor actual del AO
            if self.df['ao'].iloc[-1] > 0:
                return 2  # Señal de compra
            elif self.df['ao'].iloc[-1] < 0:
                return 1  # Señal de venta
            else:
                return 0  # Sin señal clara
        
        elif mode == 1:
            # Basado en el cruce de cero
            if self.df['ao_zero_cross_up'].iloc[-1]:
                return 2  # Señal de compra
            elif self.df['ao_zero_cross_down'].iloc[-1]:
                return 1  # Señal de venta
            else:
                return 0  # Sin señal clara
        
        elif mode == 2:
            # Basado en la formación de dos picos
            if self.df['ao_saucer_up'].iloc[-1]:
                return 2  # Señal de compra
            elif self.df['ao_saucer_down'].iloc[-1]:
                return 1  # Señal de venta
            else:
                return 0  # Sin señal clara
        
        return 0
        
    def fractals(self, mode: int = 0) -> int:
        """
        Calcula el indicador Fractals de Bill Williams y genera señales de trading.
        
        Los Fractals son indicadores que identifican patrones de cinco barras donde la barra
        central es un máximo o mínimo local. Un fractal alcista se forma cuando hay una barra
        con un máximo más alto que las dos barras anteriores y las dos posteriores. Un fractal
        bajista se forma cuando hay una barra con un mínimo más bajo que las dos barras
        anteriores y las dos posteriores.
        
        Los Fractals se utilizan para identificar posibles niveles de soporte y resistencia,
        así como para confirmar tendencias cuando se usan junto con otros indicadores como
        el Alligator.
        
        Interpretación:
        - Fractal alcista: Posible nivel de resistencia.
        - Fractal bajista: Posible nivel de soporte.
        - Fractals por encima/debajo del Alligator: Pueden indicar oportunidades de entrada.
        
        Args:
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Basado en el último fractal formado
                  1: Basado en fractals que rompen niveles previos
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra (fractal alcista)
                 1: Señal de venta (fractal bajista)
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene las columnas 'high' y 'low'.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if 'high' not in self.df.columns or 'low' not in self.df.columns:
            logging.error("FRACTALS - El DataFrame no contiene las columnas 'high' y/o 'low'.")
            raise ValueError("El DataFrame debe contener columnas 'high' y 'low' para calcular Fractals.")
        
        # Necesitamos al menos 5 barras para calcular fractals
        if len(self.df) < 5:
            logging.warning("FRACTALS - Se necesitan al menos 5 barras para calcular Fractals.")
            return 0
        
        # Identificar fractals alcistas
        # Un fractal alcista se forma cuando el máximo de la barra central es mayor que
        # los máximos de las dos barras anteriores y las dos posteriores
        self.df['fractal_up'] = False
        for i in range(2, len(self.df) - 2):
            if (self.df['high'].iloc[i] > self.df['high'].iloc[i-2]) and \
               (self.df['high'].iloc[i] > self.df['high'].iloc[i-1]) and \
               (self.df['high'].iloc[i] > self.df['high'].iloc[i+1]) and \
               (self.df['high'].iloc[i] > self.df['high'].iloc[i+2]):
                self.df.loc[self.df.index[i], 'fractal_up'] = True
        
        # Identificar fractals bajistas
        # Un fractal bajista se forma cuando el mínimo de la barra central es menor que
        # los mínimos de las dos barras anteriores y las dos posteriores
        self.df['fractal_down'] = False
        for i in range(2, len(self.df) - 2):
            if (self.df['low'].iloc[i] < self.df['low'].iloc[i-2]) and \
               (self.df['low'].iloc[i] < self.df['low'].iloc[i-1]) and \
               (self.df['low'].iloc[i] < self.df['low'].iloc[i+1]) and \
               (self.df['low'].iloc[i] < self.df['low'].iloc[i+2]):
                self.df.loc[self.df.index[i], 'fractal_down'] = True
        
        # Almacenar los valores de los fractals
        self.df['fractal_up_value'] = np.where(self.df['fractal_up'], self.df['high'], np.nan)
        self.df['fractal_down_value'] = np.where(self.df['fractal_down'], self.df['low'], np.nan)
        
        # No podemos identificar fractals en las últimas 2 barras (necesitamos 2 barras futuras)
        # Por lo tanto, verificamos si hay fractals en la tercera barra desde el final
        if len(self.df) >= 5:
            last_fractal_index = -3
            
            if mode == 0:
                # Basado en el último fractal formado
                if self.df['fractal_up'].iloc[last_fractal_index]:
                    return 2  # Señal de compra (fractal alcista)
                elif self.df['fractal_down'].iloc[last_fractal_index]:
                    return 1  # Señal de venta (fractal bajista)
            
            elif mode == 1:
                # Basado en fractals que rompen niveles previos
                # Encontrar el último fractal alcista y bajista
                last_up_indices = self.df.index[self.df['fractal_up']].tolist()
                last_down_indices = self.df.index[self.df['fractal_down']].tolist()
                
                if last_up_indices and last_down_indices:
                    # Verificar si el precio actual ha roto el último fractal
                    current_price = self.df['close'].iloc[-1]
                    last_up_value = self.df.loc[last_up_indices[-1], 'high']
                    last_down_value = self.df.loc[last_down_indices[-1], 'low']
                    
                    if current_price > last_up_value:
                        return 2  # Señal de compra (precio rompió el último fractal alcista)
                    elif current_price < last_down_value:
                        return 1  # Señal de venta (precio rompió el último fractal bajista)
        
        return 0
        
    def acceleration_deceleration(self, 
                                 fast_period: int = 5, 
                                 slow_period: int = 34, 
                                 signal_period: int = 5,
                                 mode: int = 0) -> int:
        """
        Calcula el indicador Acceleration/Deceleration Oscillator (AC) de Bill Williams y genera señales de trading.
        
        El AC mide la aceleración o desaceleración del momentum del mercado. Se calcula como
        la diferencia entre el Awesome Oscillator (AO) y su media móvil simple de N períodos.
        Muestra la aceleración o desaceleración de la fuerza impulsora actual del mercado.
        
        Interpretación:
        - Cruce de cero: Cuando el AC cruza por encima de cero, indica una posible aceleración alcista.
          Cuando cruza por debajo de cero, indica una posible aceleración bajista.
        - Cambio de color: Cuando las barras del AC cambian de color (de verde a rojo o viceversa),
          puede indicar un cambio en la aceleración del mercado.
        - Divergencia: Cuando el precio forma nuevos máximos/mínimos pero el AC no los confirma,
          puede indicar un posible cambio de tendencia.
        
        Args:
            fast_period: Número de períodos para la media móvil rápida del AO. Por defecto 5.
            slow_period: Número de períodos para la media móvil lenta del AO. Por defecto 34.
            signal_period: Número de períodos para la media móvil del AO. Por defecto 5.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Basado en el valor actual del AC (positivo/negativo)
                  1: Basado en el cruce de cero
                  2: Basado en el cambio de color (cambio de dirección)
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene las columnas 'high' y 'low'.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if 'high' not in self.df.columns or 'low' not in self.df.columns:
            logging.error("ACCELERATION/DECELERATION - El DataFrame no contiene las columnas 'high' y/o 'low'.")
            raise ValueError("El DataFrame debe contener columnas 'high' y 'low' para calcular el AC.")
        
        # Calcular el punto medio de cada barra
        self.df['median_price'] = (self.df['high'] + self.df['low']) / 2
        
        # Calcular las medias móviles simples para el AO
        self.df['ao_fast_sma'] = self.df['median_price'].rolling(window=fast_period).mean()
        self.df['ao_slow_sma'] = self.df['median_price'].rolling(window=slow_period).mean()
        
        # Calcular el Awesome Oscillator
        self.df['ao'] = self.df['ao_fast_sma'] - self.df['ao_slow_sma']
        
        # Calcular la media móvil simple del AO
        self.df['ao_sma'] = self.df['ao'].rolling(window=signal_period).mean()
        
        # Calcular el Acceleration/Deceleration Oscillator
        self.df['ac'] = self.df['ao'] - self.df['ao_sma']
        
        # Calcular cambios en el AC para detectar cruces y cambios de color
        self.df['ac_prev'] = self.df['ac'].shift(1)
        self.df['ac_change'] = self.df['ac'] - self.df['ac_prev']
        
        # Detectar cruces de cero
        self.df['ac_zero_cross_up'] = (self.df['ac'] > 0) & (self.df['ac_prev'] <= 0)
        self.df['ac_zero_cross_down'] = (self.df['ac'] < 0) & (self.df['ac_prev'] >= 0)
        
        # Detectar cambios de color (cambio de dirección)
        self.df['ac_color_change_up'] = (self.df['ac_change'] > 0) & (self.df['ac_change'].shift(1) <= 0)
        self.df['ac_color_change_down'] = (self.df['ac_change'] < 0) & (self.df['ac_change'].shift(1) >= 0)
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en el valor actual del AC
            if self.df['ac'].iloc[-1] > 0:
                return 2  # Señal de compra
            elif self.df['ac'].iloc[-1] < 0:
                return 1  # Señal de venta
            else:
                return 0  # Sin señal clara
        
        elif mode == 1:
            # Basado en el cruce de cero
            if self.df['ac_zero_cross_up'].iloc[-1]:
                return 2  # Señal de compra
            elif self.df['ac_zero_cross_down'].iloc[-1]:
                return 1  # Señal de venta
            else:
                return 0  # Sin señal clara
        
        elif mode == 2:
            # Basado en el cambio de color (cambio de dirección)
            if self.df['ac_color_change_up'].iloc[-1] and self.df['ac'].iloc[-1] > 0:
                return 2  # Señal de compra (cambio a verde por encima de cero)
            elif self.df['ac_color_change_down'].iloc[-1] and self.df['ac'].iloc[-1] < 0:
                return 1  # Señal de venta (cambio a rojo por debajo de cero)
            else:
                return 0  # Sin señal clara
        
        return 0
        
    def market_facilitation_index(self, mode: int = 0) -> int:
        """
        Calcula el indicador Market Facilitation Index (MFI) de Bill Williams y genera señales de trading.
        
        El MFI mide la eficiencia del mercado al relacionar el rango de precios con el volumen.
        Se calcula como (High - Low) / Volumen. Muestra qué tan eficientemente el mercado
        está moviendo el precio en relación con el volumen.
        
        Bill Williams clasifica las barras del MFI en cuatro tipos según el cambio en el MFI
        y el cambio en el volumen:
        - Green (MFI↑, Vol↑): El mercado está acelerando en la dirección actual.
        - Fade (MFI↓, Vol↓): El mercado está perdiendo impulso.
        - Fake (MFI↑, Vol↓): Posible movimiento falso.
        - Squat (MFI↓, Vol↑): El mercado está acumulando energía para un movimiento futuro.
        
        Interpretación:
        - Barras Green consecutivas: Fuerte tendencia, buena oportunidad para entrar.
        - Barras Squat seguidas de Green: Posible inicio de un movimiento fuerte.
        - Barras Fake: Precaución, el movimiento puede ser falso.
        - Barras Fade: El mercado está perdiendo impulso, considerar salir.
        
        Args:
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Basado en el tipo de barra actual
                  1: Basado en secuencias específicas de barras
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene las columnas 'high', 'low' y 'volume'.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if 'high' not in self.df.columns or 'low' not in self.df.columns or 'volume' not in self.df.columns:
            logging.error("MARKET FACILITATION INDEX - El DataFrame no contiene las columnas necesarias.")
            raise ValueError("El DataFrame debe contener columnas 'high', 'low' y 'volume' para calcular el MFI.")
        
        # Calcular el Market Facilitation Index
        self.df['mfi'] = (self.df['high'] - self.df['low']) / self.df['volume']
        
        # Calcular cambios en el MFI y el volumen
        self.df['mfi_change'] = self.df['mfi'] - self.df['mfi'].shift(1)
        self.df['volume_change'] = self.df['volume'] - self.df['volume'].shift(1)
        
        # Clasificar las barras según Bill Williams
        # Green: MFI↑, Vol↑
        self.df['mfi_green'] = (self.df['mfi_change'] > 0) & (self.df['volume_change'] > 0)
        
        # Fade: MFI↓, Vol↓
        self.df['mfi_fade'] = (self.df['mfi_change'] < 0) & (self.df['volume_change'] < 0)
        
        # Fake: MFI↑, Vol↓
        self.df['mfi_fake'] = (self.df['mfi_change'] > 0) & (self.df['volume_change'] < 0)
        
        # Squat: MFI↓, Vol↑
        self.df['mfi_squat'] = (self.df['mfi_change'] < 0) & (self.df['volume_change'] > 0)
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en el tipo de barra actual
            if self.df['mfi_green'].iloc[-1]:
                return 2  # Señal de compra (barra Green)
            elif self.df['mfi_fade'].iloc[-1]:
                return 1  # Señal de venta (barra Fade)
            elif self.df['mfi_fake'].iloc[-1]:
                return 0  # Sin señal clara (barra Fake)
            elif self.df['mfi_squat'].iloc[-1]:
                return 0  # Sin señal clara (barra Squat)
        
        elif mode == 1:
            # Basado en secuencias específicas de barras
            # Verificar si hay una secuencia de Squat seguida de Green (posible inicio de tendencia)
            if self.df['mfi_green'].iloc[-1] and self.df['mfi_squat'].iloc[-2]:
                return 2  # Señal de compra
            
            # Verificar si hay una secuencia de Green seguida de Fade (posible fin de tendencia)
            elif self.df['mfi_fade'].iloc[-1] and self.df['mfi_green'].iloc[-2]:
                return 1  # Señal de venta
            
            # Verificar si hay dos barras Green consecutivas (tendencia fuerte)
            elif self.df['mfi_green'].iloc[-1] and self.df['mfi_green'].iloc[-2]:
                return 2  # Señal de compra
            
            # Verificar si hay dos barras Fade consecutivas (tendencia débil)
            elif self.df['mfi_fade'].iloc[-1] and self.df['mfi_fade'].iloc[-2]:
                return 1  # Señal de venta
        
        return 0