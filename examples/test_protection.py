# -*- coding: utf-8 -*-
"""
Script para probar las protecciones implementadas en el módulo Protection.

Este script realiza pruebas básicas de las diferentes protecciones implementadas
en el módulo Protection para verificar su correcto funcionamiento.
"""
import MetaTrader5 as mt5
import logging
import datetime
from strategy.Protection import Protection

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_breakdown_protection():
    """Prueba la protección por breakdown."""
    logger.info("Probando protección por breakdown...")
    protection = Protection()
    
    # Simular diferentes escenarios
    # 1. Pérdida por debajo del umbral
    protection.initial_balance = 10000
    protection.account_info = {'equity': 9500}  # 5% de pérdida
    result = protection.breakdown(10.0)
    logger.info(f"Pérdida del 5% (umbral 10%): Trading permitido: {result['allowed']}")
    
    # 2. Pérdida igual al umbral
    protection.account_info = {'equity': 9000}  # 10% de pérdida
    result = protection.breakdown(10.0)
    logger.info(f"Pérdida del 10% (umbral 10%): Trading permitido: {result['allowed']}")
    
    # 3. Pérdida por encima del umbral
    protection.account_info = {'equity': 8500}  # 15% de pérdida
    result = protection.breakdown(10.0)
    logger.info(f"Pérdida del 15% (umbral 10%): Trading permitido: {result['allowed']}")

def test_max_drawdown_protection():
    """Prueba la protección por drawdown máximo."""
    logger.info("Probando protección por drawdown máximo...")
    protection = Protection()
    
    # Simular diferentes escenarios
    # 1. Drawdown por debajo del umbral
    protection.max_balance = 10000
    protection.account_info = {'equity': 9000}  # 10% de drawdown
    result = protection.max_drawdown(15.0)
    logger.info(f"Drawdown del 10% (umbral 15%): Trading permitido: {result['allowed']}")
    
    # 2. Drawdown igual al umbral
    protection.account_info = {'equity': 8500}  # 15% de drawdown
    result = protection.max_drawdown(15.0)
    logger.info(f"Drawdown del 15% (umbral 15%): Trading permitido: {result['allowed']}")
    
    # 3. Drawdown por encima del umbral
    protection.account_info = {'equity': 8000}  # 20% de drawdown
    result = protection.max_drawdown(15.0)
    logger.info(f"Drawdown del 20% (umbral 15%): Trading permitido: {result['allowed']}")

def test_daily_loss_limit():
    """Prueba el límite de pérdida diaria."""
    logger.info("Probando límite de pérdida diaria...")
    protection = Protection()
    
    # Simular diferentes escenarios
    # 1. Pérdida diaria por debajo del umbral
    protection.initial_balance = 10000
    protection.daily_loss = 300  # 3% de pérdida diaria
    result = protection.daily_loss_limit(5.0)
    logger.info(f"Pérdida diaria del 3% (umbral 5%): Trading permitido: {result['allowed']}")
    
    # 2. Pérdida diaria igual al umbral
    protection.daily_loss = 500  # 5% de pérdida diaria
    result = protection.daily_loss_limit(5.0)
    logger.info(f"Pérdida diaria del 5% (umbral 5%): Trading permitido: {result['allowed']}")
    
    # 3. Pérdida diaria por encima del umbral
    protection.daily_loss = 700  # 7% de pérdida diaria
    result = protection.daily_loss_limit(5.0)
    logger.info(f"Pérdida diaria del 7% (umbral 5%): Trading permitido: {result['allowed']}")

def test_consecutive_losses_protection():
    """Prueba la protección por pérdidas consecutivas."""
    logger.info("Probando protección por pérdidas consecutivas...")
    protection = Protection()
    
    # Simular diferentes escenarios
    # 1. Menos pérdidas consecutivas que el umbral
    protection.consecutive_losses = 2
    result = protection.consecutive_losses_protection(3, 0.5)
    logger.info(f"2 pérdidas consecutivas (umbral 3): Factor de volumen: {result['volume_factor']}")
    
    # 2. Igual número de pérdidas consecutivas que el umbral
    protection.consecutive_losses = 3
    result = protection.consecutive_losses_protection(3, 0.5)
    logger.info(f"3 pérdidas consecutivas (umbral 3): Factor de volumen: {result['volume_factor']}")
    
    # 3. Más pérdidas consecutivas que el umbral
    protection.consecutive_losses = 5
    result = protection.consecutive_losses_protection(3, 0.5)
    logger.info(f"5 pérdidas consecutivas (umbral 3): Factor de volumen: {result['volume_factor']}")

