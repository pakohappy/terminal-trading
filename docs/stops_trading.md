# Stops en Trading

Este documento describe los diferentes tipos de stops utilizados en trading, su implementación en el módulo `StopsDynamic.py` y cómo pueden integrarse tanto dentro como fuera de un robot de trading.

## Índice

1. [Introducción](#introducción)
2. [Tipos de Stops](#tipos-de-stops)
   - [Stop Loss](#stop-loss)
   - [Take Profit](#take-profit)
   - [Trailing Stop](#trailing-stop)
3. [Stops Dinámicos](#stops-dinámicos)
   - [Stop Loss Follower](#stop-loss-follower)
   - [Stop Loss SMA](#stop-loss-sma)
4. [Uso de Stops en Robots](#uso-de-stops-en-robots)
5. [Uso de Stops Fuera de Robots](#uso-de-stops-fuera-de-robots)
6. [Ejemplos de Integración](#ejemplos-de-integración)
7. [Recomendaciones](#recomendaciones)

## Introducción

Los stops son órdenes condicionadas que se utilizan en trading para limitar pérdidas o asegurar ganancias. Son una parte fundamental de la gestión del riesgo y pueden marcar la diferencia entre un sistema de trading rentable y uno que no lo es.

El módulo `StopsDynamic.py` implementa estrategias de stops dinámicos que se ajustan automáticamente a medida que el precio se mueve, proporcionando una gestión de riesgo más efectiva que los stops estáticos tradicionales.

## Tipos de Stops

### Stop Loss

El Stop Loss (SL) es una orden que cierra automáticamente una posición cuando el precio alcanza un nivel predeterminado, limitando así las pérdidas potenciales.

**Características:**
- Limita el riesgo por operación
- Protege el capital del trader
- Elimina la toma de decisiones emocionales

**Ejemplo básico:**
```python
# Establecer un stop loss a 50 pips del precio de entrada
# Ejemplo conceptual
import MetaTrader5 as mt5

# Obtener información de la posición
ticket_id = 12345  # ID de la posición
position = mt5.positions_get(ticket=ticket_id)[0]
symbol_info = mt5.symbol_info(position.symbol)

# Calcular niveles de stop loss
stop_loss_buy = position.price_open - (50 * symbol_info.point)  # Para una posición larga
stop_loss_sell = position.price_open + (50 * symbol_info.point)  # Para una posición corta
```

### Take Profit

El Take Profit (TP) es una orden que cierra automáticamente una posición cuando el precio alcanza un nivel de beneficio predeterminado, asegurando así las ganancias.

**Características:**
- Asegura beneficios cuando se alcanza un objetivo
- Elimina la codicia en la toma de decisiones
- Permite una gestión automatizada de las operaciones

**Ejemplo básico:**
```python
# Establecer un take profit a 100 pips del precio de entrada
# Ejemplo conceptual
import MetaTrader5 as mt5

# Obtener información de la posición
ticket_id = 12345  # ID de la posición
position = mt5.positions_get(ticket=ticket_id)[0]
symbol_info = mt5.symbol_info(position.symbol)

# Calcular niveles de take profit
take_profit_buy = position.price_open + (100 * symbol_info.point)  # Para una posición larga
take_profit_sell = position.price_open - (100 * symbol_info.point)  # Para una posición corta
```

### Trailing Stop

El Trailing Stop es un tipo de stop loss dinámico que "sigue" al precio a medida que se mueve favorablemente, manteniendo una distancia fija. Si el precio retrocede, el stop se mantiene en su posición.

**Características:**
- Protege las ganancias acumuladas
- Permite que las operaciones rentables continúen desarrollándose
- Se ajusta automáticamente a la volatilidad del mercado

**Ejemplo conceptual:**
```
Precio de entrada: 1.2000
Trailing stop inicial (50 pips): 1.1950

Si el precio sube a 1.2100:
  Nuevo trailing stop: 1.2050

Si el precio sube a 1.2200:
  Nuevo trailing stop: 1.2150

Si el precio baja a 1.2150:
  Trailing stop se mantiene en 1.2150
```

## Stops Dinámicos

Los stops dinámicos son aquellos que se ajustan automáticamente según las condiciones del mercado, proporcionando una protección más adaptativa que los stops estáticos.

### Stop Loss Follower

El Stop Loss Follower implementado en `StopsDynamic.py` es una variante del trailing stop que mantiene el stop loss a una distancia fija del precio actual, permitiendo que el stop "siga" al precio cuando este se mueve favorablemente.

**Características:**
- Mantiene una distancia fija (en pips) entre el precio actual y el stop loss
- El stop loss nunca retrocede, solo avanza en la dirección favorable
- Si no hay stop loss establecido, utiliza el precio de apertura como referencia

**Ejemplo de uso:**
```python
from strategy.StopsDynamic import StopsDynamic

# Crear instancia
stops = StopsDynamic()

# Aplicar estrategia follower con 50 pips
stops.sl_follower(50)
```

**Funcionamiento interno:**
1. Obtiene todas las posiciones abiertas
2. Para cada posición:
   - Si es una compra (BUY), coloca el SL a X pips por debajo del precio actual
   - Si es una venta (SELL), coloca el SL a X pips por encima del precio actual
   - Si el nuevo SL es menos favorable que el actual, mantiene el actual
3. Envía la orden para actualizar el stop loss

### Stop Loss SMA

El Stop Loss SMA utiliza una media móvil simple (SMA) como nivel de stop loss, añadiendo un margen adicional en pips. Esta estrategia permite que el stop loss se ajuste según la tendencia del mercado.

**Características:**
- Utiliza una SMA como referencia para el nivel de stop loss
- Añade un margen adicional en pips para evitar salidas prematuras
- Se adapta a la tendencia del mercado
- El stop loss nunca retrocede, solo avanza en la dirección favorable

**Ejemplo de uso:**
```python
from strategy.StopsDynamic import StopsDynamic

# Crear instancia
stops = StopsDynamic()

# Aplicar estrategia SMA con 20 periodos y 30 pips de margen
stops.sl_sma(30, 20)
```

**Funcionamiento interno:**
1. Obtiene todas las posiciones abiertas
2. Para cada posición:
   - Calcula la SMA con el número de periodos especificado
   - Si es una compra (BUY), coloca el SL a X pips por debajo de la SMA
   - Si es una venta (SELL), coloca el SL a X pips por encima de la SMA
   - Si el nuevo SL es menos favorable que el actual, mantiene el actual
3. Envía la orden para actualizar el stop loss

## Uso de Stops en Robots

Los stops dinámicos pueden integrarse fácilmente en robots de trading para mejorar su gestión del riesgo. A continuación, se describe cómo hacerlo:

### Integración en el Constructor

```python
from strategy.StopsDynamic import StopsDynamic
from utils.base.robot_base import RobotBase

class MyRobot(RobotBase):
    def __init__(self, symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment):
        super().__init__(symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment)
        # Inicializar el módulo de stops dinámicos
        self.stops = StopsDynamic()
```

### Implementación en el Bucle Principal

```python
def run(self):
    # Inicializar la conexión con MetaTrader 5
    self.initialize()
    
    # Bucle principal de trading
    while True:
        try:
            # Verificar posiciones abiertas
            has_positions, positions = self.check_open_positions()
            
            # Si hay posiciones, aplicar stops dinámicos
            if has_positions:
                # Aplicar stop loss follower con 50 pips
                self.stops.sl_follower(50)
                # O aplicar stop loss SMA con 20 periodos y 30 pips
                # self.stops.sl_sma(30, 20)
            
            # Resto de la lógica del robot...
            
        except Exception as e:
            import logging
            import time
            logging.error(f"Error en el bucle principal: {e}")
            time.sleep(5)
            continue
```

### Ventajas de la Integración en Robots

1. **Automatización completa**: Los stops se gestionan automáticamente sin intervención manual.
2. **Consistencia**: Se aplica la misma estrategia de stops a todas las operaciones.
3. **Eficiencia**: El robot puede ajustar los stops en tiempo real según las condiciones del mercado.
4. **Gestión integral**: Se integra con otras funcionalidades del robot como la entrada y salida de posiciones.

## Uso de Stops Fuera de Robots

Los stops dinámicos también pueden utilizarse de forma independiente, fuera de un robot de trading, para gestionar posiciones abiertas manualmente o por otros sistemas.

### Como Script Independiente

El módulo `StopsDynamic.py` puede ejecutarse como un script independiente que monitorea y ajusta continuamente los stops de todas las posiciones abiertas.

**Uso desde línea de comandos:**
```
python StopsDynamic.py --estrategia follower --pips 50
python StopsDynamic.py --estrategia sma --pips 30 --periodos 20
python StopsDynamic.py --help
```

**Parámetros disponibles:**
- `--estrategia`: Estrategia a utilizar (follower o sma)
- `--pips`: Distancia en pips para el stop loss
- `--periodos`: Periodos para la SMA (solo para estrategia sma)
- `--intervalo`: Intervalo en segundos entre iteraciones
- `--debug`: Activar modo debug (logging más detallado)

### Ventajas del Uso Independiente

1. **Flexibilidad**: Puede aplicarse a posiciones abiertas por cualquier método (manual o automatizado).
2. **Simplicidad**: No requiere modificar los sistemas de trading existentes.
3. **Complementario**: Puede utilizarse junto con otros scripts o herramientas.
4. **Adaptabilidad**: Puede ajustarse fácilmente a diferentes condiciones de mercado cambiando los parámetros.

## Ejemplos de Integración

En la carpeta `examples` se encuentra un ejemplo completo de integración de los stops dinámicos:

- `stops_integration.py`: Muestra cómo integrar los stops dinámicos en un robot de trading.

Este ejemplo demuestra:
- Cómo inicializar el módulo de stops dinámicos
- Cómo configurar diferentes estrategias de stops
- Cómo aplicar los stops a las posiciones abiertas
- Cómo manejar errores y excepciones

## Recomendaciones

1. **Ajuste de Parámetros**: Experimentar con diferentes valores de pips y periodos para encontrar la configuración óptima para cada instrumento y estrategia.

2. **Combinación de Estrategias**: Considerar la posibilidad de alternar entre diferentes estrategias de stops según las condiciones del mercado.

3. **Backtesting**: Probar las estrategias de stops en datos históricos para evaluar su rendimiento antes de utilizarlas en trading real.

4. **Monitoreo**: Aunque los stops dinámicos son automáticos, es importante monitorear su comportamiento regularmente para asegurarse de que funcionan como se espera.

5. **Adaptación**: Ajustar los parámetros de los stops según la volatilidad del mercado. Mercados más volátiles pueden requerir stops más amplios.

6. **Documentación**: Mantener un registro de las configuraciones de stops utilizadas y sus resultados para mejorar continuamente la estrategia.

7. **Integración con Protecciones**: Considerar la integración de los stops dinámicos con otras protecciones como las implementadas en el módulo `Protection.py` para una gestión de riesgos más completa.

Recuerda que los stops son solo una parte de una estrategia de trading completa. Deben utilizarse en conjunto con un buen análisis de mercado, gestión de capital y disciplina emocional para maximizar las probabilidades de éxito en el trading.