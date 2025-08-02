# -*- coding: utf-8 -*-
"""
Ejemplo de uso del Robot de Scalping con Triple SMA y RSI

Este script muestra cómo crear y ejecutar un robot de scalping que utiliza
tres medias móviles simples (SMA) y el indicador RSI para operar en periodos
de 1 minuto con protección de pérdidas.
"""
import sys
import os
import json
import logging
import MetaTrader5 as mt5
from log.log_loader import setup_logging

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar el robot y la fábrica de robots
from utils.robots.robot_scalping_sma_rsi import ScalpingSMARSIRobot
from utils.factory.robot_factory import RobotFactory

def load_config(config_file):
    """
    Carga la configuración desde un archivo JSON.
    
    Args:
        config_file: Ruta al archivo de configuración.
        
    Returns:
        dict: Diccionario con la configuración.
    """
    with open(config_file, 'r') as f:
        return json.load(f)

def run_robot_from_config():
    """
    Crea y ejecuta un robot de scalping a partir de un archivo de configuración.
    """
    # Configurar logging
    setup_logging()
    logging.info("=== Iniciando ejemplo de Robot de Scalping con Triple SMA y RSI ===")
    
    # Cargar configuración
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "configs", "scalping_sma_rsi_default.json")
    config = load_config(config_file)
    
    # Convertir timeframe de entero a constante de MT5
    timeframe_map = {
        1: mt5.TIMEFRAME_M1,
        5: mt5.TIMEFRAME_M5,
        15: mt5.TIMEFRAME_M15,
        30: mt5.TIMEFRAME_M30,
        60: mt5.TIMEFRAME_H1,
        240: mt5.TIMEFRAME_H4,
        1440: mt5.TIMEFRAME_D1
    }
    
    # Crear el robot directamente
    robot = ScalpingSMARSIRobot(
        symbol=config["symbol"],
        timeframe=timeframe_map.get(config["timeframe"], mt5.TIMEFRAME_M1),
        volume=config["volume"],
        last_candles=config["last_candles"],
        pips_sl=config["pips_sl"],
        pips_tp=config["pips_tp"],
        deviation=config["deviation"],
        comment=config["comment"],
        periodo_lento=config["periodo_lento"],
        periodo_medio=config["periodo_medio"],
        periodo_rapido=config["periodo_rapido"],
        periodo_rsi=config["periodo_rsi"],
        rsi_sobreventa=config["rsi_sobreventa"],
        rsi_sobrecompra=config["rsi_sobrecompra"],
        max_perdida_diaria=config["max_perdida_diaria"],
        usar_sl_dinamico=config["usar_sl_dinamico"],
        periodos_sl_sma=config["periodos_sl_sma"]
    )
    
    logging.info(f"Robot creado para el símbolo {config['symbol']} en timeframe M{config['timeframe']}")
    
    # Ejecutar el robot
    try:
        robot.run()
    except KeyboardInterrupt:
        logging.info("Robot detenido por el usuario")
    except Exception as e:
        logging.error(f"Error al ejecutar el robot: {str(e)}")
    finally:
        logging.info("=== Finalizando ejemplo de Robot de Scalping con Triple SMA y RSI ===")

def run_robot_from_factory():
    """
    Crea y ejecuta un robot de scalping utilizando la fábrica de robots.
    """
    # Configurar logging
    setup_logging()
    logging.info("=== Iniciando ejemplo de Robot de Scalping con Triple SMA y RSI (Factory) ===")
    
    # Crear la fábrica de robots
    factory = RobotFactory()
    
    # Registrar el nuevo tipo de robot
    factory.register_robot_type("scalping_sma_rsi", ScalpingSMARSIRobot)
    
    # Cargar configuración
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "configs", "scalping_sma_rsi_default.json")
    
    # Crear el robot a través de la fábrica
    robot = factory.create_robot_from_config("scalping_sma_rsi", config_file)
    
    logging.info(f"Robot creado a través de la fábrica")
    
    # Ejecutar el robot
    try:
        robot.run()
    except KeyboardInterrupt:
        logging.info("Robot detenido por el usuario")
    except Exception as e:
        logging.error(f"Error al ejecutar el robot: {str(e)}")
    finally:
        logging.info("=== Finalizando ejemplo de Robot de Scalping con Triple SMA y RSI (Factory) ===")

if __name__ == "__main__":
    # Puedes elegir entre ejecutar el robot directamente desde la configuración
    # o utilizando la fábrica de robots
    
    # Opción 1: Crear y ejecutar el robot directamente desde la configuración
    run_robot_from_config()
    
    # Opción 2: Crear y ejecutar el robot utilizando la fábrica de robots
    # run_robot_from_factory()