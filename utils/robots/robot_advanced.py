# -*- coding: utf-8 -*-
"""
Robot de Trading Avanzado: Implementación de estrategia avanzada con Triple SMA y Alligator

Este robot implementa una estrategia de trading avanzada que combina dos indicadores:
1. Triple SMA (Triple Simple Moving Average): Utiliza tres medias móviles simples con 
   diferentes períodos para identificar tendencias en el mercado.
2. Alligator (Bill Williams): Un indicador que utiliza tres medias móviles suavizadas 
   y desplazadas para identificar tendencias y momentos de "despertar" del mercado.

Aunque el robot importa ambos indicadores, actualmente solo utiliza el Triple SMA para
generar señales de trading. La implementación del Alligator está preparada para futuras
mejoras en la estrategia.
"""
import MetaTrader5 as mt5
from utils.base import RobotBase
from indicators.Trend import Trend
from indicators.BillWilliams import BillWilliams
from trading_platform.Metaquotes import Metaquotes as mtq

class AdvancedRobot(RobotBase):
    """
    Robot de trading avanzado que implementa una estrategia combinando Triple SMA y Alligator.
    
    Esta clase extiende RobotBase y define una estrategia avanzada que puede utilizar
    múltiples indicadores para generar señales de trading.
    
    Attributes:
        PERIODO_LENTO (int): Período para la media móvil lenta.
        PERIODO_MEDIO (int): Período para la media móvil media.
        PERIODO_RAPIDO (int): Período para la media móvil rápida.
        MODE_1 (int): Modo de operación para Triple SMA.
        JAW_PERIOD (int): Período para la línea Jaw (Mandíbula) del Alligator.
        JAW_OFFSET (int): Desplazamiento para la línea Jaw.
        TEETH_PERIOD (int): Período para la línea Teeth (Dientes) del Alligator.
        TEETH_OFFSET (int): Desplazamiento para la línea Teeth.
        LIPS_PERIOD (int): Período para la línea Lips (Labios) del Alligator.
        LIPS_OFFSET (int): Desplazamiento para la línea Lips.
        DROP_NAN (bool): Eliminar valores NaN resultantes.
        PERCENTAGE (int): Umbral de porcentaje para comparación.
        MODE_2 (int): Modo de operación para Alligator.
    """
    
    def __init__(self, 
                 symbol: str = 'USDJPY', 
                 timeframe: int = mt5.TIMEFRAME_M5, 
                 volume: float = 0.01, 
                 last_candles: int = 20, 
                 pips_sl: int = 100, 
                 pips_tp: int = 500, 
                 deviation: int = 100, 
                 comment: str = "Advanced Robot Order",
                 periodo_lento: int = 8,
                 periodo_medio: int = 6,
                 periodo_rapido: int = 4,
                 mode_1: int = 0,
                 jaw_period: int = 13,
                 jaw_offset: int = 8,
                 teeth_period: int = 8,
                 teeth_offset: int = 5,
                 lips_period: int = 5,
                 lips_offset: int = 3,
                 drop_nan: bool = True,
                 percentage: int = 20,
                 mode_2: int = 3):
        """
        Inicializa un nuevo robot con estrategia avanzada.
        
        Args:
            symbol: Par de divisas o instrumento a operar. Por defecto 'USDJPY'.
            timeframe: Marco temporal para el análisis. Por defecto mt5.TIMEFRAME_M5.
            volume: Tamaño de la posición en lotes. Por defecto 0.01.
            last_candles: Número de velas a analizar. Por defecto 20.
            pips_sl: Stop Loss en pips. Por defecto 100.
            pips_tp: Take Profit en pips. Por defecto 500.
            deviation: Desviación máxima permitida del precio. Por defecto 100.
            comment: Comentario para identificar las órdenes. Por defecto "Advanced Robot Order".
            periodo_lento: Período para la media móvil lenta. Por defecto 8.
            periodo_medio: Período para la media móvil media. Por defecto 6.
            periodo_rapido: Período para la media móvil rápida. Por defecto 4.
            mode_1: Modo de operación para Triple SMA. Por defecto 0.
            jaw_period: Período para la línea Jaw. Por defecto 13.
            jaw_offset: Desplazamiento para la línea Jaw. Por defecto 8.
            teeth_period: Período para la línea Teeth. Por defecto 8.
            teeth_offset: Desplazamiento para la línea Teeth. Por defecto 5.
            lips_period: Período para la línea Lips. Por defecto 5.
            lips_offset: Desplazamiento para la línea Lips. Por defecto 3.
            drop_nan: Eliminar valores NaN resultantes. Por defecto True.
            percentage: Umbral de porcentaje para comparación. Por defecto 20.
            mode_2: Modo de operación para Alligator. Por defecto 3.
        """
        super().__init__(symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment)
        
        # Parámetros específicos del indicador Triple SMA
        self.PERIODO_LENTO = periodo_lento
        self.PERIODO_MEDIO = periodo_medio
        self.PERIODO_RAPIDO = periodo_rapido
        self.MODE_1 = mode_1
        
        # Parámetros específicos del indicador Alligator
        self.JAW_PERIOD = jaw_period
        self.JAW_OFFSET = jaw_offset
        self.TEETH_PERIOD = teeth_period
        self.TEETH_OFFSET = teeth_offset
        self.LIPS_PERIOD = lips_period
        self.LIPS_OFFSET = lips_offset
        self.DROP_NAN = drop_nan
        self.PERCENTAGE = percentage
        self.MODE_2 = mode_2
    
    def analyze_market(self, df):
        """
        Analiza el mercado utilizando el indicador Triple SMA y genera señales de trading.
        
        Actualmente solo utiliza el Triple SMA, pero está preparado para integrar
        el indicador Alligator en futuras mejoras.
        
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
            self.MODE_1
        )
        
        # TODO: Implementar la integración del indicador Alligator
        # Ejemplo de cómo se podría integrar:
        indicator_alligator = BillWilliams(df)
        signal_alligator = indicator_alligator.alligator(
            self.JAW_PERIOD,
            self.JAW_OFFSET,
            self.TEETH_PERIOD,
            self.TEETH_OFFSET,
            self.LIPS_PERIOD,
            self.LIPS_OFFSET,
            self.DROP_NAN,
            self.PERCENTAGE,
            self.MODE_2
        )

        # Combinar señales de ambos indicadores
        if signal == 2 and signal_alligator == 2:
            return 2  # Señal de compra confirmada por ambos indicadores
        elif signal == 1 and signal_alligator == 1:
            return 1  # Señal de venta confirmada por ambos indicadores
        else:
            return 0  # Sin señal clara o señales contradictorias
    
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
                print("No hay signal que marque el cierre de la posición.")


# Punto de entrada del programa
if __name__ == "__main__":
    # Crear una instancia del robot y ejecutarlo
    robot = AdvancedRobot()
    robot.run()