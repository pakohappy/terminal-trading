#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de Logging: Verifica que el sistema de logging funcione correctamente

Este script prueba el sistema de logging mejorado, verificando que:
1. La configuración del logging se carga correctamente
2. Los diferentes niveles de log funcionan como se espera
3. Los mensajes de log tienen el formato correcto
"""
import logging
from log.log_loader import setup_logging
from utils.robots.robot_advanced import AdvancedRobot
from utils.robots.robot_stochastic import StochasticRobot
from utils.robots.robot_triple_sma import TripleSMARobot

def test_logging():
    """
    Prueba el sistema de logging mejorado.
    """
    # Configurar el sistema de logging
    setup_logging()
    
    # Probar logging directo
    logging.debug("Este es un mensaje de DEBUG")
    logging.info("Este es un mensaje de INFO")
    logging.warning("Este es un mensaje de WARNING")
    logging.error("Este es un mensaje de ERROR")
    logging.critical("Este es un mensaje de CRITICAL")
    
    # Probar logging desde robots
    robot_advanced = AdvancedRobot()
    robot_stochastic = StochasticRobot()
    robot_triple_sma = TripleSMARobot()
    
    # Simular mensajes de log desde cada robot
    logging.info("=== Probando mensajes de log desde robots ===")
    
    # Estos mensajes deberían usar el formato estandarizado con el nombre de la clase
    # Simular mensajes de log directamente para evitar dependencias de MT5
    logging.info(f"{robot_advanced.__class__.__name__} - No hay signal que marque el cierre de la posición.")
    logging.info(f"{robot_stochastic.__class__.__name__} - No hay señal para abrir una segunda posición.")
    logging.info(f"{robot_triple_sma.__class__.__name__} - No hay signal que marque el cierre de la posición.")
    
    logging.info("=== Prueba de logging completada ===")

if __name__ == "__main__":
    test_logging()