# -*- coding: utf-8 -*-
"""
Robot de Trading con Triple SMA: Implementación de estrategia basada en Triple SMA

Este robot implementa una estrategia de trading basada en el indicador Triple SMA (Triple Simple Moving Average),
que utiliza tres medias móviles simples con diferentes períodos para identificar tendencias en el mercado.
La estrategia busca oportunidades de compra cuando las medias móviles están alineadas en orden ascendente
(rápida > media > lenta) y oportunidades de venta cuando están alineadas en orden descendente
(rápida < media < lenta).
"""
import MetaTrader5 as mt5
import logging
from utils.base import RobotBase
from indicators.Trend import Trend
from trading_platform.Metaquotes import Metaquotes as mtq

class TripleSMARobot(RobotBase):
    """
    Robot de trading que implementa una estrategia basada en Triple SMA.
    
    Esta clase extiende RobotBase y define la estrategia específica basada en el
    indicador Triple SMA para generar señales de trading.
    
    Attributes:
        PERIODO_LENTO (int): Período para la media móvil lenta.
        PERIODO_MEDIO (int): Período para la media móvil media.
        PERIODO_RAPIDO (int): Período para la media móvil rápida.
        MODE (int): Modo de operación.
    """
    
    def __init__(self, 
                 symbol: str = 'BTCUSD', 
                 timeframe: int = mt5.TIMEFRAME_H1, 
                 volume: float = 0.01, 
                 last_candles: int = 20, 
                 pips_sl: int = 100000, 
                 pips_tp: int = 100000, 
                 deviation: int = 100, 
                 comment: str = "Triple SMA Robot Order",
                 periodo_lento: int = 8,
                 periodo_medio: int = 6,
                 periodo_rapido: int = 4,
                 mode: int = 0):
        """
        Inicializa un nuevo robot con estrategia basada en Triple SMA.
        
        Args:
            symbol: Par de divisas o instrumento a operar. Por defecto 'BTCUSD'.
            timeframe: Marco temporal para el análisis. Por defecto mt5.TIMEFRAME_H1.
            volume: Tamaño de la posición en lotes. Por defecto 0.01.
            last_candles: Número de velas a analizar. Por defecto 20.
            pips_sl: Stop Loss en pips. Por defecto 100000.
            pips_tp: Take Profit en pips. Por defecto 100000.
            deviation: Desviación máxima permitida del precio. Por defecto 100.
            comment: Comentario para identificar las órdenes. Por defecto "Triple SMA Robot Order".
            periodo_lento: Período para la media móvil lenta. Por defecto 8.
            periodo_medio: Período para la media móvil media. Por defecto 6.
            periodo_rapido: Período para la media móvil rápida. Por defecto 4.
            mode: Modo de operación. Por defecto 0.
        """
        super().__init__(symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment)
        
        # Parámetros específicos del indicador Triple SMA
        self.PERIODO_LENTO = periodo_lento
        self.PERIODO_MEDIO = periodo_medio
        self.PERIODO_RAPIDO = periodo_rapido
        self.MODE = mode
    
    def analyze_market(self, df):
        """
        Analiza el mercado utilizando el indicador Triple SMA y genera señales de trading.
        
        Args:
            df: DataFrame con los datos de mercado.
            
        Returns:
            int: Señal de trading (2 para compra, 1 para venta, 0 para no operar).
        """
        # Crear una instancia del indicador Trend y calcular el Triple SMA
        indicator = Trend(df)
        signal = indicator.triple_sma(
            self.PERIODO_LENTO, 
            self.PERIODO_MEDIO, 
            self.PERIODO_RAPIDO, 
            self.MODE
        )
        
        return signal
    
    def manage_positions(self, positions):
        """
        Gestiona las posiciones abiertas utilizando el indicador Triple SMA con modo 1 (fin de tendencia).
        
        Args:
            positions: Lista de posiciones abiertas.
        """
        for position in positions:
            # Obtener datos actualizados y calcular el indicador con modo 1 (fin de tendencia)
            df = self.get_market_data()
            indicator_close = Trend(df)
            signal_close = indicator_close.triple_sma(
                self.PERIODO_LENTO, 
                self.PERIODO_MEDIO, 
                self.PERIODO_RAPIDO, 
                1  # Modo 1 para detectar fin de tendencia
            )
            
            # Cerrar posiciones cuando la señal indica fin de tendencia
            # (compra -> señal de fin de tendencia alcista, venta -> señal de fin de tendencia bajista)
            if position.type == 0 and signal_close == 1 or position.type == 1 and signal_close == 2:
                mtq.close_position(position)
            else:
                logging.info(f"{self.__class__.__name__} - No hay signal que marque el cierre de la posición.")


# Punto de entrada del programa
if __name__ == "__main__":
    # Crear una instancia del robot y ejecutarlo
    robot = TripleSMARobot()
    robot.run()