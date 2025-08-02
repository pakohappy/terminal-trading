# -*- coding: utf-8 -*-
"""
Test Robot Factory: Script para probar la implementación mejorada de RobotFactory

Este script prueba las diferentes formas de crear robots utilizando la nueva
implementación de RobotFactory, verificando que todas las funcionalidades
funcionen correctamente.
"""
import os
import MetaTrader5 as mt5
from utils.factory.robot_factory import RobotFactory

def test_create_robot_with_defaults():
    """Prueba la creación de un robot con parámetros predeterminados."""
    print("\n1. Creando robot estocástico con parámetros predeterminados...")
    robot = RobotFactory.create_robot('stochastic')
    print(f"Robot creado: {robot.__class__.__name__}")
    print(f"Parámetros: SYMBOL={robot.SYMBOL}, TIMEFRAME={robot.TIMEFRAME}, K_PERIOD={robot.K_PERIOD}")
    return robot

def test_create_robot_with_custom_params():
    """Prueba la creación de un robot con parámetros personalizados."""
    print("\n2. Creando robot Triple SMA con parámetros personalizados...")
    robot = RobotFactory.create_robot(
        'triple_sma',
        symbol='EURUSD',
        timeframe=mt5.TIMEFRAME_M15,
        periodo_lento=10,
        periodo_medio=5,
        periodo_rapido=3
    )
    print(f"Robot creado: {robot.__class__.__name__}")
    print(f"Parámetros: SYMBOL={robot.SYMBOL}, TIMEFRAME={robot.TIMEFRAME}")
    print(f"Períodos: lento={robot.PERIODO_LENTO}, medio={robot.PERIODO_MEDIO}, rápido={robot.PERIODO_RAPIDO}")
    return robot

def test_create_robot_from_config():
    """Prueba la creación de un robot desde un archivo de configuración."""
    config_path = 'configs/stochastic_custom.json'
    print(f"\n3. Creando robot desde configuración: {config_path}...")
    
    if not os.path.exists(config_path):
        print(f"Error: No se encontró el archivo de configuración: {config_path}")
        return None
    
    robot = RobotFactory.create_robot_from_config(config_path)
    print(f"Robot creado: {robot.__class__.__name__}")
    print(f"Parámetros: SYMBOL={robot.SYMBOL}, TIMEFRAME={robot.TIMEFRAME}, K_PERIOD={robot.K_PERIOD}")
    return robot

def test_save_and_load_config():
    """Prueba guardar una configuración y luego cargarla."""
    config_path = 'configs/test_config.json'
    print(f"\n4. Guardando y cargando configuración: {config_path}...")
    
    # Definir una configuración personalizada
    config = {
        'symbol': 'USDJPY',
        'timeframe': mt5.TIMEFRAME_H1,
        'pips_sl': 200,
        'pips_tp': 600,
        'k_period': 10,
        'd_period': 5
    }
    
    # Guardar la configuración
    RobotFactory.save_config('stochastic', config, config_path)
    print(f"Configuración guardada en: {config_path}")
    
    # Cargar la configuración
    robot = RobotFactory.create_robot_from_config(config_path)
    print(f"Robot creado: {robot.__class__.__name__}")
    print(f"Parámetros: SYMBOL={robot.SYMBOL}, TIMEFRAME={robot.TIMEFRAME}, K_PERIOD={robot.K_PERIOD}")
    
    # Limpiar el archivo de prueba
    if os.path.exists(config_path):
        os.remove(config_path)
        print(f"Archivo de configuración de prueba eliminado: {config_path}")
    
    return robot

def test_register_robot_type():
    """Prueba registrar un nuevo tipo de robot."""
    print("\n5. Registrando un nuevo tipo de robot...")
    
    # Verificar los tipos de robots disponibles antes
    print(f"Tipos de robots antes: {', '.join(RobotFactory._robot_types.keys())}")
    
    # Registrar un nuevo tipo (usando uno existente para la prueba)
    RobotFactory.register_robot_type('custom_stochastic', 'utils.robots.robot_stochastic.StochasticRobot')
    
    # Establecer configuración predeterminada
    default_config = {
        'symbol': 'GBPUSD',
        'timeframe': mt5.TIMEFRAME_M30,
        'volume': 0.02,
        'k_period': 12,
        'd_period': 6,
        'smooth_k': 2,
        'overbought_level': 75,
        'oversold_level': 25
    }
    RobotFactory.set_default_config('custom_stochastic', default_config)
    
    # Verificar los tipos de robots después
    print(f"Tipos de robots después: {', '.join(RobotFactory._robot_types.keys())}")
    
    # Crear un robot del nuevo tipo
    robot = RobotFactory.create_robot('custom_stochastic')
    print(f"Robot creado: {robot.__class__.__name__}")
    print(f"Parámetros: SYMBOL={robot.SYMBOL}, TIMEFRAME={robot.TIMEFRAME}, K_PERIOD={robot.K_PERIOD}")
    
    return robot

def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("=== PRUEBAS DE ROBOT FACTORY ===")
    
    test_create_robot_with_defaults()
    test_create_robot_with_custom_params()
    test_create_robot_from_config()
    test_save_and_load_config()
    test_register_robot_type()
    
    print("\n=== TODAS LAS PRUEBAS COMPLETADAS ===")

if __name__ == "__main__":
    run_all_tests()