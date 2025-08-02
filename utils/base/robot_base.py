# -*- coding: utf-8 -*-
"""
Robot Base: Clase base para la creación estandarizada de robots de trading

Este módulo proporciona una clase base para la creación de robots de trading,
estandarizando la estructura y el flujo de trabajo común a todos los robots.
Permite crear nuevos robots simplemente heredando de esta clase y definiendo
la estrategia específica a utilizar.
"""
import time
import MetaTrader5 as mt5
from log.log_loader import setup_logging
from trading_platform.Metaquotes import Metaquotes as mtq
import logging

class RobotBase:
    """
    Clase base para la creación de robots de trading.
    
    Esta clase implementa la estructura común y el flujo de trabajo para todos los robots,
    permitiendo que las clases derivadas se centren únicamente en definir su estrategia
    específica de trading.
    
    Attributes:
        SYMBOL (str): Par de divisas o instrumento a operar.
        TIMEFRAME (int): Marco temporal para el análisis (ej. mt5.TIMEFRAME_M5).
        VOLUME (float): Tamaño de la posición en lotes.
        LAST_CANDLES (int): Número de velas a analizar.
        PIPS_SL (int): Stop Loss en pips.
        PIPS_TP (int): Take Profit en pips.
        DEVIATION (int): Desviación máxima permitida del precio.
        COMMENT (str): Comentario para identificar las órdenes.
    """
    
    def __init__(self, 
                 symbol: str, 
                 timeframe: int, 
                 volume: float, 
                 last_candles: int, 
                 pips_sl: int, 
                 pips_tp: int, 
                 deviation: int, 
                 comment: str):
        """
        Inicializa un nuevo robot con los parámetros de trading especificados.
        
        Args:
            symbol: Par de divisas o instrumento a operar.
            timeframe: Marco temporal para el análisis.
            volume: Tamaño de la posición en lotes.
            last_candles: Número de velas a analizar.
            pips_sl: Stop Loss en pips.
            pips_tp: Take Profit en pips.
            deviation: Desviación máxima permitida del precio.
            comment: Comentario para identificar las órdenes.
        """
        self.SYMBOL = symbol
        self.TIMEFRAME = timeframe
        self.VOLUME = volume
        self.LAST_CANDLES = last_candles
        self.PIPS_SL = pips_sl
        self.PIPS_TP = pips_tp
        self.DEVIATION = deviation
        self.COMMENT = comment
        
        # Configuración del sistema de registro (logging)
        setup_logging()
        
    def initialize(self):
        """
        Inicializa la conexión con MetaTrader 5.
        """
        mtq.initialize_mt5()
        
    def get_market_data(self):
        """
        Obtiene los datos de mercado actualizados.
        
        Returns:
            pd.DataFrame: DataFrame con los datos de precio.
        """
        df = mtq.get_df(self.SYMBOL, self.TIMEFRAME, self.LAST_CANDLES)
        logging.info(f"{self.__class__.__name__} - Datos obtenidos desde MetaTrader 5.")
        return df
        
    def analyze_market(self, df):
        """
        Analiza el mercado y genera señales de trading.
        
        Este método debe ser implementado por las clases derivadas para definir
        la estrategia específica de trading.
        
        Args:
            df: DataFrame con los datos de mercado.
            
        Returns:
            int: Señal de trading (2 para compra, 1 para venta, 0 para no operar).
        """
        raise NotImplementedError("Las clases derivadas deben implementar analyze_market()")
    
    def process_signal(self, signal):
        """
        Procesa la señal de trading y ejecuta las órdenes correspondientes.
        
        Args:
            signal: Señal de trading (2 para compra, 1 para venta, 0 para no operar).
        """
        if signal == 2:  # Señal de compra
            mtq.open_order_buy(self.SYMBOL, self.VOLUME, signal, self.PIPS_SL, 
                              self.PIPS_TP, self.DEVIATION, self.COMMENT)
        elif signal == 1:  # Señal de venta
            mtq.open_order_sell(self.SYMBOL, self.VOLUME, signal, self.PIPS_SL, 
                               self.PIPS_TP, self.DEVIATION, self.COMMENT)
        else:  # No hay señal clara
            logging.info(">>> No hay signal.")
    
    def check_open_positions(self):
        """
        Verifica si hay posiciones abiertas para el símbolo configurado.
        
        Returns:
            tuple: (bool, list) - (hay_posiciones, lista_de_posiciones)
        """
        positions = mt5.positions_get(symbol=self.SYMBOL)
        logging.info(f">>> Hay {len(positions) if positions else 0} posiciones abiertas.")
        
        if positions is None or len(positions) == 0:
            return False, []
        return True, positions
    
    def manage_positions(self, positions):
        """
        Gestiona las posiciones abiertas.
        
        Este método puede ser sobrescrito por las clases derivadas para implementar
        estrategias específicas de gestión de posiciones.
        
        Args:
            positions: Lista de posiciones abiertas.
        """
        for position in positions:
            # Obtener datos actualizados y calcular indicadores
            df = self.get_market_data()
            signal = self.analyze_market(df)
            
            # Cerrar posiciones cuando la señal es contraria a la posición
            if position.type == 0 and signal == 1 or position.type == 1 and signal == 2:
                mtq.close_position(position)
            else:
                logging.info("No hay signal que marque el cierre de la posición.")
    
    def run(self):
        """
        Ejecuta el bucle principal del robot de trading.
        """
        # Inicializar la conexión con MetaTrader 5
        self.initialize()
        
        # Bucle principal de trading
        while True:
            # Verificar posiciones abiertas
            has_positions, positions = self.check_open_positions()
            
            # Si no hay posiciones, buscar oportunidades para abrir nuevas
            if not has_positions:
                df = self.get_market_data()
                signal = self.analyze_market(df)
                self.process_signal(signal)
            # Si hay posiciones, gestionarlas
            else:
                self.manage_positions(positions)
            
            # Pausa para evitar sobrecarga de solicitudes a MetaTrader 5
            time.sleep(1)