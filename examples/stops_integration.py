# -*- coding: utf-8 -*-
"""
Ejemplo de integración del módulo StopsDynamic con robots de trading.

Este script muestra cómo integrar los stops dinámicos implementados en el módulo StopsDynamic
con los robots de trading existentes para mejorar la gestión de riesgos.
"""
import MetaTrader5 as mt5
import logging
import time
import pandas as pd
from utils.base.robot_base import RobotBase
from strategy.StopsDynamic import StopsDynamic
from trading_platform.Metaquotes import Metaquotes as mtq
from indicators.Trend import Trend

# Configurar el logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class StopsRobot(RobotBase):
    """
    Robot de trading con stops dinámicos integrados.
    
    Esta clase extiende RobotBase e integra el módulo StopsDynamic para
    implementar una gestión de stops loss más robusta y adaptativa.
    
    Attributes:
        stops (StopsDynamic): Instancia del módulo de stops dinámicos.
        sl_strategy (str): Estrategia de stop loss a utilizar ('follower' o 'sma').
        sl_pips (int): Distancia en pips para el stop loss.
        sma_periods (int): Número de periodos para la SMA (solo para estrategia 'sma').
        check_interval (int): Intervalo en segundos para verificar y actualizar los stops.
    """
    
    def __init__(self, 
                 symbol: str = 'EURUSD', 
                 timeframe: int = mt5.TIMEFRAME_M5, 
                 volume: float = 0.01, 
                 last_candles: int = 20, 
                 pips_sl: int = 100, 
                 pips_tp: int = 200, 
                 deviation: int = 20, 
                 comment: str = "Stops Robot Order",
                 sl_strategy: str = "follower",
                 sl_pips: int = 50,
                 sma_periods: int = 20,
                 check_interval: int = 60):
        """
        Inicializa un nuevo robot con stops dinámicos integrados.
        
        Args:
            symbol: Par de divisas o instrumento a operar. Por defecto 'EURUSD'.
            timeframe: Marco temporal para el análisis. Por defecto mt5.TIMEFRAME_M5.
            volume: Tamaño de la posición en lotes. Por defecto 0.01.
            last_candles: Número de velas a analizar. Por defecto 20.
            pips_sl: Stop Loss inicial en pips. Por defecto 100.
            pips_tp: Take Profit en pips. Por defecto 200.
            deviation: Desviación máxima permitida del precio. Por defecto 20.
            comment: Comentario para identificar las órdenes. Por defecto "Stops Robot Order".
            sl_strategy: Estrategia de stop loss a utilizar ('follower' o 'sma'). Por defecto 'follower'.
            sl_pips: Distancia en pips para el stop loss dinámico. Por defecto 50.
            sma_periods: Número de periodos para la SMA (solo para estrategia 'sma'). Por defecto 20.
            check_interval: Intervalo en segundos para verificar y actualizar los stops. Por defecto 60.
        """
        super().__init__(symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment)
        
        # Inicializar el módulo de stops dinámicos
        self.stops = StopsDynamic()
        
        # Configurar parámetros de stops
        self.sl_strategy = sl_strategy
        self.sl_pips = sl_pips
        self.sma_periods = sma_periods
        self.check_interval = check_interval
        
        # Tiempo de la última verificación de stops
        self.last_stops_check = 0
    
    def analyze_market(self, df):
        """
        Analiza el mercado utilizando el indicador Triple SMA y genera señales de trading.
        
        Este es solo un ejemplo simple. En un robot real, se utilizaría una estrategia más compleja.
        
        Args:
            df: DataFrame con los datos de mercado.
            
        Returns:
            int: Señal de trading (2 para compra, 1 para venta, 0 para no operar).
        """
        # Crear una instancia del indicador Trend y calcular el Triple SMA
        indicator = Trend(df)
        signal = indicator.triple_sma(8, 5, 3, 0)
        
        return signal
    
    def update_stops(self):
        """
        Actualiza los stops dinámicos según la estrategia configurada.
        
        Esta función aplica la estrategia de stops seleccionada (follower o SMA)
        a todas las posiciones abiertas.
        """
        # Verificar si es momento de actualizar los stops
        current_time = time.time()
        if current_time - self.last_stops_check < self.check_interval:
            return
        
        # Actualizar el tiempo de la última verificación
        self.last_stops_check = current_time
        
        # Aplicar la estrategia de stops seleccionada
        if self.sl_strategy == "follower":
            logging.info(f"Aplicando estrategia SL Follower con {self.sl_pips} pips")
            self.stops.sl_follower(self.sl_pips)
        elif self.sl_strategy == "sma":
            logging.info(f"Aplicando estrategia SL SMA con {self.sma_periods} periodos y {self.sl_pips} pips")
            self.stops.sl_sma(self.sl_pips, self.sma_periods)
        else:
            logging.error(f"Estrategia de stops desconocida: {self.sl_strategy}")
    
    def process_signal(self, signal):
        """
        Procesa la señal de trading y ejecuta las órdenes correspondientes.
        
        Args:
            signal: Señal de trading (2 para compra, 1 para venta, 0 para no operar).
        """
        if signal == 2:  # Señal de compra
            logging.info(f"Señal de COMPRA detectada para {self.SYMBOL}")
            mtq.open_order_buy(self.SYMBOL, self.VOLUME, signal, self.PIPS_SL, 
                              self.PIPS_TP, self.DEVIATION, self.COMMENT)
        elif signal == 1:  # Señal de venta
            logging.info(f"Señal de VENTA detectada para {self.SYMBOL}")
            mtq.open_order_sell(self.SYMBOL, self.VOLUME, signal, self.PIPS_SL, 
                               self.PIPS_TP, self.DEVIATION, self.COMMENT)
        else:  # No hay señal clara
            logging.info("No hay señal clara para operar.")
    
    def run(self):
        """
        Ejecuta el bucle principal del robot de trading con stops dinámicos.
        """
        # Inicializar la conexión con MetaTrader 5
        if not mt5.initialize():
            logging.error("Error al inicializar MetaTrader5")
            return
        
        logging.info(f"Conexión con MetaTrader5 establecida. Versión: {mt5.version()}")
        logging.info(f"Robot iniciado para {self.SYMBOL} con estrategia de stops {self.sl_strategy}")
        
        try:
            # Bucle principal de trading
            while True:
                try:
                    # Verificar posiciones abiertas
                    has_positions, positions = self.check_open_positions()
                    
                    # Si hay posiciones, actualizar los stops dinámicos
                    if has_positions:
                        self.update_stops()
                    
                    # Si no hay posiciones, buscar oportunidades para abrir nuevas
                    else:
                        df = self.get_market_data()
                        signal = self.analyze_market(df)
                        self.process_signal(signal)
                    
                    # Pausa para evitar sobrecarga de solicitudes a MetaTrader 5
                    time.sleep(1)
                    
                except Exception as e:
                    logging.error(f"Error en el bucle principal: {e}")
                    time.sleep(5)  # Pausa más larga en caso de error
                    continue
                
        finally:
            # Cerrar conexión con MetaTrader5
            logging.info("Cerrando conexión con MetaTrader5")
            mt5.shutdown()


