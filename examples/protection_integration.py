# -*- coding: utf-8 -*-
"""
Ejemplo de integración del módulo de protección con robots de trading.

Este script muestra cómo integrar las protecciones implementadas en el módulo Protection
con los robots de trading existentes para mejorar la gestión de riesgos.
"""
import MetaTrader5 as mt5
import logging
from utils.base.robot_base import RobotBase
from strategy.Protection import Protection
from trading_platform.Metaquotes import Metaquotes as mtq
from indicators.Trend import Trend
import time

class ProtectedRobot(RobotBase):
    """
    Robot de trading con protecciones integradas.
    
    Esta clase extiende RobotBase e integra el módulo de protección para
    implementar una gestión de riesgos más robusta.
    
    Attributes:
        protection (Protection): Instancia del módulo de protección.
        breakdown_percentage (float): Porcentaje de pérdida que activará la protección.
        max_drawdown_percentage (float): Porcentaje máximo de drawdown permitido.
        daily_loss_percentage (float): Porcentaje máximo de pérdida diaria permitido.
        weekly_loss_percentage (float): Porcentaje máximo de pérdida semanal permitido.
        monthly_loss_percentage (float): Porcentaje máximo de pérdida mensual permitido.
        max_consecutive_losses (int): Número máximo de pérdidas consecutivas permitidas.
        volume_reduction_factor (float): Factor de reducción del volumen.
        max_volatility_multiplier (float): Multiplicador máximo de volatilidad.
        max_correlation (float): Correlación máxima permitida entre instrumentos.
        allowed_hours (list): Lista de tuplas con horas permitidas para operar.
        allowed_days (list): Lista de días permitidos para operar.
        symbols_correlation (list): Lista de símbolos para verificar correlación.
    """
    
    def __init__(self, 
                 symbol: str = 'EURUSD', 
                 timeframe: int = mt5.TIMEFRAME_M5, 
                 volume: float = 0.01, 
                 last_candles: int = 20, 
                 pips_sl: int = 100, 
                 pips_tp: int = 200, 
                 deviation: int = 20, 
                 comment: str = "Protected Robot Order",
                 breakdown_percentage: float = 10.0,
                 max_drawdown_percentage: float = 15.0,
                 daily_loss_percentage: float = 5.0,
                 weekly_loss_percentage: float = 10.0,
                 monthly_loss_percentage: float = 15.0,
                 max_consecutive_losses: int = 3,
                 volume_reduction_factor: float = 0.5,
                 max_volatility_multiplier: float = 2.0,
                 max_correlation: float = 0.7,
                 allowed_hours: list = None,
                 allowed_days: list = None,
                 symbols_correlation: list = None):
        """
        Inicializa un nuevo robot con protecciones integradas.
        
        Args:
            symbol: Par de divisas o instrumento a operar. Por defecto 'EURUSD'.
            timeframe: Marco temporal para el análisis. Por defecto mt5.TIMEFRAME_M5.
            volume: Tamaño de la posición en lotes. Por defecto 0.01.
            last_candles: Número de velas a analizar. Por defecto 20.
            pips_sl: Stop Loss en pips. Por defecto 100.
            pips_tp: Take Profit en pips. Por defecto 200.
            deviation: Desviación máxima permitida del precio. Por defecto 20.
            comment: Comentario para identificar las órdenes. Por defecto "Protected Robot Order".
            breakdown_percentage: Porcentaje de pérdida que activará la protección. Por defecto 10.0.
            max_drawdown_percentage: Porcentaje máximo de drawdown permitido. Por defecto 15.0.
            daily_loss_percentage: Porcentaje máximo de pérdida diaria permitido. Por defecto 5.0.
            weekly_loss_percentage: Porcentaje máximo de pérdida semanal permitido. Por defecto 10.0.
            monthly_loss_percentage: Porcentaje máximo de pérdida mensual permitido. Por defecto 15.0.
            max_consecutive_losses: Número máximo de pérdidas consecutivas permitidas. Por defecto 3.
            volume_reduction_factor: Factor de reducción del volumen. Por defecto 0.5.
            max_volatility_multiplier: Multiplicador máximo de volatilidad. Por defecto 2.0.
            max_correlation: Correlación máxima permitida entre instrumentos. Por defecto 0.7.
            allowed_hours: Lista de tuplas con horas permitidas para operar. Por defecto None (24h).
            allowed_days: Lista de días permitidos para operar. Por defecto None (todos los días).
            symbols_correlation: Lista de símbolos para verificar correlación. Por defecto None.
        """
        super().__init__(symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment)
        
        # Inicializar el módulo de protección
        self.protection = Protection()
        
        # Configurar parámetros de protección
        self.breakdown_percentage = breakdown_percentage
        self.max_drawdown_percentage = max_drawdown_percentage
        self.daily_loss_percentage = daily_loss_percentage
        self.weekly_loss_percentage = weekly_loss_percentage
        self.monthly_loss_percentage = monthly_loss_percentage
        self.max_consecutive_losses = max_consecutive_losses
        self.volume_reduction_factor = volume_reduction_factor
        self.max_volatility_multiplier = max_volatility_multiplier
        self.max_correlation = max_correlation
        self.allowed_hours = allowed_hours
        self.allowed_days = allowed_days
        
        # Configurar símbolos para correlación
        if symbols_correlation is None:
            # Por defecto, usar algunos pares de divisas comunes
            self.symbols_correlation = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF']
        else:
            self.symbols_correlation = symbols_correlation
    
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
    
    def check_protections(self):
        """
        Verifica todas las protecciones configuradas y ajusta el volumen si es necesario.
        
        Returns:
            tuple: (trading_allowed, adjusted_volume, reasons)
        """
        # Verificar todas las protecciones
        protection_result = self.protection.check_all_protections(
            breakdown_percentage=self.breakdown_percentage,
            max_drawdown_percentage=self.max_drawdown_percentage,
            daily_loss_percentage=self.daily_loss_percentage,
            weekly_loss_percentage=self.weekly_loss_percentage,
            monthly_loss_percentage=self.monthly_loss_percentage,
            max_consecutive_losses=self.max_consecutive_losses,
            volume_reduction_factor=self.volume_reduction_factor,
            symbol=self.SYMBOL,
            timeframe=self.TIMEFRAME,
            max_volatility_multiplier=self.max_volatility_multiplier,
            symbols_correlation=self.symbols_correlation,
            max_correlation=self.max_correlation,
            allowed_hours=self.allowed_hours,
            allowed_days=self.allowed_days
        )
        
        # Obtener el resultado de las protecciones
        trading_allowed = protection_result['trading_allowed']
        reasons = protection_result['reasons']
        volume_factor = protection_result['volume_factor']
        
        # Ajustar el volumen según el factor calculado
        adjusted_volume = self.VOLUME * volume_factor
        
        # Registrar el resultado de las protecciones
        if not trading_allowed:
            logging.warning(f"Trading no permitido: {', '.join(reasons)}")
        elif volume_factor < 1.0:
            logging.info(f"Volumen ajustado: {self.VOLUME} -> {adjusted_volume} (factor: {volume_factor:.2f})")
        
        return trading_allowed, adjusted_volume, reasons
    
    def process_signal(self, signal):
        """
        Procesa la señal de trading y ejecuta las órdenes correspondientes,
        aplicando las protecciones configuradas.
        
        Args:
            signal: Señal de trading (2 para compra, 1 para venta, 0 para no operar).
        """
        # Verificar protecciones antes de procesar la señal
        trading_allowed, adjusted_volume, reasons = self.check_protections()
        
        # Si el trading no está permitido, no procesar la señal
        if not trading_allowed:
            logging.warning(f"Señal ignorada debido a protecciones activas: {', '.join(reasons)}")
            return
        
        # Procesar la señal con el volumen ajustado
        if signal == 2:  # Señal de compra
            mtq.open_order_buy(self.SYMBOL, adjusted_volume, signal, self.PIPS_SL, 
                              self.PIPS_TP, self.DEVIATION, self.COMMENT)
        elif signal == 1:  # Señal de venta
            mtq.open_order_sell(self.SYMBOL, adjusted_volume, signal, self.PIPS_SL, 
                               self.PIPS_TP, self.DEVIATION, self.COMMENT)
        else:  # No hay señal clara
            logging.info(">>> No hay signal.")
    
    def run(self):
        """
        Ejecuta el bucle principal del robot de trading con protecciones.
        """
        # Inicializar la conexión con MetaTrader 5
        self.initialize()
        
        # Bucle principal de trading
        while True:
            try:
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
                
            except Exception as e:
                logging.error(f"Error en el bucle principal: {e}")
                time.sleep(5)  # Pausa más larga en caso de error
                continue


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar el logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Crear una instancia del robot protegido con configuración personalizada
    robot = ProtectedRobot(
        symbol='EURUSD',
        timeframe=mt5.TIMEFRAME_M5,
        volume=0.01,
        pips_sl=50,
        pips_tp=100,
        breakdown_percentage=8.0,  # Detener trading si las pérdidas alcanzan el 8% del capital
        max_drawdown_percentage=12.0,  # Detener trading si el drawdown supera el 12%
        daily_loss_percentage=3.0,  # Limitar pérdidas diarias al 3%
        weekly_loss_percentage=7.0,  # Limitar pérdidas semanales al 7%
        monthly_loss_percentage=12.0,  # Limitar pérdidas mensuales al 12%
        max_consecutive_losses=3,  # Reducir volumen después de 3 pérdidas consecutivas
        volume_reduction_factor=0.5,  # Reducir volumen al 50%
        allowed_hours=[(8, 20)],  # Solo operar entre las 8:00 y las 20:00
        allowed_days=[0, 1, 2, 3, 4],  # Solo operar de lunes a viernes
        symbols_correlation=['EURUSD', 'GBPUSD', 'EURGBP']  # Verificar correlación entre estos pares
    )
    
    # Ejecutar el robot
    robot.run()