# Manual Paso a Paso para Crear un Nuevo Robot de Trading

## Introducción

Este manual explica de manera detallada y explícita cómo crear un nuevo robot de trading utilizando las clases base `robot_base.py` y `robot_factory.py`. Seguir estos pasos te permitirá implementar tu propia estrategia de trading de forma estandarizada y modular.

## Índice

1. [Arquitectura del Sistema](#1-arquitectura-del-sistema)
2. [Preparación del Entorno](#2-preparación-del-entorno)
3. [Generación de la Plantilla del Robot](#3-generación-de-la-plantilla-del-robot)
4. [Implementación de la Estrategia](#4-implementación-de-la-estrategia)
5. [Registro del Robot en la Factory](#5-registro-del-robot-en-la-factory)
6. [Configuración del Robot](#6-configuración-del-robot)
7. [Prueba y Ejecución](#7-prueba-y-ejecución)
8. [Ejemplos Prácticos](#8-ejemplos-prácticos)

## 1. Arquitectura del Sistema

Antes de crear un nuevo robot, es importante entender la arquitectura del sistema:

- **RobotBase (`utils/base/robot_base.py`)**: Clase base que implementa la estructura común y el flujo de trabajo para todos los robots.
- **RobotFactory (`utils/factory/robot_factory.py`)**: Implementa el patrón Factory para simplificar la creación de robots.
- **Robots Específicos (`utils/robots/`)**: Clases que heredan de `RobotBase` e implementan estrategias específicas.
- **Configuraciones (`configs/`)**: Archivos JSON con configuraciones predefinidas y personalizadas.
- **Indicadores**: Módulos que calculan indicadores técnicos y generan señales de trading.

## 2. Preparación del Entorno

1. **Asegúrate de tener todas las dependencias instaladas**:
   ```
   pip install -r requirements.txt
   ```

2. **Verifica que MetaTrader 5 esté instalado y configurado correctamente**.

3. **Familiarízate con los indicadores disponibles** en la carpeta `indicators/`:
   - `Trend.py`: Indicadores de tendencia como medias móviles.
   - `Oscillator.py`: Osciladores como el Estocástico.
   - `BillWilliams.py`: Indicadores de Bill Williams como Alligator.
   - `Volume.py`: Indicadores basados en volumen.

## 3. Generación de la Plantilla del Robot

La forma más sencilla de crear un nuevo robot es utilizando el método `generate_robot_template` de la clase `RobotFactory`:

1. **Crea un script Python** (por ejemplo, `generate_my_robot.py`) con el siguiente contenido:

```python
from utils.factory.robot_factory import RobotFactory

# Generar una plantilla para un nuevo robot
# Parámetros: nombre de la clase, ruta del archivo
RobotFactory.generate_robot_template('MiNuevoRobot', 'utils/robots/mi_nuevo_robot.py')
```

2. **Ejecuta el script**:
```
python generate_my_robot.py
```

3. **Verifica que se ha creado el archivo** `utils/robots/mi_nuevo_robot.py` con la estructura básica del robot.

## 4. Implementación de la Estrategia

Ahora debes editar el archivo generado para implementar tu estrategia de trading:

1. **Abre el archivo** `utils/robots/mi_nuevo_robot.py` en tu editor de código.

2. **Personaliza los parámetros del constructor** según tu estrategia:

```python
import MetaTrader5 as mt5
from utils.base.robot_base import RobotBase

class MiNuevoRobot(RobotBase):
    def __init__(self, 
                symbol: str = 'EURUSD', 
                timeframe: int = mt5.TIMEFRAME_M15, 
                volume: float = 0.01, 
                last_candles: int = 30, 
                pips_sl: int = 100, 
                pips_tp: int = 200, 
                deviation: int = 20, 
                comment: str = "MiNuevoRobot Order",
                # Añade tus parámetros específicos
                periodo_rsi: int = 14,
                nivel_sobrecompra: int = 70,
                nivel_sobreventa: int = 30):
        """
        Inicializa un nuevo robot con tu estrategia personalizada.
        """
        super().__init__(symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment)
        
        # Inicializar parámetros específicos de tu estrategia
        self.PERIODO_RSI = periodo_rsi
        self.NIVEL_SOBRECOMPRA = nivel_sobrecompra
        self.NIVEL_SOBREVENTA = nivel_sobreventa
```

3. **Implementa el método `analyze_market()`** que es obligatorio:

```python
def analyze_market(self, df):
    """
    Analiza el mercado utilizando tu estrategia personalizada.
    
    Args:
        df: DataFrame con los datos de mercado.
        
    Returns:
        int: Señal de trading (2 para compra, 1 para venta, 0 para no operar).
    """
    # Importa los indicadores necesarios
    from indicators.Oscillator import Oscillator
    
    # Crea una instancia del indicador
    indicator = Oscillator(df)
    
    # Calcula el RSI
    rsi = indicator.rsi(self.PERIODO_RSI)
    
    # Obtén el último valor del RSI
    last_rsi = rsi.iloc[-1]
    
    # Genera señales basadas en el RSI
    if last_rsi < self.NIVEL_SOBREVENTA:
        return 2  # Señal de compra
    elif last_rsi > self.NIVEL_SOBRECOMPRA:
        return 1  # Señal de venta
    else:
        return 0  # No hay señal clara
```

4. **(Opcional) Personaliza el método `manage_positions()`** si necesitas una gestión específica de posiciones:

```python
def manage_positions(self, positions):
    """
    Gestiona las posiciones abiertas según tu estrategia.
    
    Args:
        positions: Lista de posiciones abiertas.
    """
    for position in positions:
        # Obtener datos actualizados
        df = self.get_market_data()
        
        # Importa los indicadores necesarios
        from indicators.Oscillator import Oscillator
        
        # Crea una instancia del indicador
        indicator = Oscillator(df)
        
        # Calcula el RSI
        rsi = indicator.rsi(self.PERIODO_RSI)
        
        # Obtén el último valor del RSI
        last_rsi = rsi.iloc[-1]
        
        # Cerrar posiciones basadas en condiciones específicas
        if position.type == 0 and last_rsi > 60:  # Posición de compra y RSI alto
            from trading_platform.Metaquotes import Metaquotes as mtq
            mtq.close_position(position)
        elif position.type == 1 and last_rsi < 40:  # Posición de venta y RSI bajo
            from trading_platform.Metaquotes import Metaquotes as mtq
            mtq.close_position(position)
```

## 5. Registro del Robot en la Factory

Para que tu robot pueda ser creado a través de la factory, debes registrarlo:

1. **Crea un script Python** (por ejemplo, `register_my_robot.py`) con el siguiente contenido:

```python
from utils.factory.robot_factory import RobotFactory
import MetaTrader5 as mt5

# Registrar el nuevo robot
RobotFactory.register_robot_type('mi_nuevo_robot', 'utils.robots.mi_nuevo_robot.MiNuevoRobot')

# Establecer configuración predeterminada
default_config = {
    'symbol': 'EURUSD',
    'timeframe': mt5.TIMEFRAME_M15,
    'volume': 0.01,
    'last_candles': 30,
    'pips_sl': 100,
    'pips_tp': 200,
    'deviation': 20,
    'comment': "MiNuevoRobot Order",
    'periodo_rsi': 14,
    'nivel_sobrecompra': 70,
    'nivel_sobreventa': 30
}
RobotFactory.set_default_config('mi_nuevo_robot', default_config)

print("Robot registrado correctamente en la factory.")
```

2. **Ejecuta el script**:
```
python register_my_robot.py
```

3. **Alternativa**: También puedes añadir tu robot directamente al diccionario `_robot_types` en `robot_factory.py`:

```python
# Mapeo de tipos de robots a sus clases correspondientes
_robot_types = {
    'stochastic': 'utils.robots.robot_stochastic.StochasticRobot',
    'triple_sma': 'utils.robots.robot_triple_sma.TripleSMARobot',
    'advanced': 'utils.robots.robot_advanced.AdvancedRobot',
    'mi_nuevo_robot': 'utils.robots.mi_nuevo_robot.MiNuevoRobot'  # Añade esta línea
}
```

## 6. Configuración del Robot

Puedes crear un archivo de configuración JSON para tu robot:

1. **Crea un archivo JSON** en la carpeta `configs/` (por ejemplo, `configs/mi_nuevo_robot_default.json`):

```json
{
    "robot_type": "mi_nuevo_robot",
    "symbol": "EURUSD",
    "timeframe": 16385,
    "volume": 0.01,
    "last_candles": 30,
    "pips_sl": 100,
    "pips_tp": 200,
    "deviation": 20,
    "comment": "MiNuevoRobot Order",
    "periodo_rsi": 14,
    "nivel_sobrecompra": 70,
    "nivel_sobreventa": 30
}
```

> Nota: Para el timeframe, usa los valores numéricos de MetaTrader 5:
> - TIMEFRAME_M1 = 1
> - TIMEFRAME_M5 = 5
> - TIMEFRAME_M15 = 15
> - TIMEFRAME_H1 = 16385
> - TIMEFRAME_H4 = 16388
> - TIMEFRAME_D1 = 16408

2. **Alternativa**: Puedes generar y guardar la configuración mediante código:

```python
from utils.factory.robot_factory import RobotFactory
import MetaTrader5 as mt5

# Definir una configuración personalizada
config = {
    'symbol': 'EURUSD',
    'timeframe': mt5.TIMEFRAME_M15,
    'volume': 0.01,
    'last_candles': 30,
    'pips_sl': 100,
    'pips_tp': 200,
    'deviation': 20,
    'comment': "MiNuevoRobot Order",
    'periodo_rsi': 14,
    'nivel_sobrecompra': 70,
    'nivel_sobreventa': 30
}

# Guardar la configuración en un archivo JSON
RobotFactory.save_config('mi_nuevo_robot', config, 'configs/mi_nuevo_robot_default.json')

print("Configuración guardada correctamente.")
```

## 7. Prueba y Ejecución

Ahora puedes crear y ejecutar tu robot:

1. **Crea un script Python** (por ejemplo, `run_my_robot.py`) con el siguiente contenido:

```python
from utils.factory.robot_factory import RobotFactory
import MetaTrader5 as mt5

# Método 1: Crear un robot con configuración predeterminada
robot = RobotFactory.create_robot('mi_nuevo_robot')

# Método 2: Crear un robot con parámetros personalizados
# robot = RobotFactory.create_robot(
#     'mi_nuevo_robot',
#     symbol='USDJPY',
#     timeframe=mt5.TIMEFRAME_M5,
#     periodo_rsi=7,
#     nivel_sobrecompra=80,
#     nivel_sobreventa=20
# )

# Método 3: Crear un robot desde un archivo de configuración
# robot = RobotFactory.create_robot_from_config('configs/mi_nuevo_robot_default.json')

# Ejecutar el robot
robot.run()
```

2. **Ejecuta el script**:
```
python run_my_robot.py
```

3. **Monitorea la ejecución** para verificar que el robot funciona correctamente.

## 8. Ejemplos Prácticos

### Ejemplo 1: Robot basado en RSI y Medias Móviles

```python
def analyze_market(self, df):
    """
    Analiza el mercado utilizando RSI y Medias Móviles.
    """
    from indicators.Oscillator import Oscillator
    from indicators.Trend import Trend
    
    # Calcular RSI
    osc = Oscillator(df)
    rsi = osc.rsi(self.PERIODO_RSI)
    
    # Calcular Medias Móviles
    trend = Trend(df)
    sma_rapida = trend.sma(self.PERIODO_RAPIDO)
    sma_lenta = trend.sma(self.PERIODO_LENTO)
    
    # Obtener últimos valores
    last_rsi = rsi.iloc[-1]
    last_sma_rapida = sma_rapida.iloc[-1]
    last_sma_lenta = sma_lenta.iloc[-1]
    
    # Generar señales
    if last_rsi < self.NIVEL_SOBREVENTA and last_sma_rapida > last_sma_lenta:
        return 2  # Señal de compra
    elif last_rsi > self.NIVEL_SOBRECOMPRA and last_sma_rapida < last_sma_lenta:
        return 1  # Señal de venta
    else:
        return 0  # No hay señal clara
```

### Ejemplo 2: Robot basado en Bandas de Bollinger

```python
def analyze_market(self, df):
    """
    Analiza el mercado utilizando Bandas de Bollinger.
    """
    from indicators.Trend import Trend
    
    # Calcular Bandas de Bollinger
    trend = Trend(df)
    upper, middle, lower = trend.bollinger_bands(self.PERIODO_BB, self.DESVIACIONES_BB)
    
    # Obtener último precio de cierre
    last_close = df['close'].iloc[-1]
    
    # Obtener últimos valores de las bandas
    last_upper = upper.iloc[-1]
    last_lower = lower.iloc[-1]
    
    # Generar señales
    if last_close < last_lower:
        return 2  # Señal de compra (precio por debajo de la banda inferior)
    elif last_close > last_upper:
        return 1  # Señal de venta (precio por encima de la banda superior)
    else:
        return 0  # No hay señal clara (precio entre las bandas)
```

---

## Conclusión

Siguiendo este manual paso a paso, has aprendido a crear un nuevo robot de trading utilizando la arquitectura estandarizada del sistema. Recuerda que puedes personalizar tu robot según tus necesidades específicas y combinar diferentes indicadores para crear estrategias más complejas.

Para obtener más información sobre los indicadores disponibles y sus parámetros, consulta la documentación en la carpeta `indicators/`.

¡Buena suerte con tus operaciones de trading!