# Ejemplo de uso con diferentes configuraciones de stops
def example_follower_strategy():
    """
    Ejemplo de uso del robot con estrategia de stops follower.
    """
    robot = StopsRobot(
        symbol='EURUSD',
        timeframe=mt5.TIMEFRAME_M5,
        volume=0.01,
        pips_sl=100,
        pips_tp=200,
        sl_strategy='follower',
        sl_pips=50,
        check_interval=30
    )
    robot.run()

def example_sma_strategy():
    """
    Ejemplo de uso del robot con estrategia de stops SMA.
    """
    robot = StopsRobot(
        symbol='GBPUSD',
        timeframe=mt5.TIMEFRAME_M5,
        volume=0.01,
        pips_sl=100,
        pips_tp=200,
        sl_strategy='sma',
        sl_pips=30,
        sma_periods=20,
        check_interval=60
    )
    robot.run()

def example_multiple_symbols():
    """
    Ejemplo de cómo gestionar stops dinámicos para múltiples símbolos.
    """
    # Lista de símbolos a operar
    symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
    
    # Crear una instancia de StopsDynamic
    stops = StopsDynamic()
    
    # Inicializar conexión con MetaTrader5
    if not mt5.initialize():
        logging.error("Error al inicializar MetaTrader5")
        return
    
    logging.info(f"Conexión con MetaTrader5 establecida. Versión: {mt5.version()}")
    
    try:
        # Bucle principal
        while True:
            try:
                # Aplicar stops dinámicos a todas las posiciones abiertas
                logging.info("Aplicando stops dinámicos a todas las posiciones abiertas")
                stops.sl_follower(50)  # Aplicar estrategia follower con 50 pips
                
                # Pausa entre iteraciones
                logging.info("Esperando 60 segundos para la próxima verificación...")
                time.sleep(60)
                
            except Exception as e:
                logging.error(f"Error en el bucle principal: {e}")
                time.sleep(5)
                continue
                
    finally:
        # Cerrar conexión con MetaTrader5
        logging.info("Cerrando conexión con MetaTrader5")
        mt5.shutdown()


