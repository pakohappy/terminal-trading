# -*- coding: utf-8 -*-
"""
Módulo de indicadores técnicos de tipo oscilador.

Este módulo implementa indicadores técnicos de tipo oscilador, que fluctúan entre
valores extremos para identificar condiciones de sobrecompra o sobreventa en el mercado.
Incluye varios osciladores populares:

1. Oscilador Estocástico: Mide la posición del precio actual en relación con su rango
   de precios durante un período determinado.
2. RSI (Relative Strength Index): Mide la velocidad y el cambio de los movimientos de
   precio para evaluar condiciones de sobrecompra o sobreventa.
3. CCI (Commodity Channel Index): Mide la desviación del precio de un activo respecto
   a su precio medio estadístico.
4. Williams %R: Similar al Estocástico, mide la posición del precio actual en relación
   con el rango alto-bajo durante un período específico.
5. Momentum: Mide la velocidad de cambio del precio comparando el precio actual con
   el precio de un número específico de períodos atrás.
6. ROC (Rate of Change): Mide la variación porcentual del precio en un período determinado.

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
import numpy as np

class Oscillator:
    """
    Clase que implementa indicadores técnicos de tipo oscilador.
    
    Esta clase proporciona métodos para calcular diversos osciladores como el Estocástico, RSI,
    CCI, Williams %R, Momentum y ROC, que ayudan a identificar condiciones de sobrecompra 
    o sobreventa y posibles puntos de reversión en el mercado. Los osciladores son herramientas 
    valiosas para determinar cuándo un activo puede estar sobrevaluado o infravaluado temporalmente.
    
    Indicadores implementados:
    - Estocástico: Mide la posición del precio actual en relación con su rango de precios.
    - RSI (Relative Strength Index): Mide la velocidad y cambio de los movimientos de precio.
    - CCI (Commodity Channel Index): Mide la desviación del precio respecto a su media estadística.
    - Williams %R: Similar al Estocástico, pero con escala invertida (-100 a 0).
    - Momentum: Mide la velocidad de cambio del precio comparando con un período anterior.
    - ROC (Rate of Change): Mide la variación porcentual del precio en un período determinado.
    
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
        
    def cci(self, 
            period: int = 20, 
            constant: float = 0.015, 
            overbought_level: int = 100, 
            oversold_level: int = -100, 
            mode: int = 0) -> int:
        """
        Calcula el Commodity Channel Index (CCI) y genera señales de trading.
        
        El CCI es un oscilador desarrollado por Donald Lambert que mide la desviación
        del precio de un activo respecto a su precio medio estadístico. Ayuda a identificar
        ciclos, condiciones de sobrecompra/sobreventa y posibles puntos de reversión.
        
        El CCI se calcula mediante la siguiente fórmula:
        CCI = (Precio Típico - SMA del Precio Típico) / (constante * Desviación Media)
        
        Donde:
        - Precio Típico = (High + Low + Close) / 3
        - SMA = Media Móvil Simple del Precio Típico
        - Desviación Media = Media de las desviaciones absolutas del Precio Típico respecto a su SMA
        - Constante = Multiplicador (normalmente 0.015) que hace que el CCI caiga dentro de -100 a +100
          aproximadamente el 70-80% del tiempo
        
        Interpretación:
        - Valores por encima de +100 indican sobrecompra (posible señal de venta)
        - Valores por debajo de -100 indican sobreventa (posible señal de compra)
        - Cruce de la línea cero hacia arriba: Señal alcista
        - Cruce de la línea cero hacia abajo: Señal bajista
        - Divergencias entre el precio y el CCI pueden indicar posibles reversiones
        
        Args:
            period: Número de períodos para calcular el CCI. Por defecto 20.
            constant: Constante multiplicadora para la desviación media. Por defecto 0.015.
            overbought_level: Nivel de sobrecompra personalizado. Por defecto 100.
            oversold_level: Nivel de sobreventa personalizado. Por defecto -100.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Señales basadas en niveles de sobrecompra/sobreventa
                  1: Señales basadas en cruces de la línea cero
                  2: Señales basadas en divergencias
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene las columnas necesarias o si los parámetros son inválidos.
        """
        # Validaciones generales
        if not {'high', 'low', 'close'}.issubset(self.df.columns):
            logging.error("CCI - El DataFrame debe contener las columnas 'high', 'low' y 'close'.")
            raise ValueError("CCI - El DataFrame debe contener las columnas 'high', 'low' y 'close'.")
        
        if len(self.df) < period:
            logging.error(f"CCI - El número de filas ({len(self.df)}) es menor que el período ({period}).")
            raise ValueError(f"CCI - El número de filas ({len(self.df)}) es menor que el período ({period}).")
        
        if period <= 0:
            logging.error("CCI - El período debe ser mayor que 0.")
            raise ValueError("CCI - El período debe ser mayor que 0.")
        
        if constant <= 0:
            logging.error("CCI - La constante debe ser mayor que 0.")
            raise ValueError("CCI - La constante debe ser mayor que 0.")
        
        # Calcular el Precio Típico
        self.df['typical_price'] = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        
        # Calcular la Media Móvil Simple del Precio Típico
        self.df['sma_typical_price'] = self.df['typical_price'].rolling(window=period).mean()
        
        # Calcular la Desviación Media
        self.df['mean_deviation'] = self.df['typical_price'].rolling(window=period).apply(
            lambda x: sum(abs(i - x.mean()) for i in x) / period
        )
        
        # Calcular el CCI
        self.df['cci'] = (self.df['typical_price'] - self.df['sma_typical_price']) / (constant * self.df['mean_deviation'])
        
        # Calcular valores previos para detectar cruces
        self.df['cci_prev'] = self.df['cci'].shift(1)
        
        # Detectar cruces de la línea cero
        self.df['cci_zero_cross_up'] = (self.df['cci'] > 0) & (self.df['cci_prev'] <= 0)
        self.df['cci_zero_cross_down'] = (self.df['cci'] < 0) & (self.df['cci_prev'] >= 0)
        
        # Detectar condiciones de sobrecompra/sobreventa
        self.df['cci_overbought'] = self.df['cci'] > overbought_level
        self.df['cci_oversold'] = self.df['cci'] < oversold_level
        
        # Detectar salidas de zonas de sobrecompra/sobreventa
        self.df['cci_exit_overbought'] = (self.df['cci'] < overbought_level) & (self.df['cci_prev'] >= overbought_level)
        self.df['cci_exit_oversold'] = (self.df['cci'] > oversold_level) & (self.df['cci_prev'] <= oversold_level)
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en niveles de sobrecompra/sobreventa
            if self.df['cci_exit_oversold'].iloc[-1]:
                return 2  # Señal de compra (salida de sobreventa)
            elif self.df['cci_exit_overbought'].iloc[-1]:
                return 1  # Señal de venta (salida de sobrecompra)
            else:
                return 0  # Sin señal clara
        
        elif mode == 1:
            # Basado en cruces de la línea cero
            if self.df['cci_zero_cross_up'].iloc[-1]:
                return 2  # Señal de compra (cruce alcista de la línea cero)
            elif self.df['cci_zero_cross_down'].iloc[-1]:
                return 1  # Señal de venta (cruce bajista de la línea cero)
            else:
                return 0  # Sin señal clara
        
        elif mode == 2:
            # Basado en divergencias (simplificado)
            # Verificar si hay una divergencia alcista: precio hace mínimos más bajos pero CCI hace mínimos más altos
            if (len(self.df) >= period * 2):
                # Buscar mínimos locales en el precio y en el CCI
                window_size = period
                price_window = self.df['close'].iloc[-window_size:]
                cci_window = self.df['cci'].iloc[-window_size:]
                
                # Encontrar mínimo local en el precio y en el CCI
                price_min_idx = price_window.idxmin()
                cci_min_idx = cci_window.idxmin()
                
                # Verificar si hay una divergencia alcista (precio hace mínimo pero CCI no)
                if price_min_idx == self.df.index[-1] and cci_min_idx != self.df.index[-1] and self.df['cci'].iloc[-1] > self.df['cci'].iloc[-2]:
                    return 2  # Señal de compra (divergencia alcista)
                
                # Verificar si hay una divergencia bajista (precio hace máximo pero CCI no)
                price_max_idx = price_window.idxmax()
                cci_max_idx = cci_window.idxmax()
                
                if price_max_idx == self.df.index[-1] and cci_max_idx != self.df.index[-1] and self.df['cci'].iloc[-1] < self.df['cci'].iloc[-2]:
                    return 1  # Señal de venta (divergencia bajista)
        
        return 0  # Sin señal clara
        
    def rsi(self,
            period: int = 14,
            overbought_level: int = 70,
            oversold_level: int = 30,
            mode: int = 0) -> int:
        """
        Calcula el Índice de Fuerza Relativa (RSI) y genera señales de trading.
        
        El RSI es un oscilador de momento que mide la velocidad y el cambio de los movimientos
        de precio. Desarrollado por J. Welles Wilder en 1978, el RSI oscila entre 0 y 100 y
        tradicionalmente se considera que un activo está sobrecomprado cuando el RSI supera 70
        y sobrevendido cuando cae por debajo de 30.
        
        El RSI compara la magnitud de las ganancias recientes con la magnitud de las pérdidas
        recientes para determinar las condiciones de sobrecompra y sobreventa de un activo.
        
        La fórmula del RSI es:
        RSI = 100 - (100 / (1 + RS))
        donde RS = Promedio de ganancias / Promedio de pérdidas durante un período determinado.
        
        Interpretación:
        - Valores por encima de 70 indican sobrecompra (posible señal de venta)
        - Valores por debajo de 30 indican sobreventa (posible señal de compra)
        - El nivel 50 actúa como línea central y puede indicar cambios en la tendencia
        - Las divergencias entre el precio y el RSI pueden indicar posibles reversiones
        - El RSI tiende a permanecer en la zona superior durante tendencias alcistas fuertes
          y en la zona inferior durante tendencias bajistas fuertes
        
        Args:
            period: Número de periodos para calcular el RSI. Por defecto 14.
            overbought_level: Nivel de sobrecompra personalizado. Por defecto 70.
            oversold_level: Nivel de sobreventa personalizado. Por defecto 30.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Señales basadas en cruces del RSI con niveles de sobrecompra/sobreventa
                  1: Señales basadas únicamente en zonas de sobrecompra/sobreventa
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra (RSI sale de zona de sobreventa o está en sobreventa)
                 1: Señal de venta (RSI entra en zona de sobrecompra o está en sobrecompra)
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene la columna 'close' o si los parámetros son inválidos.
        """
        # Validaciones generales.
        if 'close' not in self.df.columns:
            logging.error("RSI - El DataFrame debe contener la columna 'close'.")
            raise ValueError("RSI - El DataFrame debe contener la columna 'close'.")
        if len(self.df) < period + 1:
            logging.error("RSI - El número de filas no es suficiente para calcular el RSI.")
            raise ValueError("RSI - El número de filas no es suficiente para calcular el RSI.")
        if period <= 0:
            logging.error("RSI - El período debe ser mayor que 0.")
            raise ValueError("RSI - El período debe ser mayor que 0.")
            
        # Calcular cambios en el precio de cierre
        delta = self.df['close'].diff()
        
        # Separar ganancias (cambios positivos) y pérdidas (cambios negativos)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calcular el promedio de ganancias y pérdidas iniciales
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calcular el RSI
        rs = avg_gain / avg_loss
        self.df['RSI'] = 100 - (100 / (1 + rs))
        
        # Detectar sobrecompra/sobreventa
        self.df['rsi_sobrecompra'] = self.df['RSI'] > overbought_level
        self.df['rsi_sobreventa'] = self.df['RSI'] < oversold_level
        
        # Detectar cruces con niveles de sobrecompra/sobreventa
        self.df['rsi_cruce_sobrecompra_arriba'] = (self.df['RSI'].shift(1) <= overbought_level) & \
                                                 (self.df['RSI'] > overbought_level)
        self.df['rsi_cruce_sobrecompra_abajo'] = (self.df['RSI'].shift(1) >= overbought_level) & \
                                                (self.df['RSI'] < overbought_level)
        self.df['rsi_cruce_sobreventa_arriba'] = (self.df['RSI'].shift(1) <= oversold_level) & \
                                               (self.df['RSI'] > oversold_level)
        self.df['rsi_cruce_sobreventa_abajo'] = (self.df['RSI'].shift(1) >= oversold_level) & \
                                              (self.df['RSI'] < oversold_level)
        
        # Detectar divergencias
        self.df['rsi_divergencia_alcista'] = (
            (self.df['close'] < self.df['close'].shift(1)) &  # Mínimo más bajo en precio
            (self.df['RSI'] > self.df['RSI'].shift(1))  # Mínimo más alto en RSI
        )
        self.df['rsi_divergencia_bajista'] = (
            (self.df['close'] > self.df['close'].shift(1)) &  # Máximo más alto en precio
            (self.df['RSI'] < self.df['RSI'].shift(1))  # Máximo más bajo en RSI
        )
        
        # Obtener los últimos valores para generar señales
        ultima_sobrecompra = self.df['rsi_sobrecompra'].iloc[-1]
        ultima_sobreventa = self.df['rsi_sobreventa'].iloc[-1]
        ultimo_cruce_sobrecompra_arriba = self.df['rsi_cruce_sobrecompra_arriba'].iloc[-1]
        ultimo_cruce_sobreventa_arriba = self.df['rsi_cruce_sobreventa_arriba'].iloc[-1]
        
        # Detectamos cruces con niveles de sobrecompra/sobreventa
        if mode == 0:
            if ultimo_cruce_sobreventa_arriba:
                return 2  # Señal de compra (RSI sale de zona de sobreventa)
            elif ultimo_cruce_sobrecompra_arriba:
                return 1  # Señal de venta (RSI entra en zona de sobrecompra)
            else:
                return 0  # Sin señal clara
        
        # Detectamos zona de sobrecompra/sobreventa
        if mode == 1:
            if ultima_sobreventa:
                return 2  # Señal de compra (RSI en zona de sobreventa)
            elif ultima_sobrecompra:
                return 1  # Señal de venta (RSI en zona de sobrecompra)
            else:
                return 0  # Sin señal clara
                
        return 0  # Sin señal clara
        
    def williams_r(self, 
                  period: int = 14, 
                  overbought_level: int = -20, 
                  oversold_level: int = -80, 
                  mode: int = 0) -> int:
        """
        Calcula el indicador Williams %R y genera señales de trading.
        
        El Williams %R, desarrollado por Larry Williams, es un oscilador de momentum que
        mide los niveles de sobrecompra y sobreventa. Es similar al Oscilador Estocástico,
        pero con una escala invertida y sin línea de señal. Mide la posición del precio actual
        en relación con el rango alto-bajo durante un período específico.
        
        El Williams %R se calcula mediante la siguiente fórmula:
        %R = -100 * (Máximo(n) - Cierre) / (Máximo(n) - Mínimo(n))
        
        Donde:
        - Máximo(n) = Precio más alto durante n períodos
        - Mínimo(n) = Precio más bajo durante n períodos
        - Cierre = Precio de cierre actual
        
        Interpretación:
        - Valores entre -80 y -100 indican sobreventa (posible señal de compra)
        - Valores entre 0 y -20 indican sobrecompra (posible señal de venta)
        - Divergencias entre el precio y el Williams %R pueden indicar posibles reversiones
        - Fallos de oscilación (cuando el indicador no alcanza la zona de sobrecompra/sobreventa)
          pueden indicar debilidad en la tendencia
        
        Args:
            period: Número de períodos para calcular el Williams %R. Por defecto 14.
            overbought_level: Nivel de sobrecompra personalizado. Por defecto -20.
            oversold_level: Nivel de sobreventa personalizado. Por defecto -80.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Señales basadas en niveles de sobrecompra/sobreventa
                  1: Señales basadas en cruces de niveles medios
                  2: Señales basadas en divergencias
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene las columnas necesarias o si los parámetros son inválidos.
        """
        # Validaciones generales
        if not {'high', 'low', 'close'}.issubset(self.df.columns):
            logging.error("WILLIAMS %R - El DataFrame debe contener las columnas 'high', 'low' y 'close'.")
            raise ValueError("WILLIAMS %R - El DataFrame debe contener las columnas 'high', 'low' y 'close'.")
        
        if len(self.df) < period:
            logging.error(f"WILLIAMS %R - El número de filas ({len(self.df)}) es menor que el período ({period}).")
            raise ValueError(f"WILLIAMS %R - El número de filas ({len(self.df)}) es menor que el período ({period}).")
        
        if period <= 0:
            logging.error("WILLIAMS %R - El período debe ser mayor que 0.")
            raise ValueError("WILLIAMS %R - El período debe ser mayor que 0.")
        
        # Calcular el máximo y mínimo para el período
        self.df['highest_high'] = self.df['high'].rolling(window=period).max()
        self.df['lowest_low'] = self.df['low'].rolling(window=period).min()
        
        # Calcular el Williams %R
        self.df['williams_r'] = -100 * (self.df['highest_high'] - self.df['close']) / (self.df['highest_high'] - self.df['lowest_low'])
        
        # Calcular valores previos para detectar cruces
        self.df['williams_r_prev'] = self.df['williams_r'].shift(1)
        
        # Detectar cruces de niveles medios (-50)
        self.df['williams_r_mid_cross_up'] = (self.df['williams_r'] > -50) & (self.df['williams_r_prev'] <= -50)
        self.df['williams_r_mid_cross_down'] = (self.df['williams_r'] < -50) & (self.df['williams_r_prev'] >= -50)
        
        # Detectar condiciones de sobrecompra/sobreventa
        self.df['williams_r_overbought'] = self.df['williams_r'] >= overbought_level
        self.df['williams_r_oversold'] = self.df['williams_r'] <= oversold_level
        
        # Detectar salidas de zonas de sobrecompra/sobreventa
        self.df['williams_r_exit_overbought'] = (self.df['williams_r'] < overbought_level) & (self.df['williams_r_prev'] >= overbought_level)
        self.df['williams_r_exit_oversold'] = (self.df['williams_r'] > oversold_level) & (self.df['williams_r_prev'] <= oversold_level)
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en niveles de sobrecompra/sobreventa
            if self.df['williams_r_exit_oversold'].iloc[-1]:
                return 2  # Señal de compra (salida de sobreventa)
            elif self.df['williams_r_exit_overbought'].iloc[-1]:
                return 1  # Señal de venta (salida de sobrecompra)
            else:
                return 0  # Sin señal clara
        
        elif mode == 1:
            # Basado en cruces de niveles medios
            if self.df['williams_r_mid_cross_up'].iloc[-1]:
                return 2  # Señal de compra (cruce alcista del nivel medio)
            elif self.df['williams_r_mid_cross_down'].iloc[-1]:
                return 1  # Señal de venta (cruce bajista del nivel medio)
            else:
                return 0  # Sin señal clara
        
        elif mode == 2:
            # Basado en divergencias (simplificado)
            # Verificar si hay una divergencia alcista: precio hace mínimos más bajos pero Williams %R hace mínimos más altos
            if (len(self.df) >= period * 2):
                # Buscar mínimos locales en el precio y en el Williams %R
                window_size = period
                price_window = self.df['close'].iloc[-window_size:]
                williams_r_window = self.df['williams_r'].iloc[-window_size:]
                
                # Encontrar mínimo local en el precio y en el Williams %R
                price_min_idx = price_window.idxmin()
                williams_r_min_idx = williams_r_window.idxmin()
                
                # Verificar si hay una divergencia alcista (precio hace mínimo pero Williams %R no)
                if price_min_idx == self.df.index[-1] and williams_r_min_idx != self.df.index[-1] and self.df['williams_r'].iloc[-1] > self.df['williams_r'].iloc[-2]:
                    return 2  # Señal de compra (divergencia alcista)
                
                # Verificar si hay una divergencia bajista (precio hace máximo pero Williams %R no)
                price_max_idx = price_window.idxmax()
                williams_r_max_idx = williams_r_window.idxmax()
                
                if price_max_idx == self.df.index[-1] and williams_r_max_idx != self.df.index[-1] and self.df['williams_r'].iloc[-1] < self.df['williams_r'].iloc[-2]:
                    return 1  # Señal de venta (divergencia bajista)
        
        return 0  # Sin señal clara
        
    def momentum(self, 
                period: int = 14, 
                signal_period: int = 9, 
                mode: int = 0) -> int:
        """
        Calcula el indicador Momentum y genera señales de trading.
        
        El Momentum es un indicador que mide la velocidad de cambio del precio comparando
        el precio actual con el precio de un número específico de períodos atrás.
        Ayuda a identificar la fuerza o debilidad de una tendencia y posibles puntos de reversión.
        
        El Momentum se calcula mediante la siguiente fórmula:
        Momentum = Precio actual - Precio hace n períodos
        
        También se puede calcular como un ratio:
        Momentum Ratio = (Precio actual / Precio hace n períodos) * 100
        
        Interpretación:
        - Valores positivos y crecientes indican una tendencia alcista fuerte
        - Valores negativos y decrecientes indican una tendencia bajista fuerte
        - Cruce de la línea cero hacia arriba: Señal alcista
        - Cruce de la línea cero hacia abajo: Señal bajista
        - Divergencias entre el precio y el Momentum pueden indicar posibles reversiones
        
        Args:
            period: Número de períodos para calcular el Momentum. Por defecto 14.
            signal_period: Número de períodos para calcular la media móvil del Momentum. Por defecto 9.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Señales basadas en cruces de la línea cero
                  1: Señales basadas en cruces de la línea de señal
                  2: Señales basadas en divergencias
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene la columna 'close' o si los parámetros son inválidos.
        """
        # Validaciones generales
        if 'close' not in self.df.columns:
            logging.error("MOMENTUM - El DataFrame debe contener la columna 'close'.")
            raise ValueError("MOMENTUM - El DataFrame debe contener la columna 'close'.")
        
        if len(self.df) < period + signal_period:
            logging.error(f"MOMENTUM - El número de filas ({len(self.df)}) es insuficiente para los períodos especificados.")
            raise ValueError(f"MOMENTUM - El número de filas ({len(self.df)}) es insuficiente para los períodos especificados.")
        
        if period <= 0 or signal_period <= 0:
            logging.error("MOMENTUM - Los períodos deben ser mayores que 0.")
            raise ValueError("MOMENTUM - Los períodos deben ser mayores que 0.")
        
        # Calcular el Momentum
        self.df['momentum'] = self.df['close'] - self.df['close'].shift(period)
        
        # Calcular la línea de señal (media móvil del Momentum)
        self.df['momentum_signal'] = self.df['momentum'].rolling(window=signal_period).mean()
        
        # Calcular valores previos para detectar cruces
        self.df['momentum_prev'] = self.df['momentum'].shift(1)
        self.df['momentum_signal_prev'] = self.df['momentum_signal'].shift(1)
        
        # Detectar cruces de la línea cero
        self.df['momentum_zero_cross_up'] = (self.df['momentum'] > 0) & (self.df['momentum_prev'] <= 0)
        self.df['momentum_zero_cross_down'] = (self.df['momentum'] < 0) & (self.df['momentum_prev'] >= 0)
        
        # Detectar cruces de la línea de señal
        self.df['momentum_signal_cross_up'] = (self.df['momentum'] > self.df['momentum_signal']) & (self.df['momentum_prev'] <= self.df['momentum_signal_prev'])
        self.df['momentum_signal_cross_down'] = (self.df['momentum'] < self.df['momentum_signal']) & (self.df['momentum_prev'] >= self.df['momentum_signal_prev'])
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en cruces de la línea cero
            if self.df['momentum_zero_cross_up'].iloc[-1]:
                return 2  # Señal de compra (cruce alcista de la línea cero)
            elif self.df['momentum_zero_cross_down'].iloc[-1]:
                return 1  # Señal de venta (cruce bajista de la línea cero)
            else:
                return 0  # Sin señal clara
        
        elif mode == 1:
            # Basado en cruces de la línea de señal
            if self.df['momentum_signal_cross_up'].iloc[-1]:
                return 2  # Señal de compra (cruce alcista de la línea de señal)
            elif self.df['momentum_signal_cross_down'].iloc[-1]:
                return 1  # Señal de venta (cruce bajista de la línea de señal)
            else:
                return 0  # Sin señal clara
        
        elif mode == 2:
            # Basado en divergencias (simplificado)
            # Verificar si hay una divergencia alcista: precio hace mínimos más bajos pero Momentum hace mínimos más altos
            if (len(self.df) >= period * 2):
                # Buscar mínimos locales en el precio y en el Momentum
                window_size = period
                price_window = self.df['close'].iloc[-window_size:]
                momentum_window = self.df['momentum'].iloc[-window_size:]
                
                # Encontrar mínimo local en el precio y en el Momentum
                price_min_idx = price_window.idxmin()
                momentum_min_idx = momentum_window.idxmin()
                
                # Verificar si hay una divergencia alcista (precio hace mínimo pero Momentum no)
                if price_min_idx == self.df.index[-1] and momentum_min_idx != self.df.index[-1] and self.df['momentum'].iloc[-1] > self.df['momentum'].iloc[-2]:
                    return 2  # Señal de compra (divergencia alcista)
                
                # Verificar si hay una divergencia bajista (precio hace máximo pero Momentum no)
                price_max_idx = price_window.idxmax()
                momentum_max_idx = momentum_window.idxmax()
                
                if price_max_idx == self.df.index[-1] and momentum_max_idx != self.df.index[-1] and self.df['momentum'].iloc[-1] < self.df['momentum'].iloc[-2]:
                    return 1  # Señal de venta (divergencia bajista)
        
        return 0  # Sin señal clara
        
    def roc(self, 
           period: int = 12, 
           signal_period: int = 9, 
           mode: int = 0) -> int:
        """
        Calcula el indicador Rate of Change (ROC) y genera señales de trading.
        
        El ROC es un oscilador que mide la variación porcentual del precio en un período
        determinado. Ayuda a identificar la velocidad de cambio del precio, condiciones
        de sobrecompra/sobreventa y posibles puntos de reversión.
        
        El ROC se calcula mediante la siguiente fórmula:
        ROC = ((Precio actual / Precio hace n períodos) - 1) * 100
        
        Interpretación:
        - Valores positivos y crecientes indican una tendencia alcista fuerte
        - Valores negativos y decrecientes indican una tendencia bajista fuerte
        - Cruce de la línea cero hacia arriba: Señal alcista
        - Cruce de la línea cero hacia abajo: Señal bajista
        - Divergencias entre el precio y el ROC pueden indicar posibles reversiones
        - Valores extremos pueden indicar condiciones de sobrecompra/sobreventa
        
        Args:
            period: Número de períodos para calcular el ROC. Por defecto 12.
            signal_period: Número de períodos para calcular la media móvil del ROC. Por defecto 9.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Señales basadas en cruces de la línea cero
                  1: Señales basadas en cruces de la línea de señal
                  2: Señales basadas en divergencias
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene la columna 'close' o si los parámetros son inválidos.
        """
        # Validaciones generales
        if 'close' not in self.df.columns:
            logging.error("ROC - El DataFrame debe contener la columna 'close'.")
            raise ValueError("ROC - El DataFrame debe contener la columna 'close'.")
        
        if len(self.df) < period + signal_period:
            logging.error(f"ROC - El número de filas ({len(self.df)}) es insuficiente para los períodos especificados.")
            raise ValueError(f"ROC - El número de filas ({len(self.df)}) es insuficiente para los períodos especificados.")
        
        if period <= 0 or signal_period <= 0:
            logging.error("ROC - Los períodos deben ser mayores que 0.")
            raise ValueError("ROC - Los períodos deben ser mayores que 0.")
        
        # Calcular el Rate of Change (ROC)
        self.df['roc'] = ((self.df['close'] / self.df['close'].shift(period)) - 1) * 100
        
        # Calcular la línea de señal (media móvil del ROC)
        self.df['roc_signal'] = self.df['roc'].rolling(window=signal_period).mean()
        
        # Calcular valores previos para detectar cruces
        self.df['roc_prev'] = self.df['roc'].shift(1)
        self.df['roc_signal_prev'] = self.df['roc_signal'].shift(1)
        
        # Detectar cruces de la línea cero
        self.df['roc_zero_cross_up'] = (self.df['roc'] > 0) & (self.df['roc_prev'] <= 0)
        self.df['roc_zero_cross_down'] = (self.df['roc'] < 0) & (self.df['roc_prev'] >= 0)
        
        # Detectar cruces de la línea de señal
        self.df['roc_signal_cross_up'] = (self.df['roc'] > self.df['roc_signal']) & (self.df['roc_prev'] <= self.df['roc_signal_prev'])
        self.df['roc_signal_cross_down'] = (self.df['roc'] < self.df['roc_signal']) & (self.df['roc_prev'] >= self.df['roc_signal_prev'])
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en cruces de la línea cero
            if self.df['roc_zero_cross_up'].iloc[-1]:
                return 2  # Señal de compra (cruce alcista de la línea cero)
            elif self.df['roc_zero_cross_down'].iloc[-1]:
                return 1  # Señal de venta (cruce bajista de la línea cero)
            else:
                return 0  # Sin señal clara
        
        elif mode == 1:
            # Basado en cruces de la línea de señal
            if self.df['roc_signal_cross_up'].iloc[-1]:
                return 2  # Señal de compra (cruce alcista de la línea de señal)
            elif self.df['roc_signal_cross_down'].iloc[-1]:
                return 1  # Señal de venta (cruce bajista de la línea de señal)
            else:
                return 0  # Sin señal clara
        
        elif mode == 2:
            # Basado en divergencias (simplificado)
            # Verificar si hay una divergencia alcista: precio hace mínimos más bajos pero ROC hace mínimos más altos
            if (len(self.df) >= period * 2):
                # Buscar mínimos locales en el precio y en el ROC
                window_size = period
                price_window = self.df['close'].iloc[-window_size:]
                roc_window = self.df['roc'].iloc[-window_size:]
                
                # Encontrar mínimo local en el precio y en el ROC
                price_min_idx = price_window.idxmin()
                roc_min_idx = roc_window.idxmin()
                
                # Verificar si hay una divergencia alcista (precio hace mínimo pero ROC no)
                if price_min_idx == self.df.index[-1] and roc_min_idx != self.df.index[-1] and self.df['roc'].iloc[-1] > self.df['roc'].iloc[-2]:
                    return 2  # Señal de compra (divergencia alcista)
                
                # Verificar si hay una divergencia bajista (precio hace máximo pero ROC no)
                price_max_idx = price_window.idxmax()
                roc_max_idx = roc_window.idxmax()
                
                if price_max_idx == self.df.index[-1] and roc_max_idx != self.df.index[-1] and self.df['roc'].iloc[-1] < self.df['roc'].iloc[-2]:
                    return 1  # Señal de venta (divergencia bajista)
        
        return 0  # Sin señal clara
        
    def chaikin_oscillator(self, fast_period: int = 3, slow_period: int = 10, mode: int = 0) -> int:
        """
        Calcula el Chaikin Oscillator y genera señales de trading.
        
        El Chaikin Oscillator es un indicador que combina acumulación/distribución con MACD
        para detectar cambios en la presión de compra/venta. Se calcula como la diferencia
        entre dos medias móviles exponenciales (rápida y lenta) de la línea de
        Acumulación/Distribución (A/D).
        
        Args:
            fast_period: Número de períodos para la EMA rápida. Por defecto 3.
            slow_period: Número de períodos para la EMA lenta. Por defecto 10.
            mode: Modo de operación que determina cómo se generan las señales:
                 0: Basado en el cruce de la línea cero
                 1: Basado en divergencias entre precio y Chaikin Oscillator
                 Por defecto 0.
                 
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra (Chaikin Oscillator cruza por encima de cero o divergencia alcista)
                 1: Señal de venta (Chaikin Oscillator cruza por debajo de cero o divergencia bajista)
                 0: Sin señal clara
                 
        Raises:
            ValueError: Si el DataFrame no contiene las columnas necesarias.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if not {'high', 'low', 'close', 'volume'}.issubset(self.df.columns):
            logging.error("CHAIKIN OSCILLATOR - El DataFrame debe contener las columnas 'high', 'low', 'close' y 'volume'.")
            raise ValueError("El DataFrame debe contener las columnas 'high', 'low', 'close' y 'volume' para calcular el Chaikin Oscillator.")
        
        # Crear una copia del DataFrame para no modificar el original
        df_temp = self.df.copy()
        
        # Calcular el Money Flow Multiplier (MFM)
        # MFM = ((Close - Low) - (High - Close)) / (High - Low)
        df_temp['mfm'] = ((df_temp['close'] - df_temp['low']) - 
                          (df_temp['high'] - df_temp['close'])) / (df_temp['high'] - df_temp['low'])
        
        # Reemplazar valores infinitos o NaN con ceros
        df_temp['mfm'].replace([np.inf, -np.inf], 0, inplace=True)
        df_temp['mfm'].fillna(0, inplace=True)
        
        # Calcular el Money Flow Volume (MFV)
        df_temp['mfv'] = df_temp['mfm'] * df_temp['volume']
        
        # Calcular la línea de Acumulación/Distribución (A/D)
        df_temp['ad_line'] = df_temp['mfv'].cumsum()
        
        # Calcular las EMAs de la línea A/D
        df_temp['ad_ema_fast'] = df_temp['ad_line'].ewm(span=fast_period, adjust=False).mean()
        df_temp['ad_ema_slow'] = df_temp['ad_line'].ewm(span=slow_period, adjust=False).mean()
        
        # Calcular el Chaikin Oscillator
        df_temp['chaikin_osc'] = df_temp['ad_ema_fast'] - df_temp['ad_ema_slow']
        
        # Añadir el Chaikin Oscillator al DataFrame original
        self.df['chaikin_osc'] = df_temp['chaikin_osc']
        
        # Detectar cruces de la línea cero
        self.df['chaikin_cruce_alcista'] = (self.df['chaikin_osc'].shift(1) < 0) & (self.df['chaikin_osc'] > 0)
        self.df['chaikin_cruce_bajista'] = (self.df['chaikin_osc'].shift(1) > 0) & (self.df['chaikin_osc'] < 0)
        
        # Detectar divergencias
        # Divergencia alcista: precio hace mínimos más bajos pero Chaikin hace mínimos más altos
        precio_bajando = self.df['close'].iloc[-1] < self.df['close'].iloc[-2]
        chaikin_subiendo = self.df['chaikin_osc'].iloc[-1] > self.df['chaikin_osc'].iloc[-2]
        divergencia_alcista = precio_bajando and chaikin_subiendo
        
        # Divergencia bajista: precio hace máximos más altos pero Chaikin hace máximos más bajos
        precio_subiendo = self.df['close'].iloc[-1] > self.df['close'].iloc[-2]
        chaikin_bajando = self.df['chaikin_osc'].iloc[-1] < self.df['chaikin_osc'].iloc[-2]
        divergencia_bajista = precio_subiendo and chaikin_bajando
        
        # Obtener los últimos valores
        ultimo_cruce_alcista = self.df['chaikin_cruce_alcista'].iloc[-1]
        ultimo_cruce_bajista = self.df['chaikin_cruce_bajista'].iloc[-1]
        
        # Generar señales según el modo
        if mode == 0:
            if ultimo_cruce_alcista:
                return 2  # Señal de compra
            elif ultimo_cruce_bajista:
                return 1  # Señal de venta
        
        elif mode == 1:
            if divergencia_alcista:
                return 2  # Señal de compra
            elif divergencia_bajista:
                return 1  # Señal de venta
        
        return 0  # Sin señal clara