# Protecciones para Trading

Este documento describe las diferentes protecciones implementadas en el módulo `Protection.py` para ayudar a gestionar el riesgo en operaciones de trading.

## Índice

1. [Introducción](#introducción)
2. [Tipos de Protecciones](#tipos-de-protecciones)
   - [Protección por Breakdown](#protección-por-breakdown)
   - [Protección por Drawdown Máximo](#protección-por-drawdown-máximo)
   - [Límites de Pérdida por Período](#límites-de-pérdida-por-período)
   - [Protección por Pérdidas Consecutivas](#protección-por-pérdidas-consecutivas)
   - [Ajuste de Posición Basado en Volatilidad](#ajuste-de-posición-basado-en-volatilidad)
   - [Protección por Correlación](#protección-por-correlación)
   - [Restricciones Basadas en Tiempo](#restricciones-basadas-en-tiempo)
3. [Integración con Robots de Trading](#integración-con-robots-de-trading)
4. [Ejemplos de Uso](#ejemplos-de-uso)
5. [Recomendaciones](#recomendaciones)

## Introducción

La gestión del riesgo es uno de los aspectos más importantes del trading. El módulo `Protection.py` implementa diversas estrategias de protección de capital que ayudan a limitar las pérdidas y preservar el capital del trader.

Estas protecciones pueden utilizarse de forma individual o combinada para crear un sistema de gestión de riesgos robusto y adaptado a las necesidades específicas de cada trader.

## Tipos de Protecciones

### Protección por Breakdown

Esta protección detiene las operaciones cuando las pérdidas alcanzan un cierto porcentaje del capital inicial.

**Parámetros:**
- `percentage`: Porcentaje de pérdida que activará la protección.

**Ejemplo:**
```python
from strategy.Protection import Protection

protection = Protection()
result = protection.breakdown(10.0)  # Detener si las pérdidas alcanzan el 10% del capital
```

### Protección por Drawdown Máximo

Detiene el trading cuando el drawdown (caída desde el balance máximo alcanzado) supera un porcentaje máximo.

**Parámetros:**
- `max_percentage`: Porcentaje máximo de drawdown permitido.

**Ejemplo:**
```python
from strategy.Protection import Protection

protection = Protection()
result = protection.max_drawdown(15.0)  # Detener si el drawdown supera el 15%
```

### Límites de Pérdida por Período

Estas protecciones limitan las pérdidas a un porcentaje máximo del balance inicial en diferentes períodos de tiempo.

#### Límite de Pérdida Diaria

**Parámetros:**
- `max_loss_percentage`: Porcentaje máximo de pérdida diaria permitido.

**Ejemplo:**
```python
from strategy.Protection import Protection

protection = Protection()
result = protection.daily_loss_limit(5.0)  # Limitar pérdidas diarias al 5%
```

#### Límite de Pérdida Semanal

**Parámetros:**
- `max_loss_percentage`: Porcentaje máximo de pérdida semanal permitido.

**Ejemplo:**
```python
from strategy.Protection import Protection

protection = Protection()
result = protection.weekly_loss_limit(10.0)  # Limitar pérdidas semanales al 10%
```

#### Límite de Pérdida Mensual

**Parámetros:**
- `max_loss_percentage`: Porcentaje máximo de pérdida mensual permitido.

**Ejemplo:**
```python
from strategy.Protection import Protection

protection = Protection()
result = protection.monthly_loss_limit(15.0)  # Limitar pérdidas mensuales al 15%
```

### Protección por Pérdidas Consecutivas

Reduce el tamaño de posición después de un número de pérdidas consecutivas.

**Parámetros:**
- `max_consecutive_losses`: Número máximo de pérdidas consecutivas permitidas.
- `volume_reduction_factor`: Factor de reducción del volumen (0.5 = 50% de reducción).

**Ejemplo:**
```python
from strategy.Protection import Protection

protection = Protection()
result = protection.consecutive_losses_protection(3, 0.5)  # Reducir volumen al 50% después de 3 pérdidas consecutivas
```

### Ajuste de Posición Basado en Volatilidad

Ajusta el tamaño de posición basado en la volatilidad del mercado. Reduce el tamaño cuando la volatilidad es alta y lo aumenta cuando es baja.

**Parámetros:**
- `symbol`: Símbolo del instrumento.
- `timeframe`: Marco temporal para el análisis.
- `lookback_periods`: Número de períodos para calcular la volatilidad.
- `max_volatility_multiplier`: Multiplicador máximo de volatilidad para reducir el tamaño.

**Ejemplo:**
```python
from strategy.Protection import Protection
import MetaTrader5 as mt5

protection = Protection()
result = protection.volatility_based_position_sizing('EURUSD', mt5.TIMEFRAME_H1, 20, 2.0)
```

### Protección por Correlación

Evita abrir múltiples posiciones en instrumentos altamente correlacionados.

**Parámetros:**
- `symbols`: Lista de símbolos a analizar.
- `timeframe`: Marco temporal para el análisis.
- `max_correlation`: Correlación máxima permitida entre instrumentos.
- `lookback_periods`: Número de períodos para calcular la correlación.

**Ejemplo:**
```python
from strategy.Protection import Protection
import MetaTrader5 as mt5

protection = Protection()
result = protection.correlation_protection(['EURUSD', 'GBPUSD', 'EURGBP'], mt5.TIMEFRAME_H1, 0.7, 50)
```

### Restricciones Basadas en Tiempo

Limita las operaciones a ciertos días de la semana y horas del día.

**Parámetros:**
- `allowed_hours`: Lista de tuplas con horas permitidas (inicio, fin) en formato 24h.
- `allowed_days`: Lista de días permitidos (0=lunes, 6=domingo).

**Ejemplo:**
```python
from strategy.Protection import Protection

protection = Protection()
# Solo operar de lunes a viernes entre las 8:00 y las 20:00
result = protection.time_based_restrictions([(8, 20)], [0, 1, 2, 3, 4])
```

## Integración con Robots de Trading

Para integrar estas protecciones en un robot de trading, se recomienda seguir estos pasos:

1. Crear una instancia de la clase `Protection` en el constructor del robot.
2. Implementar un método `check_protections()` que verifique todas las protecciones configuradas.
3. Llamar a este método antes de procesar cualquier señal de trading.
4. Ajustar el volumen de las operaciones según el factor de volumen calculado.
5. No procesar señales si el trading no está permitido.

Ejemplo de integración:

```python
from strategy.Protection import Protection
from utils.base.robot_base import RobotBase

class ProtectedRobot(RobotBase):
    def __init__(self, symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment):
        super().__init__(symbol, timeframe, volume, last_candles, pips_sl, pips_tp, deviation, comment)
        self.protection = Protection()
        
    def check_protections(self):
        protection_result = self.protection.check_all_protections(
            breakdown_percentage=10.0,
            max_drawdown_percentage=15.0,
            daily_loss_percentage=5.0
        )
        trading_allowed = protection_result['trading_allowed']
        volume_factor = protection_result['volume_factor']
        adjusted_volume = self.VOLUME * volume_factor
        return trading_allowed, adjusted_volume
        
    def process_signal(self, signal):
        trading_allowed, adjusted_volume = self.check_protections()
        if not trading_allowed:
            return
        # Procesar señal con volumen ajustado
```

## Ejemplos de Uso

En la carpeta `examples` se encuentra un ejemplo completo de integración de las protecciones con un robot de trading:

- `protection_integration.py`: Muestra cómo crear un robot con todas las protecciones integradas.

## Recomendaciones

1. **Configuración Personalizada**: Ajustar los parámetros de protección según el instrumento, estrategia y perfil de riesgo.
2. **Pruebas en Demo**: Probar las protecciones en una cuenta demo antes de utilizarlas en una cuenta real.
3. **Monitoreo Regular**: Revisar periódicamente el rendimiento de las protecciones y ajustar los parámetros si es necesario.
4. **Combinación de Protecciones**: Utilizar múltiples protecciones para crear un sistema de gestión de riesgos más robusto.
5. **Registro Detallado**: Activar el logging para registrar todas las acciones de protección y facilitar el análisis posterior.

Recuerda que ninguna protección es perfecta y que la gestión del riesgo debe ser parte de una estrategia de trading completa que incluya análisis de mercado, gestión de capital y disciplina emocional.