def test_time_based_restrictions():
    """Prueba las restricciones basadas en tiempo."""
    logger.info("Probando restricciones basadas en tiempo...")
    protection = Protection()
    
    # Obtener la hora y día actual
    current_time = datetime.datetime.now()
    current_hour = current_time.hour
    current_day = current_time.weekday()  # 0=lunes, 6=domingo
    
    logger.info(f"Hora actual: {current_hour}, Día actual: {current_day} (0=lunes, 6=domingo)")
    
    # 1. Probar con horario que incluye la hora actual
    allowed_hours = [(current_hour - 1, current_hour + 1)]
    result = protection.time_based_restrictions(allowed_hours)
    logger.info(f"Horario permitido [{current_hour - 1}-{current_hour + 1}]: Trading permitido: {result['allowed']}")
    
    # 2. Probar con horario que no incluye la hora actual
    if current_hour < 12:
        allowed_hours = [(current_hour + 2, current_hour + 4)]
    else:
        allowed_hours = [(current_hour - 4, current_hour - 2)]
    result = protection.time_based_restrictions(allowed_hours)
    logger.info(f"Horario no permitido: Trading permitido: {result['allowed']}")
    
    # 3. Probar con día que no incluye el día actual
    allowed_days = [(current_day + 1) % 7, (current_day + 2) % 7]
    result = protection.time_based_restrictions(None, allowed_days)
    logger.info(f"Día no permitido: Trading permitido: {result['allowed']}")

def test_check_all_protections():
    """Prueba la verificación de todas las protecciones."""
    logger.info("Probando verificación de todas las protecciones...")
    protection = Protection()
    
    # Configurar escenario donde todas las protecciones permiten el trading
    protection.initial_balance = 10000
    protection.max_balance = 10000
    protection.account_info = {'equity': 9800}  # 2% de pérdida
    protection.daily_loss = 100  # 1% de pérdida diaria
    protection.weekly_loss = 200  # 2% de pérdida semanal
    protection.monthly_loss = 300  # 3% de pérdida mensual
    protection.consecutive_losses = 1
    
    result = protection.check_all_protections(
        breakdown_percentage=10.0,
        max_drawdown_percentage=15.0,
        daily_loss_percentage=5.0,
        weekly_loss_percentage=10.0,
        monthly_loss_percentage=15.0,
        max_consecutive_losses=3,
        volume_reduction_factor=0.5
    )
    
    logger.info(f"Todas las protecciones OK: Trading permitido: {result['trading_allowed']}")
    logger.info(f"Factor de volumen: {result['volume_factor']}")
    
    # Configurar escenario donde una protección no permite el trading
    protection.daily_loss = 600  # 6% de pérdida diaria (por encima del umbral de 5%)
    
    result = protection.check_all_protections(
        breakdown_percentage=10.0,
        max_drawdown_percentage=15.0,
        daily_loss_percentage=5.0,
        weekly_loss_percentage=10.0,
        monthly_loss_percentage=15.0,
        max_consecutive_losses=3,
        volume_reduction_factor=0.5
    )
    
    logger.info(f"Pérdida diaria excede el umbral: Trading permitido: {result['trading_allowed']}")
    if not result['trading_allowed']:
        logger.info(f"Razones: {result['reasons']}")

def main():
    """Función principal para ejecutar todas las pruebas."""
    logger.info("Iniciando pruebas de protecciones...")
    
    # Inicializar MetaTrader 5 si es necesario para algunas pruebas
    # Comentar si no se necesita o no está disponible
    # if not mt5.initialize():
    #     logger.error("Error al inicializar MetaTrader 5")
    #     return
    
    try:
        # Ejecutar pruebas
        test_breakdown_protection()
        test_max_drawdown_protection()
        test_daily_loss_limit()
        test_consecutive_losses_protection()
        test_time_based_restrictions()
        test_check_all_protections()
        
        logger.info("Todas las pruebas completadas.")
        
    except Exception as e:
        logger.error(f"Error durante las pruebas: {e}")
    
    finally:
        # Cerrar conexión con MetaTrader 5 si se inicializó
        # mt5.shutdown()
        pass

if __name__ == "__main__":
    main()