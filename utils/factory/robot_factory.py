# -*- coding: utf-8 -*-
"""
Robot Factory: Clase para simplificar la creación de robots de trading

Este módulo proporciona una clase factory que facilita la creación de diferentes
tipos de robots de trading, ocultando la complejidad de la instanciación y
configuración de cada tipo específico de robot.
"""
import os
import json
import importlib
import MetaTrader5 as mt5
from typing import Dict, Any, Type, Optional
from utils.base.robot_base import RobotBase

class RobotFactory:
    """
    Factory para crear diferentes tipos de robots de trading.
    
    Esta clase implementa el patrón de diseño Factory para simplificar la creación
    de diferentes tipos de robots de trading, proporcionando métodos para crear
    robots a partir de configuraciones predefinidas o personalizadas.
    """
    
    # Mapeo de tipos de robots a sus clases correspondientes
    _robot_types = {
        'stochastic': 'utils.robots.robot_stochastic.StochasticRobot',
        'triple_sma': 'utils.robots.robot_triple_sma.TripleSMARobot',
        'advanced': 'utils.robots.robot_advanced.AdvancedRobot'
    }
    
    # Configuraciones predeterminadas para cada tipo de robot
    _default_configs = {
        'stochastic': {
            'symbol': 'BTCUSD',
            'timeframe': mt5.TIMEFRAME_M5,
            'volume': 0.01,
            'last_candles': 30,
            'pips_sl': 50000,
            'pips_tp': 50000,
            'deviation': 100,
            'comment': "Stochastic Robot Order",
            'k_period': 5,
            'd_period': 3,
            'smooth_k': 3,
            'overbought_level': 80,
            'oversold_level': 20,
            'mode': 0
        },
        'triple_sma': {
            'symbol': 'BTCUSD',
            'timeframe': mt5.TIMEFRAME_H1,
            'volume': 0.01,
            'last_candles': 20,
            'pips_sl': 100000,
            'pips_tp': 100000,
            'deviation': 100,
            'comment': "Triple SMA Robot Order",
            'periodo_lento': 8,
            'periodo_medio': 6,
            'periodo_rapido': 4,
            'mode': 0
        },
        'advanced': {
            'symbol': 'USDJPY',
            'timeframe': mt5.TIMEFRAME_M5,
            'volume': 0.01,
            'last_candles': 20,
            'pips_sl': 100,
            'pips_tp': 500,
            'deviation': 100,
            'comment': "Advanced Robot Order",
            'periodo_lento': 8,
            'periodo_medio': 6,
            'periodo_rapido': 4,
            'mode_1': 0,
            'jaw_period': 13,
            'jaw_offset': 8,
            'teeth_period': 8,
            'teeth_offset': 5,
            'lips_period': 5,
            'lips_offset': 3,
            'drop_nan': True,
            'percentage': 20,
            'mode_2': 3
        }
    }
    
    @classmethod
    def register_robot_type(cls, robot_type: str, class_path: str) -> None:
        """
        Registra un nuevo tipo de robot en la factory.
        
        Args:
            robot_type: Identificador único para el tipo de robot.
            class_path: Ruta completa a la clase del robot (módulo.submodulo.Clase).
        """
        cls._robot_types[robot_type] = class_path
    
    @classmethod
    def set_default_config(cls, robot_type: str, config: Dict[str, Any]) -> None:
        """
        Establece o actualiza la configuración predeterminada para un tipo de robot.
        
        Args:
            robot_type: Tipo de robot para el que se establece la configuración.
            config: Diccionario con la configuración predeterminada.
        """
        cls._default_configs[robot_type] = config
    
    @classmethod
    def get_robot_class(cls, robot_type: str) -> Type[RobotBase]:
        """
        Obtiene la clase del robot a partir de su tipo.
        
        Args:
            robot_type: Tipo de robot a obtener.
            
        Returns:
            Type[RobotBase]: Clase del robot.
            
        Raises:
            ValueError: Si el tipo de robot no está registrado.
        """
        if robot_type not in cls._robot_types:
            raise ValueError(f"Tipo de robot no válido: {robot_type}. "
                             f"Los tipos válidos son: {', '.join(cls._robot_types.keys())}.")
        
        # Obtener la ruta de la clase
        class_path = cls._robot_types[robot_type]
        
        # Separar el módulo y el nombre de la clase
        module_path, class_name = class_path.rsplit('.', 1)
        
        # Importar el módulo dinámicamente
        module = importlib.import_module(module_path)
        
        # Obtener la clase del módulo
        robot_class = getattr(module, class_name)
        
        return robot_class
    
    @classmethod
    def create_robot(cls, robot_type: str, **kwargs) -> RobotBase:
        """
        Crea un robot de trading del tipo especificado con los parámetros proporcionados.
        
        Este método permite crear cualquier tipo de robot soportado especificando su
        tipo y proporcionando los parámetros necesarios como argumentos de palabra clave.
        Si no se proporcionan todos los parámetros, se utilizan los valores predeterminados.
        
        Args:
            robot_type: Tipo de robot a crear.
            **kwargs: Parámetros específicos para el tipo de robot seleccionado.
            
        Returns:
            RobotBase: Una instancia del robot del tipo especificado.
            
        Raises:
            ValueError: Si el tipo de robot especificado no es válido.
        """
        robot_type = robot_type.lower()
        
        # Obtener la configuración predeterminada para este tipo de robot
        if robot_type not in cls._default_configs:
            raise ValueError(f"No hay configuración predeterminada para el tipo de robot: {robot_type}")
        
        # Combinar la configuración predeterminada con los parámetros proporcionados
        config = cls._default_configs[robot_type].copy()
        config.update(kwargs)
        
        # Obtener la clase del robot
        robot_class = cls.get_robot_class(robot_type)
        
        # Crear y devolver una instancia del robot
        return robot_class(**config)
    
    @classmethod
    def create_robot_from_config(cls, config_path: str, **kwargs) -> RobotBase:
        """
        Crea un robot de trading a partir de un archivo de configuración JSON.
        
        Args:
            config_path: Ruta al archivo de configuración JSON.
            **kwargs: Parámetros adicionales que sobrescriben los del archivo.
            
        Returns:
            RobotBase: Una instancia del robot configurado.
            
        Raises:
            FileNotFoundError: Si el archivo de configuración no existe.
            ValueError: Si el archivo no contiene un tipo de robot válido.
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"No se encontró el archivo de configuración: {config_path}")
        
        # Cargar la configuración desde el archivo JSON
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Verificar que el archivo contiene el tipo de robot
        if 'robot_type' not in config:
            raise ValueError("El archivo de configuración debe contener el campo 'robot_type'")
        
        # Extraer el tipo de robot
        robot_type = config.pop('robot_type')
        
        # Actualizar la configuración con los parámetros adicionales
        config.update(kwargs)
        
        # Crear y devolver el robot
        return cls.create_robot(robot_type, **config)
    
    @classmethod
    def save_config(cls, robot_type: str, config: Dict[str, Any], config_path: str) -> None:
        """
        Guarda una configuración de robot en un archivo JSON.
        
        Args:
            robot_type: Tipo de robot.
            config: Diccionario con la configuración.
            config_path: Ruta donde guardar el archivo de configuración.
        """
        # Asegurarse de que el directorio existe
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        # Añadir el tipo de robot a la configuración
        full_config = {'robot_type': robot_type}
        full_config.update(config)
        
        # Guardar la configuración en formato JSON
        with open(config_path, 'w') as f:
            json.dump(full_config, f, indent=4)
    
    @classmethod
    def generate_robot_template(cls, template_name: str, output_path: str) -> None:
        """
        Genera un archivo de plantilla para un nuevo robot.
        
        Args:
            template_name: Nombre de la clase del nuevo robot.
            output_path: Ruta donde guardar el archivo de plantilla.
        """
        # Plantilla para un nuevo robot
        template = f'''# -*- coding: utf-8 -*-
"""
{template_name}: Implementación de estrategia personalizada de trading

