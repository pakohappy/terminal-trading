# -*- coding: utf-8 -*-
"""
Módulo de indicadores técnicos de tendencia.

Este módulo implementa indicadores técnicos que ayudan a identificar la dirección
y fuerza de la tendencia en el mercado. Incluye indicadores como:
- MACD (Moving Average Convergence Divergence): Muestra la relación entre dos medias
  móviles exponenciales y ayuda a identificar cambios en la fuerza, dirección, 
  momentum y duración de una tendencia.
- SMA (Simple Moving Average): Calcula el precio promedio durante un período específico
  para suavizar las fluctuaciones y mostrar la tendencia general.
- EMA (Exponential Moving Average): Similar a la SMA pero da más peso a los datos recientes,
  reaccionando más rápido a los cambios de precio.
- WMA (Weighted Moving Average): Asigna pesos linealmente decrecientes a los precios,
  dando más importancia a los datos recientes.
- Triple SMA (Triple Simple Moving Average): Utiliza tres medias móviles de diferentes
  períodos para identificar tendencias más robustas y filtrar señales falsas.
- Bollinger Bands: Consiste en una media móvil central y dos bandas de desviación estándar,
  útil para identificar volatilidad y posibles reversiones.
- Ichimoku Cloud: Sistema completo de análisis de tendencias que proporciona niveles de
  soporte/resistencia y señales de trading.
- ADX (Average Directional Index): Mide la fuerza de una tendencia independientemente
  de su dirección.

Los indicadores de tendencia son especialmente útiles en mercados direccionales,
donde pueden ayudar a identificar y seguir la tendencia predominante. A diferencia
de los osciladores, estos indicadores funcionan mejor en mercados con tendencia clara
y pueden generar señales falsas en mercados laterales o sin tendencia.

Características principales de los indicadores de tendencia:
- Suelen ser indicadores "retrasados" que confirman una tendencia después de que ha comenzado
- Ayudan a determinar la dirección y fuerza de una tendencia
- Pueden utilizarse para identificar soportes y resistencias dinámicos
- Funcionan mejor en combinación con otros tipos de indicadores (osciladores, volumen)
"""
import logging
import pandas as pd