# Ejemplo de uso independiente de StopsDynamic
def example_standalone_stops():
    """
    Ejemplo de uso independiente del módulo StopsDynamic sin un robot.
    
    Este ejemplo muestra cómo utilizar el módulo StopsDynamic directamente
    para gestionar los stops de posiciones abiertas manualmente o por otros sistemas.
    """
    # Inicializar conexión con MetaTrader5
    if not mt5.initialize():
        logging.error("Error al inicializar MetaTrader5")
        return
    
    logging.info(f"Conexión con MetaTrader5 establecida. Versión: {mt5.version()}")
    
    # Crear una instancia de StopsDynamic
    stops = StopsDynamic()
    
    try:
        # Bucle principal
        while True:
            try:
                # Obtener posiciones abiertas
                positions = mt5.positions_get()
                
                if positions is None or len(positions) == 0:
                    logging.info("No hay posiciones abiertas.")
                else:
                    # Convertir a DataFrame para análisis
                    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
                    logging.info(f"Posiciones abiertas: {len(df)}")
                    
                    # Aplicar diferentes estrategias según el símbolo
                    for symbol in df['symbol'].unique():
                        symbol_positions = df[df['symbol'] == symbol]
                        
                        # Decidir la estrategia según el símbolo
                        if symbol in ['EURUSD', 'GBPUSD']:
                            logging.info(f"Aplicando estrategia SL Follower para {symbol}")
                            stops.sl_follower(50)
                        else:
                            logging.info(f"Aplicando estrategia SL SMA para {symbol}")
                            stops.sl_sma(30, 20)
                
                # Pausa entre iteraciones
                logging.info("Esperando 60 segundos para la próxima verificación...")
                time.sleep(60)
                
            except Exception as e:
                logging.error(f"Error en el bucle principal: {e}")
                time.sleep(5)
                continue
                
    finally:
        # Cerrar conexión con MetaTrader5
        logging.info("Cerrando conexión con MetaTrader5")
        mt5.shutdown()


if __name__ == "__main__":
    """
    Punto de entrada principal para ejecutar el ejemplo.
    
    Descomentar la función de ejemplo que se desea ejecutar.
    """
    # Ejemplo de robot con estrategia follower
    example_follower_strategy()
    
    # Ejemplo de robot con estrategia SMA
    # example_sma_strategy()
    
    # Ejemplo de gestión de stops para múltiples símbolos
    # example_multiple_symbols()
    
    # Ejemplo de uso independiente de StopsDynamic
    # example_standalone_stops()