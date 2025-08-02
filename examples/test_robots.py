# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la implementación de robots estandarizados

Este script crea instancias de los diferentes tipos de robots implementados
y verifica que se inicialicen correctamente con sus parámetros predeterminados
y personalizados. No ejecuta los robots, solo verifica su creación.
"""
import MetaTrader5 as mt5
from utils.factory import RobotFactory
from utils.base import RobotBase
from utils.robots import StochasticRobot
from utils.robots import TripleSMARobot
from utils.robots import AdvancedRobot

def test_robot_creation():
    """
    Prueba la creación de robots utilizando diferentes métodos.
    """
    print("=== Prueba de creación de robots ===")
    
    # Prueba 1: Crear robots directamente
    print("\n1. Creación directa de robots:")
    
    robot1 = StochasticRobot()
    print(f"  - StochasticRobot creado: {type(robot1).__name__}")
    print(f"    Symbol: {robot1.SYMBOL}, Timeframe: {robot1.TIMEFRAME}")
    print(f"    K_PERIOD: {robot1.K_PERIOD}, D_PERIOD: {robot1.D_PERIOD}")
    
    robot2 = TripleSMARobot(symbol='EURUSD')
    print(f"  - TripleSMARobot creado: {type(robot2).__name__}")
    print(f"    Symbol: {robot2.SYMBOL}, Timeframe: {robot2.TIMEFRAME}")
    print(f"    PERIODO_LENTO: {robot2.PERIODO_LENTO}, PERIODO_RAPIDO: {robot2.PERIODO_RAPIDO}")
    
    # Prueba 2: Crear robots utilizando métodos específicos del factory
    print("\n2. Creación de robots con métodos específicos del factory:")
    
    robot3 = RobotFactory.create_stochastic_robot(
        symbol='GBPUSD',
        k_period=10,
        d_period=5
    )
    print(f"  - StochasticRobot creado con factory: {type(robot3).__name__}")
    print(f"    Symbol: {robot3.SYMBOL}, Timeframe: {robot3.TIMEFRAME}")
    print(f"    K_PERIOD: {robot3.K_PERIOD}, D_PERIOD: {robot3.D_PERIOD}")
    
    robot4 = RobotFactory.create_advanced_robot(
        symbol='USDJPY',
        timeframe=mt5.TIMEFRAME_H1,
        pips_sl=200,
        pips_tp=600
    )
    print(f"  - AdvancedRobot creado con factory: {type(robot4).__name__}")
    print(f"    Symbol: {robot4.SYMBOL}, Timeframe: {robot4.TIMEFRAME}")
    print(f"    PIPS_SL: {robot4.PIPS_SL}, PIPS_TP: {robot4.PIPS_TP}")
    
    # Prueba 3: Crear robots utilizando el método genérico del factory
    print("\n3. Creación de robots con método genérico del factory:")
    
    robot5 = RobotFactory.create_robot(
        'triple_sma',
        symbol='AUDUSD',
        periodo_lento=12,
        periodo_medio=8,
        periodo_rapido=4
    )
    print(f"  - Robot creado con método genérico: {type(robot5).__name__}")
    print(f"    Symbol: {robot5.SYMBOL}, Timeframe: {robot5.TIMEFRAME}")
    print(f"    PERIODO_LENTO: {robot5.PERIODO_LENTO}, PERIODO_RAPIDO: {robot5.PERIODO_RAPIDO}")
    
    # Prueba 4: Verificar que todos los robots heredan de RobotBase
    print("\n4. Verificación de herencia:")
    robots = [robot1, robot2, robot3, robot4, robot5]
    for i, robot in enumerate(robots, 1):
        print(f"  - Robot {i} ({type(robot).__name__}) es instancia de RobotBase: {isinstance(robot, RobotBase)}")
    
    print("\n=== Pruebas completadas con éxito ===")

if __name__ == "__main__":
    test_robot_creation()