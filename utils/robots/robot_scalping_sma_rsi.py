# -*- coding: utf-8 -*-
"""
Robot de Trading Scalping con Triple SMA y RSI: Implementación de estrategia de scalping

Este robot implementa una estrategia de scalping basada en la combinación de tres medias móviles simples (SMA)
y el indicador RSI (Relative Strength Index) para operar en periodos de 1 minuto.
La estrategia busca oportunidades de entrada rápidas cuando las medias móviles están alineadas
y el RSI confirma la dirección del movimiento, con protección de pérdidas incorporada.
"""
import MetaTrader5 as mt5
import logging
import time
from utils.base import RobotBase
from indicators.Trend import Trend
from indicators.Oscillator import Oscillator
from trading_platform.Metaquotes import Metaquotes as mtq
from strategy.StopsDynamic import StopsDynamic
from strategy.Protection import Protection

class ScalpingSMARSIRobot(RobotBase):
    """
    Robot de trading que implementa una estrategia de scalping basada en Triple SMA y RSI.
    
    Esta clase extiende RobotBase y define una estrategia específica para scalping
    utilizando tres medias móviles simples y el RSI para generar señales de trading
    en periodos de 1 minuto con protección de pérdidas.
    
    Attributes:
        PERIODO_LENTO (int): Período para la media móvil lenta.
        PERIODO_MEDIO (int): Período para la media móvil media.
        PERIODO_RAPIDO (int): Período para la media móvil rápida.
        PERIODO_RSI (int): Período para el cálculo del RSI.
        RSI_SOBREVENTA (int): Nivel de sobreventa del RSI.
        RSI_SOBRECOMPRA (int): Nivel de sobrecompra del RSI.
        MAX_PERDIDA_DIARIA (float): Porcentaje máximo de pérdida diaria permitida.
        USAR_SL_DINAMICO (bool): Indica si se debe usar stop loss dinámico.
        PERIODOS_SL_SMA (int): Períodos para el SMA usado en el stop loss dinámico.
    """
    
    def __init__(self, 
                 symbol: str = 'EURUSD', 
                 timeframe: int = mt5.TIMEFRAME_M1,  # Período de 1 minuto para scalping
                 volume: float = 0.01, 
                 last_candles: int = 100,  # Más candles para mejor análisis
                 pips_sl: int = 20,  # Stop loss más ajustado para scalping
                 pips_tp: int = 30,  # Take profit más ajustado para scalping
                 deviation: int = 10, 
                 comment: str = "Scalping SMA RSI Robot",
                 periodo_lento: int = 50,
                 periodo_medio: int = 20,
                 periodo_rapido: int = 5,
                 periodo_rsi: int = 14,
                 rsi_sobreventa: int = 30,
                 rsi_sobrecompra: int = 70,
                 max_perdida_diaria: float = 2.0,
                 usar_sl_dinamico: bool = True,
                 periodos_sl_sma: int = 10):
        """
        Inicializa un nuevo robot con estrategia de scalping basada en Triple SMA y RSI.
        
        Args:
            symbol: Par de divisas o instrumento a operar. Por defecto 'EURUSD'.
            timeframe: Marco temporal para el análisis. Por defecto mt5.TIMEFRAME_M1.
            volume: Tamaño de la posición en lotes. Por defecto 0.01.
            last_candles: Número de velas a analizar. Por defecto 100.
            pips_sl: Stop Loss en pips. Por defecto 20.
            pips_tp: Take Profit en pips. Por defecto 30.
            deviation: Desviación máxima permitida del precio. Por defecto 10.
            comment: Comentario para identificar las órdenes. Por defecto "Scalping SMA RSI Robot".
            periodo_lento: Período para la media móvil lenta. Por defecto 50.
            periodo_medio: Período para la media móvil media. Por defecto 20.
            periodo_rapido: Período para la media móvil rápida. Por defecto 5.
            periodo_rsi: Período para el cálculo del RSI. Por defecto 14.
            rsi_sobreventa: Nivel de sobreventa del RSI. Por defecto 30.
            rsi_sobrecompra: Nivel de sobrecompra del RSI. Por defecto 70.
            max_perdida_diaria: Porcentaje máximo de pérdida diaria permitida. Por defecto 2.0%.
            usar_sl_dinamico: Indica si se debe usar stop loss dinámico. Por defecto True.
            periodos_sl_sma: Períodos para el SMA usado en el stop loss dinámico. Por defecto 10.
        """
        super().__init__(symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment)
        
        # Parámetros específicos de los indicadores
        self.PERIODO_LENTO = periodo_lento
        self.PERIODO_MEDIO = periodo_medio
        self.PERIODO_RAPIDO = periodo_rapido
        self.PERIODO_RSI = periodo_rsi
        self.RSI_SOBREVENTA = rsi_sobreventa
        self.RSI_SOBRECOMPRA = rsi_sobrecompra
        
        # Parámetros de protección
        self.MAX_PERDIDA_DIARIA = max_perdida_diaria
        self.USAR_SL_DINAMICO = usar_sl_dinamico
        self.PERIODOS_SL_SMA = periodos_sl_sma
        
        # Inicializar protecciones
        self.protection = Protection()
        
        logging.info(f"{self.__class__.__name__} inicializado con parámetros específicos")
    
    def analyze_market(self, df):
        """
        Analiza el mercado utilizando Triple SMA y RSI para generar señales de trading.
        
        Args:
            df: DataFrame con los datos de mercado.
            
        Returns:
            int: Señal de trading (2 para compra, 1 para venta, 0 para no operar).
        """
        # Verificar protecciones antes de analizar el mercado
        if not self._check_protections():
            logging.info(f"{self.__class__.__name__} - Protecciones activadas, no se generarán señales.")
            return 0
        
        # Crear instancias de los indicadores
        trend_indicator = Trend(df)
        oscillator_indicator = Oscillator(df)
        
        # Calcular señales de Triple SMA
        sma_signal = trend_indicator.triple_sma(
            self.PERIODO_LENTO, 
            self.PERIODO_MEDIO, 
            self.PERIODO_RAPIDO, 
            0  # Modo 0 para detectar inicio de tendencia
        )
        
        # Calcular RSI
        rsi_value = oscillator_indicator.rsi(
            self.PERIODO_RSI,
            self.RSI_SOBRECOMPRA,
            self.RSI_SOBREVENTA,
            0  # Modo 0 para obtener el valor actual
        )
        
        # Lógica de trading combinando Triple SMA y RSI
        signal = 0  # Por defecto, no operar
        
        # Señal de compra: Triple SMA indica compra y RSI confirma (no sobrecomprado)
        if sma_signal == 2 and rsi_value < self.RSI_SOBRECOMPRA:
            signal = 2  # Compra
            logging.info(f"{self.__class__.__name__} - Señal de COMPRA generada: SMA={sma_signal}, RSI={rsi_value}")
        
        # Señal de venta: Triple SMA indica venta y RSI confirma (no sobrevendido)
        elif sma_signal == 1 and rsi_value > self.RSI_SOBREVENTA:
            signal = 1  # Venta
            logging.info(f"{self.__class__.__name__} - Señal de VENTA generada: SMA={sma_signal}, RSI={rsi_value}")
        
        return signal
    
    def _check_protections(self):
        """
        Verifica las protecciones configuradas.
        
        Returns:
            bool: True si se permite operar, False si alguna protección está activada.
        """
        # Actualizar información de la cuenta
        self.protection.update_account_info()
        
        # Verificar límite de pérdida diaria
        if not self.protection.daily_loss_limit(self.MAX_PERDIDA_DIARIA):
            logging.warning(f"{self.__class__.__name__} - Límite de pérdida diaria alcanzado ({self.MAX_PERDIDA_DIARIA}%).")
            return False
        
        return True
    
    def manage_positions(self, positions):
        """
        Gestiona las posiciones abiertas utilizando Triple SMA con modo 1 (fin de tendencia) y RSI.
        
        Args:
            positions: Lista de posiciones abiertas.
        """
        for position in positions:
            # Obtener datos actualizados
            df = self.get_market_data()
            
            # Calcular indicadores para cierre
            trend_indicator = Trend(df)
            oscillator_indicator = Oscillator(df)
            
            # Señal de Triple SMA para cierre (modo 1 - fin de tendencia)
            sma_signal_close = trend_indicator.triple_sma(
                self.PERIODO_LENTO, 
                self.PERIODO_MEDIO, 
                self.PERIODO_RAPIDO, 
                1  # Modo 1 para detectar fin de tendencia
            )
            
            # Valor actual del RSI
            rsi_value = oscillator_indicator.rsi(
                self.PERIODO_RSI,
                self.RSI_SOBRECOMPRA,
                self.RSI_SOBREVENTA,
                0  # Modo 0 para obtener el valor actual
            )
            
            # Lógica de cierre de posiciones
            should_close = False
            
            # Cerrar posición larga si:
            # - Triple SMA indica fin de tendencia alcista, o
            # - RSI está sobrecomprado
            if position.type == 0:  # Posición larga
                if sma_signal_close == 1 or rsi_value >= self.RSI_SOBRECOMPRA:
                    should_close = True
                    reason = "fin de tendencia alcista" if sma_signal_close == 1 else "RSI sobrecomprado"
            
            # Cerrar posición corta si:
            # - Triple SMA indica fin de tendencia bajista, o
            # - RSI está sobrevendido
            elif position.type == 1:  # Posición corta
                if sma_signal_close == 2 or rsi_value <= self.RSI_SOBREVENTA:
                    should_close = True
                    reason = "fin de tendencia bajista" if sma_signal_close == 2 else "RSI sobrevendido"
            
            # Cerrar la posición si es necesario
            if should_close:
                logging.info(f"{self.__class__.__name__} - Cerrando posición por {reason}.")
                mtq.close_position(position)
            else:
                logging.info(f"{self.__class__.__name__} - No hay signal que marque el cierre de la posición.")
            
            # Aplicar stop loss dinámico si está habilitado
            if self.USAR_SL_DINAMICO:
                self._apply_dynamic_sl(position)
    
    def _apply_dynamic_sl(self, position):
        """
        Aplica stop loss dinámico a la posición.
        
        Args:
            position: Posición a la que aplicar el stop loss dinámico.
        """
        try:
            # Usar SL basado en SMA
            if position.type == 0:  # Posición larga
                StopsDynamic.sl_sma(self.PIPS_SL, self.PERIODOS_SL_SMA)
                logging.info(f"{self.__class__.__name__} - Stop loss dinámico aplicado a posición larga.")
            elif position.type == 1:  # Posición corta
                StopsDynamic.sl_sma(self.PIPS_SL, self.PERIODOS_SL_SMA)
                logging.info(f"{self.__class__.__name__} - Stop loss dinámico aplicado a posición corta.")
        except Exception as e:
            logging.error(f"{self.__class__.__name__} - Error al aplicar stop loss dinámico: {str(e)}")
    
    def run(self):
        """
        Ejecuta el bucle principal del robot de trading con protecciones adicionales.
        """
        # Inicializar la conexión con MetaTrader 5
        self.initialize()
        
        logging.info(f"{self.__class__.__name__} - Iniciando robot de scalping con Triple SMA y RSI")
        
        # Bucle principal de trading
        try:
            while True:
                # Verificar protecciones antes de continuar
                if not self._check_protections():
                    logging.warning(f"{self.__class__.__name__} - Protecciones activadas, esperando 60 segundos...")
                    time.sleep(60)
                    continue
                
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
                # Para scalping en M1, revisamos cada 5 segundos
                time.sleep(5)
        except KeyboardInterrupt:
            logging.info(f"{self.__class__.__name__} - Robot detenido por el usuario")
        except Exception as e:
            logging.error(f"{self.__class__.__name__} - Error en el bucle principal: {str(e)}")
        finally:
            logging.info(f"{self.__class__.__name__} - Shutting down")


# Punto de entrada del programa
if __name__ == "__main__":
    # Crear una instancia del robot y ejecutarlo
    robot = ScalpingSMARSIRobot()
    robot.run()