class Trend:
    """
    Clase que implementa indicadores técnicos de tendencia.
    
    Esta clase proporciona métodos para calcular diversos indicadores de tendencia como
    MACD, SMA, EMA, WMA, Triple SMA, Bollinger Bands, Ichimoku Cloud y ADX, que ayudan
    a identificar la dirección y fuerza de la tendencia en el mercado. Los indicadores
    de tendencia son fundamentales para determinar si el mercado está en una fase
    alcista, bajista o lateral.
    
    Indicadores implementados:
    - MACD: Muestra la relación entre dos medias móviles exponenciales.
    - SMA: Calcula el precio promedio durante un período específico.
    - EMA: Media móvil exponencial que da más peso a los datos recientes.
    - WMA: Media móvil ponderada que asigna pesos linealmente decrecientes.
    - Triple SMA: Utiliza tres medias móviles de diferentes períodos.
    - Bollinger Bands: Media móvil con bandas de desviación estándar.
    - Ichimoku Cloud: Sistema completo de análisis de tendencias.
    - ADX: Mide la fuerza de una tendencia independientemente de su dirección.
    
    Los indicadores implementados en esta clase pueden utilizarse para:
    - Confirmar la dirección de la tendencia actual
    - Identificar posibles cambios de tendencia
    - Determinar la fuerza relativa de una tendencia
    - Generar señales de entrada y salida basadas en cruces de medias móviles
    - Filtrar señales falsas mediante la combinación de varios indicadores
    
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
        
        Desarrollado por Gerald Appel en los años 70, el MACD es uno de los indicadores
        técnicos más populares y versátiles. Combina elementos de seguimiento de tendencia
        y momentum en un solo indicador.
        
        Componentes del MACD:
        - Línea MACD: Diferencia entre la EMA rápida y la EMA lenta (EMA12 - EMA26 por defecto)
        - Línea de Señal: EMA de la línea MACD (EMA9 del MACD por defecto)
        - Histograma: Diferencia entre la línea MACD y la línea de Señal
        
        Interpretación:
        - Cruces: Cuando la línea MACD cruza por encima de la línea de Señal, se genera una
          señal alcista. Cuando cruza por debajo, se genera una señal bajista.
        - Divergencias: Cuando el precio forma nuevos máximos/mínimos pero el MACD no los
          confirma, puede indicar un posible cambio de tendencia.
        - Cruce de cero: Cuando la línea MACD cruza por encima de cero, indica momentum
          alcista. Cuando cruza por debajo, indica momentum bajista.
        
        Args:
            periodo_rapido: Período para la EMA rápida. Por defecto 12.
            periodo_lento: Período para la EMA lenta. Por defecto 26.
            periodo_senyal: Período para la línea de señal (EMA del MACD). Por defecto 9.
            
        Returns:
            int: Señal de trading:
                 2: Señal de compra (cruce alcista: MACD cruza por encima de la línea de señal)
                 1: Señal de venta (cruce bajista: MACD cruza por debajo de la línea de señal)
                 0: Sin señal clara (no se detectan cruces)
                
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
            return 2
        elif ultimo_cruce_bajista:
            logging.info("MACD - Se detectó un cruce bajista.")
            return 1
        else:
            logging.info("MACD - No se detectaron cruces alcistas o bajistas.")
            return 0

    def sma(self, periodo: int = 20) -> int:
        """
        Calcula la tendencia utilizando la SMA (Simple Moving Average) y genera señales de trading.
        
        La SMA es un indicador de tendencia que calcula el precio promedio durante un período
        específico. Se utiliza para suavizar las fluctuaciones de precios y ayudar a identificar
        la dirección de la tendencia.
        
        La SMA es uno de los indicadores técnicos más antiguos y sencillos, pero sigue siendo
        muy efectivo. A diferencia de otros tipos de medias móviles (como la EMA), la SMA
        asigna el mismo peso a todos los precios del período.
        
        Cálculo:
        SMA = (P₁ + P₂ + ... + Pₙ) / n
        donde P son los precios y n es el número de períodos.
        
        Interpretación:
        - Cuando el precio cruza por encima de la SMA, puede indicar el inicio de una tendencia alcista
        - Cuando el precio cruza por debajo de la SMA, puede indicar el inicio de una tendencia bajista
        - La SMA también puede actuar como soporte (en tendencias alcistas) o resistencia (en tendencias bajistas)
        - SMAs de períodos más cortos reaccionan más rápido a los cambios de precio pero generan más señales falsas
        - SMAs de períodos más largos son más lentas pero más fiables para identificar la tendencia principal
        
        Args:
            periodo: Número de períodos para calcular la media móvil simple. Por defecto 20.
            
        Returns:
            int: Señal de trading:
                 2: Señal de compra (tendencia alcista: precio por encima de la SMA)
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
            return 2  # Tendencia alcista
        else:
            logging.info("SMA - Tendencia bajista detectada.")
            return 1  # Tendencia bajista

    def ema(self, 
            periodo: int = 20, 
            mode: int = 0) -> int:
        """
        Calcula la Media Móvil Exponencial (EMA) y genera señales de trading.
        
        La EMA es similar a la SMA, pero da más peso a los datos recientes, lo que la hace
        más sensible a los cambios de precio recientes. Esto permite que la EMA reaccione
        más rápidamente a los cambios de tendencia que la SMA.
        
        La EMA se calcula utilizando la siguiente fórmula:
        EMA = Precio actual * k + EMA anterior * (1 - k)
        donde k = 2 / (periodo + 1)
        
        Interpretación:
        - Cuando el precio cruza por encima de la EMA: Señal alcista
        - Cuando el precio cruza por debajo de la EMA: Señal bajista
        - Cuando la EMA de período corto cruza por encima de la EMA de período largo: Señal alcista
        - Cuando la EMA de período corto cruza por debajo de la EMA de período largo: Señal bajista
        - La pendiente de la EMA indica la dirección de la tendencia
        
        Args:
            periodo: Número de períodos para calcular la EMA. Por defecto 20.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Señales basadas en cruces del precio con la EMA
                  1: Señales basadas en la pendiente de la EMA
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene la columna 'close'.
        """
        # Validar que el DataFrame tenga la columna 'close'.
        if 'close' not in self.df.columns:
            logging.error("EMA - El DataFrame no contiene la columna 'close'.")
            raise ValueError("El DataFrame debe contener una columna 'close' para calcular la EMA.")
        
        # Calcular la EMA
        self.df['ema'] = self.df['close'].ewm(span=periodo, adjust=False).mean()
        
        # Calcular la EMA anterior para detectar la pendiente
        self.df['ema_prev'] = self.df['ema'].shift(1)
        
        # Detectar cruces del precio con la EMA
        self.df['price_above_ema'] = self.df['close'] > self.df['ema']
        self.df['price_above_ema_prev'] = self.df['close'].shift(1) > self.df['ema_prev']
        
        self.df['price_cross_ema_up'] = (self.df['price_above_ema']) & (~self.df['price_above_ema_prev'])
        self.df['price_cross_ema_down'] = (~self.df['price_above_ema']) & (self.df['price_above_ema_prev'])
        
        # Calcular la pendiente de la EMA
        self.df['ema_slope'] = self.df['ema'] - self.df['ema_prev']
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en cruces del precio con la EMA
            if self.df['price_cross_ema_up'].iloc[-1]:
                return 2  # Señal de compra (precio cruza por encima de la EMA)
            elif self.df['price_cross_ema_down'].iloc[-1]:
                return 1  # Señal de venta (precio cruza por debajo de la EMA)
            else:
                return 0  # Sin señal clara
        
        elif mode == 1:
            # Basado en la pendiente de la EMA
            if self.df['ema_slope'].iloc[-1] > 0:
                return 2  # Señal de compra (pendiente positiva)
            elif self.df['ema_slope'].iloc[-1] < 0:
                return 1  # Señal de venta (pendiente negativa)
            else:
                return 0  # Sin señal clara
        
        return 0  # Sin señal clara
    
    def wma(self, 
           periodo: int = 20, 
           mode: int = 0) -> int:
        """
        Calcula la Media Móvil Ponderada (WMA) y genera señales de trading.
        
        La WMA asigna pesos linealmente decrecientes a los precios, dando más importancia
        a los datos recientes. A diferencia de la EMA, que asigna pesos exponencialmente
        decrecientes, la WMA asigna pesos de forma lineal.
        
        La WMA se calcula utilizando la siguiente fórmula:
        WMA = (P1*n + P2*(n-1) + ... + Pn*1) / (n + (n-1) + ... + 1)
        donde:
        - P1, P2, ..., Pn son los precios
        - n es el período
        
        Interpretación:
        - Cuando el precio cruza por encima de la WMA: Señal alcista
        - Cuando el precio cruza por debajo de la WMA: Señal bajista
        - Cuando la WMA de período corto cruza por encima de la WMA de período largo: Señal alcista
        - Cuando la WMA de período corto cruza por debajo de la WMA de período largo: Señal bajista
        - La pendiente de la WMA indica la dirección de la tendencia
        
        Args:
            periodo: Número de períodos para calcular la WMA. Por defecto 20.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Señales basadas en cruces del precio con la WMA
                  1: Señales basadas en la pendiente de la WMA
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene la columna 'close'.
        """
        # Validar que el DataFrame tenga la columna 'close'.
        if 'close' not in self.df.columns:
            logging.error("WMA - El DataFrame no contiene la columna 'close'.")
            raise ValueError("El DataFrame debe contener una columna 'close' para calcular la WMA.")
        
        # Calcular la WMA
        # Crear una función para calcular la WMA
        def calculate_wma(data, period):
            weights = list(range(1, period + 1))
            wma = data.rolling(window=period).apply(lambda x: sum(weights * x) / sum(weights), raw=True)
            return wma
        
        self.df['wma'] = calculate_wma(self.df['close'], periodo)
        
        # Calcular la WMA anterior para detectar la pendiente
        self.df['wma_prev'] = self.df['wma'].shift(1)
        
        # Detectar cruces del precio con la WMA
        self.df['price_above_wma'] = self.df['close'] > self.df['wma']
        self.df['price_above_wma_prev'] = self.df['close'].shift(1) > self.df['wma_prev']
        
        self.df['price_cross_wma_up'] = (self.df['price_above_wma']) & (~self.df['price_above_wma_prev'])
        self.df['price_cross_wma_down'] = (~self.df['price_above_wma']) & (self.df['price_above_wma_prev'])
        
        # Calcular la pendiente de la WMA
        self.df['wma_slope'] = self.df['wma'] - self.df['wma_prev']
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en cruces del precio con la WMA
            if self.df['price_cross_wma_up'].iloc[-1]:
                return 2  # Señal de compra (precio cruza por encima de la WMA)
            elif self.df['price_cross_wma_down'].iloc[-1]:
                return 1  # Señal de venta (precio cruza por debajo de la WMA)
            else:
                return 0  # Sin señal clara
        
        elif mode == 1:
            # Basado en la pendiente de la WMA
            if self.df['wma_slope'].iloc[-1] > 0:
                return 2  # Señal de compra (pendiente positiva)
            elif self.df['wma_slope'].iloc[-1] < 0:
                return 1  # Señal de venta (pendiente negativa)
            else:
                return 0  # Sin señal clara
        
        return 0  # Sin señal clara
    
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
        
        Este enfoque es una extensión del sistema de doble media móvil, pero añade una tercera
        media móvil para confirmar la tendencia y reducir las señales falsas. La Triple SMA
        es especialmente útil en mercados volátiles donde una sola media móvil podría generar
        demasiadas señales falsas.
        
        Componentes:
        - SMA Rápida: Reacciona más rápidamente a los cambios de precio (período corto)
        - SMA Media: Actúa como filtro intermedio (período medio)
        - SMA Lenta: Identifica la tendencia principal (período largo)
        
        Interpretación:
        - Alineación Alcista: SMA Rápida > SMA Media > SMA Lenta (señal de compra)
        - Alineación Bajista: SMA Rápida < SMA Media < SMA Lenta (señal de venta)
        - Cuando la SMA Rápida cambia de dirección respecto a la SMA Media, puede indicar
          un posible fin de tendencia o una corrección temporal
        
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
                 0: Sin señal clara
                 
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
                return 0

        if mode == 1:
            if ultimo_caida_rapido_respecto_medio or alineacion_bajista:
                return 1
            if ultima_subida_rapido_respecto_medio or alineacion_alcista:
                return 2
            else:
                return 0
                
        # Si llegamos aquí, es porque no se ha especificado un modo válido
        logging.warning("TRIPLE SMA - Modo no válido especificado. Se devuelve 0 (sin señal clara).")
        return 0
        
    def bollinger_bands(self, 
                       periodo: int = 20, 
                       desviaciones: float = 2.0, 
                       mode: int = 0) -> int:
        """
        Calcula las Bandas de Bollinger y genera señales de trading.
        
        Las Bandas de Bollinger, desarrolladas por John Bollinger, consisten en una media móvil
        central y dos bandas de desviación estándar, una superior y otra inferior. Son útiles
        para identificar volatilidad, sobrecompra/sobreventa y posibles reversiones.
        
        Las Bandas de Bollinger se calculan de la siguiente manera:
        - Banda Media: SMA del precio de cierre durante n períodos
        - Banda Superior: Banda Media + (Desviación Estándar * k)
        - Banda Inferior: Banda Media - (Desviación Estándar * k)
        
        donde:
        - n es el período (típicamente 20)
        - k es el número de desviaciones estándar (típicamente 2)
        
        Interpretación:
        - Cuando el precio toca o cruza la banda superior: Posible sobrecompra
        - Cuando el precio toca o cruza la banda inferior: Posible sobreventa
        - Estrechamiento de las bandas (baja volatilidad): Posible movimiento fuerte próximo
        - Ensanchamiento de las bandas (alta volatilidad): Posible continuación de la tendencia
        - El precio tiende a volver a la banda media después de tocar las bandas exteriores
        
        Args:
            periodo: Número de períodos para calcular la SMA y la desviación estándar. Por defecto 20.
            desviaciones: Número de desviaciones estándar para las bandas superior e inferior. Por defecto 2.0.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Señales basadas en toques/cruces de las bandas
                  1: Señales basadas en el ancho de las bandas (volatilidad)
                  2: Señales basadas en el %B (posición relativa dentro de las bandas)
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene la columna 'close'.
        """
        # Validar que el DataFrame tenga la columna 'close'.
        if 'close' not in self.df.columns:
            logging.error("BOLLINGER BANDS - El DataFrame no contiene la columna 'close'.")
            raise ValueError("El DataFrame debe contener una columna 'close' para calcular las Bandas de Bollinger.")
        
        # Calcular la media móvil simple (banda media)
        self.df['bb_media'] = self.df['close'].rolling(window=periodo).mean()
        
        # Calcular la desviación estándar
        self.df['bb_std'] = self.df['close'].rolling(window=periodo).std()
        
        # Calcular las bandas superior e inferior
        self.df['bb_superior'] = self.df['bb_media'] + (self.df['bb_std'] * desviaciones)
        self.df['bb_inferior'] = self.df['bb_media'] - (self.df['bb_std'] * desviaciones)
        
        # Calcular el ancho de las bandas (indicador de volatilidad)
        self.df['bb_ancho'] = (self.df['bb_superior'] - self.df['bb_inferior']) / self.df['bb_media']
        
        # Calcular el %B (posición relativa dentro de las bandas)
        self.df['bb_percent_b'] = (self.df['close'] - self.df['bb_inferior']) / (self.df['bb_superior'] - self.df['bb_inferior'])
        
        # Detectar toques/cruces de las bandas
        self.df['toca_banda_superior'] = self.df['close'] >= self.df['bb_superior']
        self.df['toca_banda_inferior'] = self.df['close'] <= self.df['bb_inferior']
        
        # Detectar cuando el precio vuelve dentro de las bandas después de tocarlas
        self.df['retorno_desde_superior'] = (self.df['close'] < self.df['bb_superior']) & (self.df['close'].shift(1) >= self.df['bb_superior'].shift(1))
        self.df['retorno_desde_inferior'] = (self.df['close'] > self.df['bb_inferior']) & (self.df['close'].shift(1) <= self.df['bb_inferior'].shift(1))
        
        # Detectar estrechamiento y ensanchamiento de las bandas
        self.df['bb_ancho_prev'] = self.df['bb_ancho'].shift(1)
        self.df['estrechamiento'] = self.df['bb_ancho'] < self.df['bb_ancho_prev']
        self.df['ensanchamiento'] = self.df['bb_ancho'] > self.df['bb_ancho_prev']
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en toques/cruces de las bandas
            if self.df['retorno_desde_inferior'].iloc[-1]:
                return 2  # Señal de compra (precio vuelve dentro desde la banda inferior)
            elif self.df['retorno_desde_superior'].iloc[-1]:
                return 1  # Señal de venta (precio vuelve dentro desde la banda superior)
            else:
                return 0  # Sin señal clara
        
        elif mode == 1:
            # Basado en el ancho de las bandas (volatilidad)
            # Estrechamiento seguido de ensanchamiento puede indicar inicio de tendencia
            if self.df['ensanchamiento'].iloc[-1] and self.df['estrechamiento'].iloc[-2]:
                # Determinar dirección basada en la posición del precio respecto a la banda media
                if self.df['close'].iloc[-1] > self.df['bb_media'].iloc[-1]:
                    return 2  # Señal de compra (posible inicio de tendencia alcista)
                elif self.df['close'].iloc[-1] < self.df['bb_media'].iloc[-1]:
                    return 1  # Señal de venta (posible inicio de tendencia bajista)
            return 0  # Sin señal clara
        
        elif mode == 2:
            # Basado en el %B (posición relativa dentro de las bandas)
            # %B > 1: Sobrecompra, %B < 0: Sobreventa, 0 < %B < 1: Dentro de las bandas
            if self.df['bb_percent_b'].iloc[-1] < 0 and self.df['bb_percent_b'].iloc[-2] < 0 and self.df['bb_percent_b'].iloc[-1] > self.df['bb_percent_b'].iloc[-2]:
                return 2  # Señal de compra (recuperación desde sobreventa)
            elif self.df['bb_percent_b'].iloc[-1] > 1 and self.df['bb_percent_b'].iloc[-2] > 1 and self.df['bb_percent_b'].iloc[-1] < self.df['bb_percent_b'].iloc[-2]:
                return 1  # Señal de venta (caída desde sobrecompra)
            else:
                return 0  # Sin señal clara
        
        return 0  # Sin señal clara
        
    def ichimoku_cloud(self, 
                      tenkan_period: int = 9, 
                      kijun_period: int = 26, 
                      senkou_span_b_period: int = 52, 
                      displacement: int = 26, 
                      mode: int = 0) -> int:
        """
        Calcula el Ichimoku Cloud (Ichimoku Kinko Hyo) y genera señales de trading.
        
        El Ichimoku Cloud es un sistema completo de análisis técnico desarrollado por Goichi Hosoda
        en Japón. Proporciona información sobre niveles de soporte/resistencia, dirección de la
        tendencia, momentum y señales de trading.
        
        Componentes del Ichimoku Cloud:
        - Tenkan-sen (Línea de Conversión): (Máximo(n) + Mínimo(n)) / 2, donde n = tenkan_period
        - Kijun-sen (Línea Base): (Máximo(n) + Mínimo(n)) / 2, donde n = kijun_period
        - Senkou Span A (Nube Adelantada A): (Tenkan-sen + Kijun-sen) / 2, desplazada displacement períodos
        - Senkou Span B (Nube Adelantada B): (Máximo(n) + Mínimo(n)) / 2, donde n = senkou_span_b_period, desplazada displacement períodos
        - Chikou Span (Línea de Retraso): Precio de cierre desplazado -displacement períodos
        
        Interpretación:
        - Cuando el precio está por encima de la nube: Tendencia alcista
        - Cuando el precio está por debajo de la nube: Tendencia bajista
        - Cuando el precio está dentro de la nube: Sin tendencia clara (consolidación)
        - Cuando Tenkan-sen cruza por encima de Kijun-sen: Señal alcista
        - Cuando Tenkan-sen cruza por debajo de Kijun-sen: Señal bajista
        - El color de la nube también indica la tendencia (verde/rojo)
        
        Args:
            tenkan_period: Período para calcular Tenkan-sen. Por defecto 9.
            kijun_period: Período para calcular Kijun-sen. Por defecto 26.
            senkou_span_b_period: Período para calcular Senkou Span B. Por defecto 52.
            displacement: Períodos de desplazamiento para Senkou Spans y Chikou Span. Por defecto 26.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Señales basadas en cruces de Tenkan-sen y Kijun-sen
                  1: Señales basadas en la posición del precio respecto a la nube
                  2: Señales basadas en la combinación de múltiples factores
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene las columnas necesarias.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if not {'high', 'low', 'close'}.issubset(self.df.columns):
            logging.error("ICHIMOKU CLOUD - El DataFrame no contiene las columnas 'high', 'low' y/o 'close'.")
            raise ValueError("El DataFrame debe contener columnas 'high', 'low' y 'close' para calcular el Ichimoku Cloud.")
        
        # Calcular Tenkan-sen (Línea de Conversión)
        self.df['tenkan_sen'] = (self.df['high'].rolling(window=tenkan_period).max() + 
                                self.df['low'].rolling(window=tenkan_period).min()) / 2
        
        # Calcular Kijun-sen (Línea Base)
        self.df['kijun_sen'] = (self.df['high'].rolling(window=kijun_period).max() + 
                               self.df['low'].rolling(window=kijun_period).min()) / 2
        
        # Calcular Senkou Span A (Nube Adelantada A)
        self.df['senkou_span_a'] = ((self.df['tenkan_sen'] + self.df['kijun_sen']) / 2).shift(displacement)
        
        # Calcular Senkou Span B (Nube Adelantada B)
        self.df['senkou_span_b'] = ((self.df['high'].rolling(window=senkou_span_b_period).max() + 
                                    self.df['low'].rolling(window=senkou_span_b_period).min()) / 2).shift(displacement)
        
        # Calcular Chikou Span (Línea de Retraso)
        self.df['chikou_span'] = self.df['close'].shift(-displacement)
        
        # Detectar cruces de Tenkan-sen y Kijun-sen
        self.df['tenkan_kijun_cross_up'] = (self.df['tenkan_sen'] > self.df['kijun_sen']) & (self.df['tenkan_sen'].shift(1) <= self.df['kijun_sen'].shift(1))
        self.df['tenkan_kijun_cross_down'] = (self.df['tenkan_sen'] < self.df['kijun_sen']) & (self.df['tenkan_sen'].shift(1) >= self.df['kijun_sen'].shift(1))
        
        # Detectar posición del precio respecto a la nube
        self.df['price_above_cloud'] = (self.df['close'] > self.df['senkou_span_a']) & (self.df['close'] > self.df['senkou_span_b'])
        self.df['price_below_cloud'] = (self.df['close'] < self.df['senkou_span_a']) & (self.df['close'] < self.df['senkou_span_b'])
        self.df['price_in_cloud'] = ~(self.df['price_above_cloud'] | self.df['price_below_cloud'])
        
        # Detectar color de la nube (verde/rojo)
        self.df['green_cloud'] = self.df['senkou_span_a'] > self.df['senkou_span_b']
        self.df['red_cloud'] = self.df['senkou_span_a'] < self.df['senkou_span_b']
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en cruces de Tenkan-sen y Kijun-sen
            if self.df['tenkan_kijun_cross_up'].iloc[-1]:
                return 2  # Señal de compra (cruce alcista)
            elif self.df['tenkan_kijun_cross_down'].iloc[-1]:
                return 1  # Señal de venta (cruce bajista)
            else:
                return 0  # Sin señal clara
        
        elif mode == 1:
            # Basado en la posición del precio respecto a la nube
            if self.df['price_above_cloud'].iloc[-1] and self.df['price_in_cloud'].iloc[-2]:
                return 2  # Señal de compra (precio rompe por encima de la nube)
            elif self.df['price_below_cloud'].iloc[-1] and self.df['price_in_cloud'].iloc[-2]:
                return 1  # Señal de venta (precio rompe por debajo de la nube)
            else:
                return 0  # Sin señal clara
        
        elif mode == 2:
            # Basado en la combinación de múltiples factores
            # Señal alcista fuerte: Precio por encima de la nube + Nube verde + Tenkan-sen > Kijun-sen
            if (self.df['price_above_cloud'].iloc[-1] and 
                self.df['green_cloud'].iloc[-1] and 
                self.df['tenkan_sen'].iloc[-1] > self.df['kijun_sen'].iloc[-1]):
                return 2  # Señal de compra (señal alcista fuerte)
            
            # Señal bajista fuerte: Precio por debajo de la nube + Nube roja + Tenkan-sen < Kijun-sen
            elif (self.df['price_below_cloud'].iloc[-1] and 
                 self.df['red_cloud'].iloc[-1] and 
                 self.df['tenkan_sen'].iloc[-1] < self.df['kijun_sen'].iloc[-1]):
                return 1  # Señal de venta (señal bajista fuerte)
            else:
                return 0  # Sin señal clara
        
        return 0  # Sin señal clara
        
    def adx(self, 
           period: int = 14, 
           smooth_period: int = 14, 
           threshold: int = 25, 
           mode: int = 0) -> int:
        """
        Calcula el Average Directional Index (ADX) y genera señales de trading.
        
        El ADX, desarrollado por J. Welles Wilder, es un indicador que mide la fuerza de una
        tendencia independientemente de su dirección. Se utiliza junto con los indicadores
        direccionales positivo (DI+) y negativo (DI-) para determinar si hay una tendencia
        y su dirección.
        
        El ADX se calcula mediante los siguientes pasos:
        1. Calcular el True Range (TR)
        2. Calcular el Directional Movement (DM+ y DM-)
        3. Calcular el Directional Indicator (DI+ y DI-)
        4. Calcular el Directional Index (DX)
        5. Calcular el Average Directional Index (ADX) como media móvil del DX
        
        Interpretación:
        - ADX > 25: Tendencia fuerte (cuanto mayor sea el valor, más fuerte es la tendencia)
        - ADX < 20: Tendencia débil o mercado lateral
        - Cuando DI+ cruza por encima de DI-: Señal alcista
        - Cuando DI- cruza por encima de DI+: Señal bajista
        - ADX creciente: La tendencia se está fortaleciendo
        - ADX decreciente: La tendencia se está debilitando
        
        Args:
            period: Número de períodos para calcular DI+ y DI-. Por defecto 14.
            smooth_period: Número de períodos para suavizar el ADX. Por defecto 14.
            threshold: Umbral para considerar una tendencia como fuerte. Por defecto 25.
            mode: Modo de operación que determina cómo se generan las señales:
                  0: Señales basadas en cruces de DI+ y DI-
                  1: Señales basadas en el valor del ADX y la dirección de DI+/DI-
                  2: Señales basadas en la pendiente del ADX
                  Por defecto 0.
        
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra
                 1: Señal de venta
                 0: Sin señal clara
        
        Raises:
            ValueError: Si el DataFrame no contiene las columnas necesarias.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if not {'high', 'low', 'close'}.issubset(self.df.columns):
            logging.error("ADX - El DataFrame no contiene las columnas 'high', 'low' y/o 'close'.")
            raise ValueError("El DataFrame debe contener columnas 'high', 'low' y 'close' para calcular el ADX.")
        
        # Calcular True Range (TR)
        self.df['tr0'] = abs(self.df['high'] - self.df['low'])
        self.df['tr1'] = abs(self.df['high'] - self.df['close'].shift(1))
        self.df['tr2'] = abs(self.df['low'] - self.df['close'].shift(1))
        self.df['tr'] = self.df[['tr0', 'tr1', 'tr2']].max(axis=1)
        
        # Calcular Directional Movement (DM+ y DM-)
        self.df['up_move'] = self.df['high'] - self.df['high'].shift(1)
        self.df['down_move'] = self.df['low'].shift(1) - self.df['low']
        
        self.df['dm_plus'] = 0.0
        self.df.loc[(self.df['up_move'] > self.df['down_move']) & (self.df['up_move'] > 0), 'dm_plus'] = self.df['up_move']
        
        self.df['dm_minus'] = 0.0
        self.df.loc[(self.df['down_move'] > self.df['up_move']) & (self.df['down_move'] > 0), 'dm_minus'] = self.df['down_move']
        
        # Calcular Smoothed TR, DM+ y DM- (utilizando la técnica de Wilder)
        # Primero calculamos la suma inicial
        self.df['tr_sum'] = self.df['tr'].rolling(window=period).sum()
        self.df['dm_plus_sum'] = self.df['dm_plus'].rolling(window=period).sum()
        self.df['dm_minus_sum'] = self.df['dm_minus'].rolling(window=period).sum()
        
        # Luego aplicamos el suavizado de Wilder para el resto de los valores
        for i in range(period, len(self.df)):
            self.df.loc[self.df.index[i], 'tr_sum'] = self.df.loc[self.df.index[i-1], 'tr_sum'] - (self.df.loc[self.df.index[i-1], 'tr_sum'] / period) + self.df.loc[self.df.index[i], 'tr']
            self.df.loc[self.df.index[i], 'dm_plus_sum'] = self.df.loc[self.df.index[i-1], 'dm_plus_sum'] - (self.df.loc[self.df.index[i-1], 'dm_plus_sum'] / period) + self.df.loc[self.df.index[i], 'dm_plus']
            self.df.loc[self.df.index[i], 'dm_minus_sum'] = self.df.loc[self.df.index[i-1], 'dm_minus_sum'] - (self.df.loc[self.df.index[i-1], 'dm_minus_sum'] / period) + self.df.loc[self.df.index[i], 'dm_minus']
        
        # Calcular Directional Indicators (DI+ y DI-)
        self.df['di_plus'] = 100 * (self.df['dm_plus_sum'] / self.df['tr_sum'])
        self.df['di_minus'] = 100 * (self.df['dm_minus_sum'] / self.df['tr_sum'])
        
        # Calcular Directional Index (DX)
        self.df['dx'] = 100 * (abs(self.df['di_plus'] - self.df['di_minus']) / (self.df['di_plus'] + self.df['di_minus']))
        
        # Calcular Average Directional Index (ADX)
        self.df['adx'] = self.df['dx'].rolling(window=smooth_period).mean()
        
        # Detectar cruces de DI+ y DI-
        self.df['di_cross_up'] = (self.df['di_plus'] > self.df['di_minus']) & (self.df['di_plus'].shift(1) <= self.df['di_minus'].shift(1))
        self.df['di_cross_down'] = (self.df['di_plus'] < self.df['di_minus']) & (self.df['di_plus'].shift(1) >= self.df['di_minus'].shift(1))
        
        # Calcular la pendiente del ADX
        self.df['adx_prev'] = self.df['adx'].shift(1)
        self.df['adx_slope'] = self.df['adx'] - self.df['adx_prev']
        
        # Generar señales según el modo seleccionado
        if mode == 0:
            # Basado en cruces de DI+ y DI-
            if self.df['di_cross_up'].iloc[-1]:
                return 2  # Señal de compra (DI+ cruza por encima de DI-)
            elif self.df['di_cross_down'].iloc[-1]:
                return 1  # Señal de venta (DI- cruza por encima de DI+)
            else:
                return 0  # Sin señal clara
        
        elif mode == 1:
            # Basado en el valor del ADX y la dirección de DI+/DI-
            if self.df['adx'].iloc[-1] > threshold:
                if self.df['di_plus'].iloc[-1] > self.df['di_minus'].iloc[-1]:
                    return 2  # Señal de compra (tendencia alcista fuerte)
                elif self.df['di_minus'].iloc[-1] > self.df['di_plus'].iloc[-1]:
                    return 1  # Señal de venta (tendencia bajista fuerte)
            return 0  # Sin señal clara (tendencia débil o sin tendencia)
        
        elif mode == 2:
            # Basado en la pendiente del ADX
            if self.df['adx_slope'].iloc[-1] > 0 and self.df['adx'].iloc[-1] > threshold:
                if self.df['di_plus'].iloc[-1] > self.df['di_minus'].iloc[-1]:
                    return 2  # Señal de compra (tendencia alcista fortaleciendo)
                elif self.df['di_minus'].iloc[-1] > self.df['di_plus'].iloc[-1]:
                    return 1  # Señal de venta (tendencia bajista fortaleciendo)
            return 0  # Sin señal clara
        
        return 0  # Sin señal clara