Este robot implementa una estrategia de trading personalizada.
Describe aquí la estrategia y su funcionamiento.
"""
import MetaTrader5 as mt5
from utils.base.robot_base import RobotBase
# Importar los indicadores necesarios
# from indicators.Trend import Trend
# from indicators.Oscillator import Oscillator

class {template_name}(RobotBase):
    """
    Robot de trading que implementa una estrategia personalizada.
    
    Esta clase extiende RobotBase y define una estrategia específica
    para generar señales de trading.
    
    Attributes:
        PARAM1 (int): Descripción del parámetro 1.
        PARAM2 (int): Descripción del parámetro 2.
        # Añadir más atributos según sea necesario
    """
    
    def __init__(self, 
                 symbol: str = 'EURUSD', 
                 timeframe: int = mt5.TIMEFRAME_M15, 
                 volume: float = 0.01, 
                 last_candles: int = 30, 
                 pips_sl: int = 100, 
                 pips_tp: int = 200, 
                 deviation: int = 20, 
                 comment: str = "{template_name} Order",
                 # Parámetros específicos de la estrategia
                 param1: int = 10,
                 param2: int = 5):
        """
        Inicializa un nuevo robot con estrategia personalizada.
        
        Args:
            symbol: Par de divisas o instrumento a operar.
            timeframe: Marco temporal para el análisis.
            volume: Tamaño de la posición en lotes.
            last_candles: Número de velas a analizar.
            pips_sl: Stop Loss en pips.
            pips_tp: Take Profit en pips.
            deviation: Desviación máxima permitida del precio.
            comment: Comentario para identificar las órdenes.
            param1: Descripción del parámetro 1.
            param2: Descripción del parámetro 2.
            # Añadir más parámetros según sea necesario
        """
        super().__init__(symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment)
        
        # Inicializar parámetros específicos de la estrategia
        self.PARAM1 = param1
        self.PARAM2 = param2
        # Inicializar más parámetros según sea necesario
    
    def analyze_market(self, df):
        """
        Analiza el mercado utilizando la estrategia personalizada y genera señales de trading.
        
        Args:
            df: DataFrame con los datos de mercado.
            
        Returns:
            int: Señal de trading (2 para compra, 1 para venta, 0 para no operar).
        """
        # Implementar aquí la lógica de análisis del mercado
        # Ejemplo:
        # indicator = Trend(df)
        # signal = indicator.some_method(self.PARAM1, self.PARAM2)
        
        # Retornar una señal de ejemplo (reemplazar con la lógica real)
        return 0  # 0 significa no operar
    
    def manage_positions(self, positions):
        """
        Gestiona las posiciones abiertas utilizando la estrategia personalizada.
        
        Este método es opcional. Si no se sobrescribe, se utilizará el comportamiento
        predeterminado de la clase base.
        
        Args:
            positions: Lista de posiciones abiertas.
        """
        # Implementar aquí la lógica personalizada para gestionar posiciones
        # O llamar al método de la clase base para comportamiento estándar
        super().manage_positions(positions)


# Punto de entrada del programa
if __name__ == "__main__":
    # Crear una instancia del robot y ejecutarlo
    robot = {template_name}()
    robot.run()
'''
        
        # Asegurarse de que el directorio existe
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Guardar la plantilla en el archivo
        with open(output_path, 'w') as f:
            f.write(template)


# Ejemplo de uso
if __name__ == "__main__":
    # Crear un robot con parámetros predeterminados
    robot1 = RobotFactory.create_robot('stochastic')
    
    # Crear un robot con parámetros personalizados
    robot2 = RobotFactory.create_robot(
        'triple_sma',
        symbol='EURUSD',
        timeframe=mt5.TIMEFRAME_M15,
        periodo_lento=10,
        periodo_medio=5,
        periodo_rapido=3
    )
    
    # Guardar una configuración personalizada
    config = {
        'symbol': 'USDJPY',
        'timeframe': mt5.TIMEFRAME_H1,
        'pips_sl': 200,
        'pips_tp': 600
    }
    RobotFactory.save_config('advanced', config, 'configs/my_advanced_robot.json')
    
    # Generar una plantilla para un nuevo robot
    # RobotFactory.generate_robot_template('MyCustomRobot', 'utils/robots/my_custom_robot.py')
    
    # Ejecutar uno de los robots
    # robot1.run()