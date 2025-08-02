# -*- coding: utf-8 -*-
"""
Robot de Trading con Estocástico: Implementación de estrategia basada en el Oscilador Estocástico

Este robot implementa una estrategia de trading basada en el indicador estocástico,
que es un oscilador que mide la posición del precio actual en relación con su rango
de precios durante un período determinado. El robot busca oportunidades de compra
cuando el estocástico sale de la zona de sobreventa y oportunidades de venta cuando
sale de la zona de sobrecompra.
"""
import MetaTrader5 as mt5
import logging
from utils.base import RobotBase
from indicators.Oscillator import Oscillator

class StochasticRobot(RobotBase):
    """
    Robot de trading que implementa una estrategia basada en el Oscilador Estocástico.
    
    Esta clase extiende RobotBase y define la estrategia específica basada en el
    indicador estocástico para generar señales de trading.
    
    Attributes:
        K_PERIOD (int): Período para calcular %K (línea principal).
        D_PERIOD (int): Período para calcular %D (línea de señal).
        SMOOTH_K (int): Suavizado de la línea %K.
        OVERBOUGHT_LEVEL (int): Nivel de sobrecompra.
        OVERSOLD_LEVEL (int): Nivel de sobreventa.
        MODE (int): Modo de operación.
    """
    
    def __init__(self, 
                 symbol: str = 'BTCUSD', 
                 timeframe: int = mt5.TIMEFRAME_M5, 
                 volume: float = 0.01, 
                 last_candles: int = 30, 
                 pips_sl: int = 50000, 
                 pips_tp: int = 50000, 
                 deviation: int = 100, 
                 comment: str = "Stochastic Robot Order",
                 k_period: int = 5,
                 d_period: int = 3,
                 smooth_k: int = 3,
                 overbought_level: int = 80,
                 oversold_level: int = 20,
                 mode: int = 0):
        """
        Inicializa un nuevo robot con estrategia basada en el Oscilador Estocástico.
        
        Args:
            symbol: Par de divisas o instrumento a operar. Por defecto 'BTCUSD'.
            timeframe: Marco temporal para el análisis. Por defecto mt5.TIMEFRAME_M5.
            volume: Tamaño de la posición en lotes. Por defecto 0.01.
            last_candles: Número de velas a analizar. Por defecto 30.
            pips_sl: Stop Loss en pips. Por defecto 50000.
            pips_tp: Take Profit en pips. Por defecto 50000.
            deviation: Desviación máxima permitida del precio. Por defecto 100.
            comment: Comentario para identificar las órdenes. Por defecto "Stochastic Robot Order".
            k_period: Período para calcular %K. Por defecto 5.
            d_period: Período para calcular %D. Por defecto 3.
            smooth_k: Suavizado de la línea %K. Por defecto 3.
            overbought_level: Nivel de sobrecompra. Por defecto 80.
            oversold_level: Nivel de sobreventa. Por defecto 20.
            mode: Modo de operación. Por defecto 0.
        """
        super().__init__(symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment)
        
        # Parámetros específicos del indicador estocástico
        self.K_PERIOD = k_period
        self.D_PERIOD = d_period
        self.SMOOTH_K = smooth_k
        self.OVERBOUGHT_LEVEL = overbought_level
        self.OVERSOLD_LEVEL = oversold_level
        self.MODE = mode
    
    def analyze_market(self, df):
        """
        Analiza el mercado utilizando el indicador estocástico y genera señales de trading.
        
        Args:
            df: DataFrame con los datos de mercado.
            
        Returns:
            int: Señal de trading (2 para compra, 1 para venta, 0 para no operar).
        """
        # Crear una instancia del indicador Oscillator y calcular el estocástico
        indicator = Oscillator(df)
        signal = indicator.stochastic(
            self.K_PERIOD, 
            self.D_PERIOD, 
            self.SMOOTH_K, 
            self.OVERBOUGHT_LEVEL, 
            self.OVERSOLD_LEVEL, 
            self.MODE
        )
        
        return signal
    
    def manage_positions(self, positions):
        """
        Gestiona las posiciones abiertas utilizando el indicador estocástico.
        
        Args:
            positions: Lista de posiciones abiertas.
        """
        if len(positions) == 1:
            for position in positions:
                # Obtener datos actualizados y calcular el indicador
                df = self.get_market_data()
                indicator = Oscillator(df)
                signal = indicator.stochastic(
                    self.K_PERIOD, 
                    self.D_PERIOD, 
                    self.SMOOTH_K, 
                    self.OVERBOUGHT_LEVEL, 
                    self.OVERSOLD_LEVEL, 
                    self.MODE
                )

                # Si la señal coincide con la posición actual, no hacer nada
                if position.type == 0 and signal == 2 or position.type == 1 and signal == 1:
                    logging.info(f"{self.__class__.__name__} - No hay señal para abrir una segunda posición.")

                # Si tenemos una posición de compra y hay señal de venta, abrir una posición de venta
                if position.type == 0 and signal == 1:
                    self.process_signal(signal)

                # Si tenemos una posición de venta y hay señal de compra, abrir una posición de compra
                if position.type == 1 and signal == 2:
                    self.process_signal(signal)
        else:
            # Comportamiento por defecto para múltiples posiciones
            super().manage_positions(positions)


# Punto de entrada del programa
if __name__ == "__main__":
    # Crear una instancia del robot y ejecutarlo
    robot = StochasticRobot()
    robot.run()