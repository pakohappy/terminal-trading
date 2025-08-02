# -*- coding: utf-8 -*-
"""
Módulo de indicadores técnicos basados en volumen.

Este módulo implementa indicadores técnicos que utilizan el volumen de operaciones 
para generar señales de trading. Los indicadores basados en volumen ayudan a confirmar 
tendencias, identificar posibles reversiones y evaluar la fuerza de los movimientos 
del mercado.

Indicadores implementados:
- On-Balance Volume (OBV): Acumula volumen en dirección de la tendencia del precio
- Volume Price Trend (VPT): Similar a OBV pero considera la magnitud del cambio de precio
- Chaikin Money Flow (CMF): Mide la presión de compra/venta durante un período
- Money Flow Index (MFI): Oscilador que combina precio y volumen (RSI con volumen)
- Ease of Movement (EOM): Relaciona el cambio de precio con el volumen
- Chaikin Oscillator: Combina acumulación/distribución con MACD para detectar cambios en la presión de compra/venta
- Volume Weighted Average Price (VWAP): Precio promedio ponderado por volumen, útil para determinar valor justo
"""
import logging
import pandas as pd
import numpy as np


class Volume:
    """
    Clase que implementa indicadores técnicos basados en volumen.
    
    Esta clase proporciona métodos para calcular indicadores que utilizan
    el volumen de operaciones para generar señales de trading y evaluar
    la fuerza de los movimientos del mercado.
    
    Indicadores implementados:
    - OBV (On-Balance Volume): Acumula volumen en dirección de la tendencia del precio.
    - VPT (Volume Price Trend): Similar a OBV pero considera la magnitud del cambio de precio.
    - CMF (Chaikin Money Flow): Mide la presión de compra/venta durante un período.
    - MFI (Money Flow Index): Oscilador que combina precio y volumen (RSI con volumen).
    - EOM (Ease of Movement): Relaciona el cambio de precio con el volumen.
    - Chaikin Oscillator: Combina acumulación/distribución con MACD para detectar cambios en la presión de compra/venta.
    - VWAP (Volume Weighted Average Price): Precio promedio ponderado por volumen, útil para determinar valor justo.
    
    Attributes:
        df (pd.DataFrame): DataFrame con los datos de precios y volumen. Debe contener
                          columnas 'open', 'high', 'low', 'close' y 'volume' para 
                          la mayoría de los indicadores.
    """
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa la clase con un DataFrame que contiene datos de precios y volumen.
        
        Args:
            df: DataFrame con datos de precios y volumen. Debe contener al menos
                columnas 'close' y 'volume' para la mayoría de los indicadores.
                Para algunos indicadores se requieren también 'open', 'high' y 'low'.
        """
        self.df = df
        
    def obv(self, mode: int = 0) -> int:
        """
        Calcula el indicador On-Balance Volume (OBV) y genera señales de trading.
        
        El OBV es un indicador acumulativo que suma el volumen en días alcistas y
        resta el volumen en días bajistas. Ayuda a confirmar tendencias de precios
        y detectar divergencias.
        
        Args:
            mode: Modo de operación que determina cómo se generan las señales:
                 0: Basado en la dirección del OBV (alcista/bajista)
                 1: Basado en divergencias entre precio y OBV
                 Por defecto 0.
                 
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra (OBV alcista o divergencia alcista)
                 1: Señal de venta (OBV bajista o divergencia bajista)
                 0: Sin señal clara
                 
        Raises:
            ValueError: Si el DataFrame no contiene las columnas 'close' y 'volume'.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if not {'close', 'volume'}.issubset(self.df.columns):
            logging.error("OBV - El DataFrame debe contener las columnas 'close' y 'volume'.")
            raise ValueError("El DataFrame debe contener las columnas 'close' y 'volume' para calcular el OBV.")
        
        # Crear una copia del DataFrame para no modificar el original
        df_temp = self.df.copy()
        
        # Calcular el cambio diario de precios
        df_temp['price_change'] = df_temp['close'].diff()
        
        # Inicializar el OBV
        df_temp['obv'] = 0
        
        # Calcular el OBV
        for i in range(1, len(df_temp)):
            if df_temp['price_change'].iloc[i] > 0:
                # Precio subió, sumar volumen
                df_temp.loc[df_temp.index[i], 'obv'] = df_temp['obv'].iloc[i-1] + df_temp['volume'].iloc[i]
            elif df_temp['price_change'].iloc[i] < 0:
                # Precio bajó, restar volumen
                df_temp.loc[df_temp.index[i], 'obv'] = df_temp['obv'].iloc[i-1] - df_temp['volume'].iloc[i]
            else:
                # Precio sin cambio, mantener OBV
                df_temp.loc[df_temp.index[i], 'obv'] = df_temp['obv'].iloc[i-1]
        
        # Añadir el OBV al DataFrame original
        self.df['obv'] = df_temp['obv']
        
        # Calcular la media móvil del OBV para determinar la tendencia
        self.df['obv_sma'] = self.df['obv'].rolling(window=14).mean()
        
        # Determinar si el OBV está en tendencia alcista o bajista
        obv_alcista = self.df['obv'].iloc[-1] > self.df['obv_sma'].iloc[-1]
        
        # Detectar divergencias
        # Divergencia alcista: precio hace mínimos más bajos pero OBV hace mínimos más altos
        precio_bajando = self.df['close'].iloc[-1] < self.df['close'].iloc[-2]
        obv_subiendo = self.df['obv'].iloc[-1] > self.df['obv'].iloc[-2]
        divergencia_alcista = precio_bajando and obv_subiendo
        
        # Divergencia bajista: precio hace máximos más altos pero OBV hace máximos más bajos
        precio_subiendo = self.df['close'].iloc[-1] > self.df['close'].iloc[-2]
        obv_bajando = self.df['obv'].iloc[-1] < self.df['obv'].iloc[-2]
        divergencia_bajista = precio_subiendo and obv_bajando
        
        # Generar señales según el modo
        if mode == 0:
            if obv_alcista:
                return 2  # Señal de compra
            else:
                return 1  # Señal de venta
        
        elif mode == 1:
            if divergencia_alcista:
                return 2  # Señal de compra
            elif divergencia_bajista:
                return 1  # Señal de venta
        
        return 0  # Sin señal clara
        
    def vpt(self, mode: int = 0) -> int:
        """
        Calcula el indicador Volume Price Trend (VPT) y genera señales de trading.
        
        El VPT es similar al OBV pero considera la magnitud del cambio de precio.
        Multiplica el volumen por el porcentaje de cambio en el precio para dar
        más peso a movimientos de precio más significativos.
        
        Args:
            mode: Modo de operación que determina cómo se generan las señales:
                 0: Basado en la dirección del VPT (alcista/bajista)
                 1: Basado en divergencias entre precio y VPT
                 Por defecto 0.
                 
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra (VPT alcista o divergencia alcista)
                 1: Señal de venta (VPT bajista o divergencia bajista)
                 0: Sin señal clara
                 
        Raises:
            ValueError: Si el DataFrame no contiene las columnas 'close' y 'volume'.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if not {'close', 'volume'}.issubset(self.df.columns):
            logging.error("VPT - El DataFrame debe contener las columnas 'close' y 'volume'.")
            raise ValueError("El DataFrame debe contener las columnas 'close' y 'volume' para calcular el VPT.")
        
        # Crear una copia del DataFrame para no modificar el original
        df_temp = self.df.copy()
        
        # Calcular el cambio porcentual diario de precios
        df_temp['price_pct_change'] = df_temp['close'].pct_change()
        
        # Calcular el VPT
        df_temp['vpt_change'] = df_temp['volume'] * df_temp['price_pct_change']
        df_temp['vpt'] = df_temp['vpt_change'].cumsum()
        
        # Añadir el VPT al DataFrame original
        self.df['vpt'] = df_temp['vpt']
        
        # Calcular la media móvil del VPT para determinar la tendencia
        self.df['vpt_sma'] = self.df['vpt'].rolling(window=14).mean()
        
        # Determinar si el VPT está en tendencia alcista o bajista
        vpt_alcista = self.df['vpt'].iloc[-1] > self.df['vpt_sma'].iloc[-1]
        
        # Detectar divergencias
        # Divergencia alcista: precio hace mínimos más bajos pero VPT hace mínimos más altos
        precio_bajando = self.df['close'].iloc[-1] < self.df['close'].iloc[-2]
        vpt_subiendo = self.df['vpt'].iloc[-1] > self.df['vpt'].iloc[-2]
        divergencia_alcista = precio_bajando and vpt_subiendo
        
        # Divergencia bajista: precio hace máximos más altos pero VPT hace máximos más bajos
        precio_subiendo = self.df['close'].iloc[-1] > self.df['close'].iloc[-2]
        vpt_bajando = self.df['vpt'].iloc[-1] < self.df['vpt'].iloc[-2]
        divergencia_bajista = precio_subiendo and vpt_bajando
        
        # Generar señales según el modo
        if mode == 0:
            if vpt_alcista:
                return 2  # Señal de compra
            else:
                return 1  # Señal de venta
        
        elif mode == 1:
            if divergencia_alcista:
                return 2  # Señal de compra
            elif divergencia_bajista:
                return 1  # Señal de venta
        
        return 0  # Sin señal clara
        
    def cmf(self, periodo: int = 20, mode: int = 0) -> int:
        """
        Calcula el indicador Chaikin Money Flow (CMF) y genera señales de trading.
        
        El CMF mide la presión de compra/venta durante un período específico.
        Combina el volumen con la posición de cierre relativa al rango de precios
        para determinar si el dinero está fluyendo hacia o desde un valor.
        
        Args:
            periodo: Número de períodos para calcular el CMF. Por defecto 20.
            mode: Modo de operación que determina cómo se generan las señales:
                 0: Basado en el cruce de la línea cero
                 1: Basado en niveles extremos (sobrecompra/sobreventa)
                 Por defecto 0.
                 
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra (CMF cruza por encima de cero o está en sobreventa)
                 1: Señal de venta (CMF cruza por debajo de cero o está en sobrecompra)
                 0: Sin señal clara
                 
        Raises:
            ValueError: Si el DataFrame no contiene las columnas necesarias.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if not {'high', 'low', 'close', 'volume'}.issubset(self.df.columns):
            logging.error("CMF - El DataFrame debe contener las columnas 'high', 'low', 'close' y 'volume'.")
            raise ValueError("El DataFrame debe contener las columnas 'high', 'low', 'close' y 'volume' para calcular el CMF.")
        
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
        
        # Calcular el Chaikin Money Flow (CMF)
        # CMF = Sum(MFV, periodo) / Sum(Volume, periodo)
        df_temp['cmf'] = df_temp['mfv'].rolling(window=periodo).sum() / df_temp['volume'].rolling(window=periodo).sum()
        
        # Añadir el CMF al DataFrame original
        self.df['cmf'] = df_temp['cmf']
        
        # Detectar cruces de la línea cero
        self.df['cmf_cruce_alcista'] = (self.df['cmf'].shift(1) < 0) & (self.df['cmf'] > 0)
        self.df['cmf_cruce_bajista'] = (self.df['cmf'].shift(1) > 0) & (self.df['cmf'] < 0)
        
        # Detectar niveles extremos (sobrecompra/sobreventa)
        # Valores típicos: sobrecompra > 0.25, sobreventa < -0.25
        self.df['cmf_sobrecompra'] = self.df['cmf'] > 0.25
        self.df['cmf_sobreventa'] = self.df['cmf'] < -0.25
        
        # Obtener los últimos valores
        ultimo_cruce_alcista = self.df['cmf_cruce_alcista'].iloc[-1]
        ultimo_cruce_bajista = self.df['cmf_cruce_bajista'].iloc[-1]
        ultima_sobrecompra = self.df['cmf_sobrecompra'].iloc[-1]
        ultima_sobreventa = self.df['cmf_sobreventa'].iloc[-1]
        
        # Generar señales según el modo
        if mode == 0:
            if ultimo_cruce_alcista:
                return 2  # Señal de compra
            elif ultimo_cruce_bajista:
                return 1  # Señal de venta
        
        elif mode == 1:
            if ultima_sobreventa:
                return 2  # Señal de compra
            elif ultima_sobrecompra:
                return 1  # Señal de venta
        
        return 0  # Sin señal clara
        
    def mfi(self, periodo: int = 14, overbought_level: int = 80, oversold_level: int = 20) -> int:
        """
        Calcula el indicador Money Flow Index (MFI) y genera señales de trading.
        
        El MFI es un oscilador que combina precio y volumen, similar al RSI pero
        incorporando el volumen. Mide la presión de compra y venta en un rango de 0 a 100,
        donde valores por encima de 80 indican sobrecompra y por debajo de 20 indican sobreventa.
        
        Args:
            periodo: Número de períodos para calcular el MFI. Por defecto 14.
            overbought_level: Nivel de sobrecompra. Por defecto 80.
            oversold_level: Nivel de sobreventa. Por defecto 20.
                 
        Returns:
            int: Señal de trading:
                 2: Señal de compra (MFI en zona de sobreventa)
                 1: Señal de venta (MFI en zona de sobrecompra)
                 0: Sin señal clara
                 
        Raises:
            ValueError: Si el DataFrame no contiene las columnas necesarias.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if not {'high', 'low', 'close', 'volume'}.issubset(self.df.columns):
            logging.error("MFI - El DataFrame debe contener las columnas 'high', 'low', 'close' y 'volume'.")
            raise ValueError("El DataFrame debe contener las columnas 'high', 'low', 'close' y 'volume' para calcular el MFI.")
        
        # Crear una copia del DataFrame para no modificar el original
        df_temp = self.df.copy()
        
        # Calcular el precio típico
        df_temp['precio_tipico'] = (df_temp['high'] + df_temp['low'] + df_temp['close']) / 3
        
        # Calcular el Raw Money Flow
        df_temp['raw_money_flow'] = df_temp['precio_tipico'] * df_temp['volume']
        
        # Determinar si el precio típico subió o bajó
        df_temp['precio_tipico_anterior'] = df_temp['precio_tipico'].shift(1)
        df_temp['precio_subio'] = df_temp['precio_tipico'] > df_temp['precio_tipico_anterior']
        df_temp['precio_bajo'] = df_temp['precio_tipico'] < df_temp['precio_tipico_anterior']
        
        # Calcular el Positive Money Flow y Negative Money Flow
        df_temp['positive_money_flow'] = np.where(df_temp['precio_subio'], df_temp['raw_money_flow'], 0)
        df_temp['negative_money_flow'] = np.where(df_temp['precio_bajo'], df_temp['raw_money_flow'], 0)
        
        # Calcular la suma de los flujos positivos y negativos durante el período
        df_temp['positive_money_flow_sum'] = df_temp['positive_money_flow'].rolling(window=periodo).sum()
        df_temp['negative_money_flow_sum'] = df_temp['negative_money_flow'].rolling(window=periodo).sum()
        
        # Calcular el Money Ratio
        df_temp['money_ratio'] = df_temp['positive_money_flow_sum'] / df_temp['negative_money_flow_sum']
        
        # Calcular el Money Flow Index
        df_temp['mfi'] = 100 - (100 / (1 + df_temp['money_ratio']))
        
        # Añadir el MFI al DataFrame original
        self.df['mfi'] = df_temp['mfi']
        
        # Detectar condiciones de sobrecompra y sobreventa
        self.df['mfi_sobrecompra'] = self.df['mfi'] > overbought_level
        self.df['mfi_sobreventa'] = self.df['mfi'] < oversold_level
        
        # Obtener los últimos valores
        ultima_sobrecompra = self.df['mfi_sobrecompra'].iloc[-1]
        ultima_sobreventa = self.df['mfi_sobreventa'].iloc[-1]
        
        # Generar señales
        if ultima_sobreventa:
            return 2  # Señal de compra
        elif ultima_sobrecompra:
            return 1  # Señal de venta
        
        return 0  # Sin señal clara
        
    def eom(self, periodo: int = 14, ema_periodo: int = 14, mode: int = 0) -> int:
        """
        Calcula el indicador Ease of Movement (EOM) y genera señales de trading.
        
        El EOM relaciona el cambio de precio con el volumen, midiendo la "facilidad"
        con la que el precio se mueve. Valores positivos indican que el precio sube
        fácilmente (con poco volumen), mientras que valores negativos indican que
        el precio baja fácilmente.
        
        Args:
            periodo: Número de períodos para calcular el EOM. Por defecto 14.
            ema_periodo: Número de períodos para la media móvil del EOM. Por defecto 14.
            mode: Modo de operación que determina cómo se generan las señales:
                 0: Basado en el cruce de la línea cero
                 1: Basado en divergencias entre precio y EOM
                 Por defecto 0.
                 
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra (EOM cruza por encima de cero o divergencia alcista)
                 1: Señal de venta (EOM cruza por debajo de cero o divergencia bajista)
                 0: Sin señal clara
                 
        Raises:
            ValueError: Si el DataFrame no contiene las columnas necesarias.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if not {'high', 'low', 'volume'}.issubset(self.df.columns):
            logging.error("EOM - El DataFrame debe contener las columnas 'high', 'low' y 'volume'.")
            raise ValueError("El DataFrame debe contener las columnas 'high', 'low' y 'volume' para calcular el EOM.")
        
        # Crear una copia del DataFrame para no modificar el original
        df_temp = self.df.copy()
        
        # Calcular el punto medio del rango de precios
        df_temp['midpoint_move'] = ((df_temp['high'] + df_temp['low']) / 2) - ((df_temp['high'].shift(1) + df_temp['low'].shift(1)) / 2)
        
        # Calcular el Box Ratio
        df_temp['box_ratio'] = (df_temp['volume'] / 100000000) / (df_temp['high'] - df_temp['low'])
        
        # Calcular el EOM de un período
        df_temp['eom_1period'] = df_temp['midpoint_move'] / df_temp['box_ratio']
        
        # Calcular el EOM para el período especificado (media móvil)
        df_temp['eom'] = df_temp['eom_1period'].rolling(window=periodo).mean()
        
        # Calcular la EMA del EOM
        df_temp['eom_ema'] = df_temp['eom'].ewm(span=ema_periodo, adjust=False).mean()
        
        # Añadir el EOM al DataFrame original
        self.df['eom'] = df_temp['eom']
        self.df['eom_ema'] = df_temp['eom_ema']
        
        # Detectar cruces de la línea cero
        self.df['eom_cruce_alcista'] = (self.df['eom'].shift(1) < 0) & (self.df['eom'] > 0)
        self.df['eom_cruce_bajista'] = (self.df['eom'].shift(1) > 0) & (self.df['eom'] < 0)
        
        # Detectar divergencias
        # Divergencia alcista: precio hace mínimos más bajos pero EOM hace mínimos más altos
        precio_bajando = self.df['low'].iloc[-1] < self.df['low'].iloc[-2]
        eom_subiendo = self.df['eom'].iloc[-1] > self.df['eom'].iloc[-2]
        divergencia_alcista = precio_bajando and eom_subiendo
        
        # Divergencia bajista: precio hace máximos más altos pero EOM hace máximos más bajos
        precio_subiendo = self.df['high'].iloc[-1] > self.df['high'].iloc[-2]
        eom_bajando = self.df['eom'].iloc[-1] < self.df['eom'].iloc[-2]
        divergencia_bajista = precio_subiendo and eom_bajando
        
        # Obtener los últimos valores
        ultimo_cruce_alcista = self.df['eom_cruce_alcista'].iloc[-1]
        ultimo_cruce_bajista = self.df['eom_cruce_bajista'].iloc[-1]
        
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
        
        
    def vwap(self, mode: int = 0) -> int:
        """
        Calcula el Volume Weighted Average Price (VWAP) y genera señales de trading.
        
        El VWAP es un indicador que calcula el precio promedio ponderado por volumen
        durante un período específico, generalmente un día de trading. Es útil para
        determinar el precio "justo" o valor de consenso del mercado.
        
        El VWAP se calcula como:
        VWAP = Σ(Precio típico * Volumen) / Σ(Volumen)
        donde Precio típico = (Alto + Bajo + Cierre) / 3
        
        Args:
            mode: Modo de operación que determina cómo se generan las señales:
                 0: Basado en la posición del precio respecto al VWAP
                 1: Basado en cruces del precio con el VWAP
                 Por defecto 0.
                 
        Returns:
            int: Señal de trading según el modo seleccionado:
                 2: Señal de compra (precio por debajo del VWAP o cruce alcista)
                 1: Señal de venta (precio por encima del VWAP o cruce bajista)
                 0: Sin señal clara
                 
        Raises:
            ValueError: Si el DataFrame no contiene las columnas necesarias.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if not {'high', 'low', 'close', 'volume'}.issubset(self.df.columns):
            logging.error("VWAP - El DataFrame debe contener las columnas 'high', 'low', 'close' y 'volume'.")
            raise ValueError("El DataFrame debe contener las columnas 'high', 'low', 'close' y 'volume' para calcular el VWAP.")
        
        # Crear una copia del DataFrame para no modificar el original
        df_temp = self.df.copy()
        
        # Calcular el precio típico
        df_temp['precio_tipico'] = (df_temp['high'] + df_temp['low'] + df_temp['close']) / 3
        
        # Calcular el precio típico ponderado por volumen
        df_temp['precio_tipico_ponderado'] = df_temp['precio_tipico'] * df_temp['volume']
        
        # Calcular el VWAP
        df_temp['vwap_numerador'] = df_temp['precio_tipico_ponderado'].cumsum()
        df_temp['vwap_denominador'] = df_temp['volume'].cumsum()
        df_temp['vwap'] = df_temp['vwap_numerador'] / df_temp['vwap_denominador']
        
        # Añadir el VWAP al DataFrame original
        self.df['vwap'] = df_temp['vwap']
        
        # Detectar la posición del precio respecto al VWAP
        self.df['precio_sobre_vwap'] = self.df['close'] > self.df['vwap']
        
        # Detectar cruces del precio con el VWAP
        self.df['precio_sobre_vwap_prev'] = self.df['precio_sobre_vwap'].shift(1)
        # Usar operadores lógicos not y and en lugar del operador ~ para evitar problemas con NaN
        self.df['cruce_alcista_vwap'] = (self.df['precio_sobre_vwap_prev'] == False) & (self.df['precio_sobre_vwap'] == True)
        self.df['cruce_bajista_vwap'] = (self.df['precio_sobre_vwap_prev'] == True) & (self.df['precio_sobre_vwap'] == False)
        
        # Obtener los últimos valores
        ultimo_precio_sobre_vwap = self.df['precio_sobre_vwap'].iloc[-1]
        ultimo_cruce_alcista = self.df['cruce_alcista_vwap'].iloc[-1]
        ultimo_cruce_bajista = self.df['cruce_bajista_vwap'].iloc[-1]
        
        # Generar señales según el modo
        if mode == 0:
            # Basado en la posición del precio respecto al VWAP
            if not ultimo_precio_sobre_vwap:
                return 2  # Señal de compra (precio por debajo del VWAP, posible valor de compra)
            else:
                return 1  # Señal de venta (precio por encima del VWAP, posible valor de venta)
        
        elif mode == 1:
            # Basado en cruces del precio con el VWAP
            if ultimo_cruce_alcista:
                return 2  # Señal de compra (precio cruza por encima del VWAP)
            elif ultimo_cruce_bajista:
                return 1  # Señal de venta (precio cruza por debajo del VWAP)
        
        return 0  # Sin señal clara