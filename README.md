# Sistema de Trading Automatizado

Este proyecto implementa un sistema de trading automatizado que permite crear, configurar y ejecutar robots de trading con diferentes estrategias. El sistema está diseñado para interactuar con MetaTrader 5 y proporciona una arquitectura modular y extensible para implementar diversas estrategias de trading.

## Índice

1. [Instalación y Configuración](#instalación-y-configuración)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Creación de Robots](#creación-de-robots)
4. [Estrategias Disponibles](#estrategias-disponibles)
5. [Protecciones](#protecciones)
6. [Stops Dinámicos](#stops-dinámicos)
7. [Ejemplos de Uso](#ejemplos-de-uso)
8. [Configuración](#configuración)

## Instalación y Configuración

### Requisitos Previos

- Python 3.7 o superior
- MetaTrader 5 instalado y configurado
- Cuenta de trading (demo o real) en MetaTrader 5

### Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/tu-usuario/trading.git
   cd trading
   ```

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Asegúrate de que MetaTrader 5 esté en ejecución y hayas iniciado sesión en tu cuenta.

## Arquitectura del Sistema

El sistema está organizado en varios módulos:

- **Base (`utils/base/`)**: Contiene la clase base para todos los robots (`RobotBase`).
- **Factory (`utils/factory/`)**: Implementa el patrón Factory para crear robots (`RobotFactory`).
- **Robots (`utils/robots/`)**: Implementaciones específicas de robots con diferentes estrategias.
- **Indicadores (`indicators/`)**: Módulos para calcular indicadores técnicos (tendencia, osciladores, etc.).
- **Estrategias (`strategy/`)**: Componentes para gestión de riesgos y protecciones.
- **Plataforma de Trading (`trading_platform/`)**: Interfaz con MetaTrader 5.
- **Configuraciones (`configs/`)**: Archivos JSON con configuraciones predefinidas.
- **Ejemplos (`examples/`)**: Scripts de ejemplo para demostrar el uso del sistema.
- **Logs (`log/`)**: Sistema de registro para monitorear la actividad.

## Creación de Robots

### Usando la Factory

La forma más sencilla de crear un robot es utilizando la clase `RobotFactory`:

```python
from utils.factory.robot_factory import RobotFactory
import MetaTrader5 as mt5

# Crear un robot con configuración predeterminada
robot = RobotFactory.create_robot('scalping_sma_rsi')

# Crear un robot con parámetros personalizados
robot = RobotFactory.create_robot(
    'scalping_sma_rsi',
    symbol='EURUSD',
    timeframe=mt5.TIMEFRAME_M5,
    volume=0.02
)

# Crear un robot desde un archivo de configuración
robot = RobotFactory.create_robot_from_config('configs/scalping_sma_rsi_default.json')

# Ejecutar el robot
robot.run()
```

### Creando un Nuevo Robot

Para crear un nuevo robot personalizado:

1. Genera una plantilla:
   ```python
   from utils.factory.robot_factory import RobotFactory
   
   RobotFactory.generate_robot_template('MiNuevoRobot', 'utils/robots/mi_nuevo_robot.py')
   ```

2. Edita el archivo generado para implementar tu estrategia.

3. Registra el robot en la factory:
   ```python
   RobotFactory.register_robot_type('mi_nuevo_robot', 'utils.robots.mi_nuevo_robot.MiNuevoRobot')
   ```

4. Crea una configuración predeterminada:
   ```python
   default_config = {
       'symbol': 'EURUSD',
       'timeframe': mt5.TIMEFRAME_M15,
       'volume': 0.01,
       # Otros parámetros específicos de tu robot
   }
   RobotFactory.set_default_config('mi_nuevo_robot', default_config)
   ```

Para más detalles, consulta el [Manual de Creación de Robots](docs/manual_crear_robot.md).

## Estrategias Disponibles

El sistema incluye varias estrategias de trading implementadas:

### ScalpingSMARSIRobot

Estrategia de scalping que combina Triple SMA (Simple Moving Average) y RSI (Relative Strength Index):

- Utiliza tres medias móviles (rápida, media y lenta) para detectar tendencias.
- Confirma las señales con el RSI para evitar operar en condiciones de sobrecompra/sobreventa.
- Ideal para timeframes pequeños (M1, M5).

### TripleSMARobot

Estrategia basada únicamente en tres medias móviles:

- Genera señales de compra cuando la media rápida cruza por encima de la media y la lenta.
- Genera señales de venta cuando la media rápida cruza por debajo de la media y la lenta.
- Adecuada para seguir tendencias en timeframes más grandes.

### StochasticRobot

Estrategia basada en el oscilador estocástico:

- Genera señales de compra cuando el estocástico cruza hacia arriba desde la zona de sobreventa.
- Genera señales de venta cuando el estocástico cruza hacia abajo desde la zona de sobrecompra.
- Útil para mercados laterales o con rangos definidos.

### AdvancedRobot

Robot avanzado que combina múltiples indicadores y protecciones:

- Integra análisis de tendencia, osciladores y volumen.
- Implementa múltiples capas de protección.
- Gestión dinámica de posiciones.

## Protecciones

El sistema incluye varias protecciones para gestionar el riesgo:

### Protección por Breakdown

Detiene las operaciones cuando las pérdidas alcanzan un cierto porcentaje del capital inicial.

```python
from strategy.Protection import Protection

# Crear una instancia de Protection
protection = Protection()

# Actualizar información de la cuenta antes de verificar protecciones
protection.update_account_info()

# Verificar protección por breakdown
result = protection.breakdown(10.0)  # Detener si las pérdidas alcanzan el 10% del capital
if not result:
    print("Protección por breakdown activada - detener trading")
```

### Protección por Drawdown Máximo

Detiene el trading cuando el drawdown supera un porcentaje máximo.

```python
from strategy.Protection import Protection

protection = Protection()
protection.update_account_info()

# Verificar protección por drawdown máximo
result = protection.max_drawdown(15.0)  # Detener si el drawdown supera el 15%
if not result:
    print("Protección por drawdown máximo activada - detener trading")
```

### Límites de Pérdida por Período

Limita las pérdidas a un porcentaje máximo en diferentes períodos:

```python
from strategy.Protection import Protection

protection = Protection()
protection.update_account_info()

# Limitar pérdidas diarias al 5%
result = protection.daily_loss_limit(5.0)
if not result:
    print("Límite de pérdida diaria alcanzado")

# Limitar pérdidas semanales al 10%
result = protection.weekly_loss_limit(10.0)
if not result:
    print("Límite de pérdida semanal alcanzado")

# Limitar pérdidas mensuales al 15%
result = protection.monthly_loss_limit(15.0)
if not result:
    print("Límite de pérdida mensual alcanzado")
```

### Otras Protecciones

- **Protección por Pérdidas Consecutivas**: Reduce el tamaño de posición después de un número de pérdidas consecutivas.
- **Ajuste de Posición Basado en Volatilidad**: Ajusta el tamaño de posición según la volatilidad del mercado.
- **Protección por Correlación**: Evita abrir múltiples posiciones en instrumentos altamente correlacionados.
- **Restricciones Basadas en Tiempo**: Limita las operaciones a ciertos días y horas.

Para más detalles, consulta la [Documentación de Protecciones](docs/protecciones_trading.md).

## Stops Dinámicos

El sistema implementa stops dinámicos que se ajustan automáticamente:

### Stop Loss Follower

Mantiene el stop loss a una distancia fija del precio actual, permitiendo que "siga" al precio cuando se mueve favorablemente.

```python
from strategy.StopsDynamic import StopsDynamic

# Crear una instancia de StopsDynamic
stops_dynamic = StopsDynamic()

# Aplicar stop loss follower a todas las posiciones abiertas
# con una distancia de 50 pips
stops_dynamic.sl_follower(50)  # Stop loss a 50 pips del precio actual
```

### Stop Loss SMA

Utiliza una media móvil simple como nivel de stop loss, añadiendo un margen adicional en pips.

```python
from strategy.StopsDynamic import StopsDynamic

# Crear una instancia de StopsDynamic
stops_dynamic = StopsDynamic()

# Aplicar stop loss basado en SMA a todas las posiciones abiertas
# con un margen de 30 pips y una SMA de 20 periodos
stops_dynamic.sl_sma(30, 20)  # Stop loss a 30 pips por debajo/encima de la SMA de 20 periodos
```

Para más detalles, consulta la [Documentación de Stops](docs/stops_trading.md).

## Ejemplos de Uso

### Ejecutar un Robot Predefinido

```python
from utils.factory.robot_factory import RobotFactory
import MetaTrader5 as mt5

# Crear y ejecutar un robot de scalping
robot = RobotFactory.create_robot(
    'scalping_sma_rsi',
    symbol='EURUSD',
    timeframe=mt5.TIMEFRAME_M1,
    volume=0.01
)
robot.run()
```

### Simular una Estrategia

El sistema permite simular estrategias sin ejecutar operaciones reales:

```
# Ejecutar la simulación del robot de scalping desde la línea de comandos
python examples/test_scalping_sma_rsi_simulation.py
```

O desde un script Python:

```python
# Importar el módulo de simulación
import sys
import os

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la función de simulación
from examples.test_scalping_sma_rsi_simulation import simulate_trading_signals

# Ejecutar la simulación
result_df = simulate_trading_signals()
```

### Más Ejemplos

Explora la carpeta `examples/` para ver más ejemplos de uso:

- `test_robots.py`: Muestra cómo crear y ejecutar diferentes tipos de robots.
- `test_indicators.py`: Demuestra el uso de los indicadores técnicos.
- `protection_integration.py`: Ejemplo de integración de protecciones.
- `stops_integration.py`: Ejemplo de uso de stops dinámicos.

## Configuración

Las configuraciones de los robots se pueden guardar en archivos JSON en la carpeta `configs/`:

```json
{
    "robot_type": "scalping_sma_rsi",
    "symbol": "EURUSD",
    "timeframe": 1,
    "volume": 0.01,
    "last_candles": 100,
    "pips_sl": 20,
    "pips_tp": 30,
    "deviation": 10,
    "comment": "Scalping SMA RSI Robot",
    "periodo_lento": 50,
    "periodo_medio": 20,
    "periodo_rapido": 5,
    "periodo_rsi": 14,
    "rsi_sobreventa": 30,
    "rsi_sobrecompra": 70,
    "max_perdida_diaria": 2.0,
    "usar_sl_dinamico": true,
    "periodos_sl_sma": 10
}
```

Para cargar una configuración:

```python
robot = RobotFactory.create_robot_from_config('configs/scalping_sma_rsi_default.json')
```

---

## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -am 'Añadir nueva característica'`)
4. Haz push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un nuevo Pull Request

## Licencia

Este proyecto está licenciado bajo [tu licencia aquí].