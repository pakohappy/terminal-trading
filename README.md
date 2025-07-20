# Robot de Trading Automatizado basado en terminal

<p style="color: red; font-weight: bold;">
*** El trading automatizado conlleva riesgos. Este sistema se proporciona con fines educativos y no garantiza beneficios. Utilízalo bajo tu propia responsabilidad y siempre con precaución ***
</p>
## Introducción

Este repositorio contiene un sistema de trading automatizado diseñado para operar en los mercados financieros a través de MetaTrader 5. El sistema está compuesto por varios robots de trading a modo de ejemplo, que utilizan diferentes estrategias e indicadores técnicos para identificar oportunidades de compra y venta.

Los robots están diseñados para ser flexibles y configurables, permitiendo ajustar parámetros como el par de divisas, el marco temporal, los niveles de stop-loss y take-profit, y los parámetros específicos de cada indicador técnico.

## Estructura del Repositorio

El repositorio está organizado en las siguientes carpetas y archivos:

- **robot1.py, robot2.py, robot3.py**: Implementaciones de diferentes robots de trading a modo de ejemplo con estrategias distintas.
  - `robot1.py`: Utiliza el oscilador estocástico para generar señales.
  - `robot2.py`: Utiliza el indicador Triple SMA (Triple Simple Moving Average) para identificar tendencias.
  - `robot3.py`: Combina el indicador Triple SMA con el Alligator de Bill Williams (preparado para futuras mejoras).

- **indicators/**: Contiene las implementaciones de los indicadores técnicos utilizados por los robots.
  - `Oscillator.py`: Implementa el oscilador estocástico.
  - `Trend.py`: Implementa indicadores de tendencia como MACD y Triple SMA.
  - `BillWilliams.py`: Implementa el indicador Alligator de Bill Williams.
  - `Volume.py`: Preparado para implementar indicadores basados en volumen.

- **trading_platform/**: Contiene la integración con la plataforma de trading.
  - `Metaquotes.py`: Proporciona funciones para interactuar con MetaTrader 5.

- **strategy/**: Contiene componentes de estrategia adicionales.
  - `Protection.py`: Diseñado para implementar protecciones de capital.
  - `StopsDynamic.py`: Implementa estrategias de stop-loss dinámico.

- **log/**: Contiene la configuración y archivos de registro.
  - `log_loader.py`: Configuración del sistema de registro.
  - `logs/`: Directorio donde se almacenan los archivos de registro.

## Configuración del Robot de Trading

### Requisitos Previos

1. **Instalar MetaTrader 5**: Descarga e instala [MetaTrader 5](https://www.metatrader5.com/es/download).
2. **Instalar Python**: Asegúrate de tener Python 3.7 o superior instalado.
3. **Instalar Dependencias**: Instala las dependencias necesarias con pip:

```bash
pip install -r requirements.txt
```

3. **Configurar Logging**: El sistema utiliza un sistema de registro para monitorear la actividad. Los logs se almacenan en `log/logs/bot.log`.

## Creación de un Robot de Trading

Para crear tu propio robot de trading, puedes seguir estos pasos:

1. **Seleccionar una Estrategia**: Decide qué tipo de estrategia quieres implementar (tendencia, oscilador, etc.).
2. **Elegir Indicadores**: Selecciona los indicadores técnicos que utilizarás para generar señales.
3. **Implementar la Lógica de Trading**: Crea un nuevo archivo Python basado en uno de los robots existentes y modifica la lógica según tu estrategia.

### Ejemplo de Implementación Básica

```python
import time
import MetaTrader5 as mt5
from log.log_loader import setup_logging
from trading_platform.Metaquotes import Metaquotes as mtq
from indicators.Trend import Trend

# Configuración del robot
SYMBOL = 'EURUSD'
TIMEFRAME = mt5.TIMEFRAME_H1
VOLUME = 0.01
LAST_CANDLES = 20
PIPS_SL = 50
PIPS_TP = 100
DEVIATION = 20
COMMENT = "Mi Robot"

# Parámetros del indicador
PERIODO_LENTO = 20
PERIODO_MEDIO = 10
PERIODO_RAPIDO = 5
MODE = 0

# Configuración del logging
setup_logging()

def run():
    # Inicializar MetaTrader 5
    mtq.initialize_mt5()
    
    while True:
        # Verificar posiciones abiertas
        positions = mt5.positions_get(symbol=SYMBOL)
        
        # Si no hay posiciones, buscar oportunidades
        if positions is None or len(positions) == 0:
            # Obtener datos
            df = mtq.get_df(SYMBOL, TIMEFRAME, LAST_CANDLES)
            
            # Calcular indicador y obtener señal
            indicator = Trend(df)
            signal = indicator.triple_sma(PERIODO_LENTO, PERIODO_MEDIO, PERIODO_RAPIDO, MODE)
            
            # Abrir posiciones según la señal
            if signal == 2:  # Señal de compra
                mtq.open_order_buy(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
            elif signal == 1:  # Señal de venta
                mtq.open_order_sell(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
        
        # Pausa para evitar sobrecarga
        time.sleep(1)

if __name__ == "__main__":
    run()
```

## Implementación de Estrategias de Trading

### Estrategias Basadas en Osciladores

Los osciladores son indicadores técnicos que fluctúan entre dos valores extremos y pueden señalar condiciones de sobrecompra o sobreventa. El robot1.py utiliza el oscilador estocástico:

```python
# Crear una instancia del indicador Oscillator y calcular el estocástico
indicator = Oscillator(df)
signal = indicator.stochastic(K_PERIOD, D_PERIOD, SMOOTH_K, OVERBOUGHT_LEVEL, OVERSOLD_LEVEL, MODE)

# Interpretar la señal
if signal == 2:  # Señal de compra (cruce al alza en zona de sobreventa)
    mtq.open_order_buy(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
elif signal == 1:  # Señal de venta (cruce a la baja en zona de sobrecompra)
    mtq.open_order_sell(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
```

### Estrategias Basadas en Tendencias

Las estrategias basadas en tendencias buscan identificar y seguir la dirección del mercado. El robot2.py y robot3.py utilizan el indicador Triple SMA:

```python
# Crear una instancia del indicador Trend y calcular el Triple SMA
indicator = Trend(df)
signal = indicator.triple_sma(PERIODO_LENTO, PERIODO_MEDIO, PERIODO_RAPIDO, MODE)

# Interpretar la señal
if signal == 2:  # Señal de compra (alineación alcista: rápida > media > lenta)
    mtq.open_order_buy(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
elif signal == 1:  # Señal de venta (alineación bajista: rápida < media < lenta)
    mtq.open_order_sell(SYMBOL, VOLUME, signal, PIPS_SL, PIPS_TP, DEVIATION, COMMENT)
```

### Gestión de Posiciones

Es importante implementar una buena gestión de posiciones para proteger el capital y maximizar las ganancias:

```python
# Cerrar posiciones cuando la señal indica fin de tendencia
if position.type == 0 and signal_close == 1 or position.type == 1 and signal_close == 2:
    mtq.close_position(position)
```

### Stop-Loss Dinámico

El archivo `strategy/StopsDynamic.py` implementa una estrategia de stop-loss dinámico que ajusta el stop-loss a medida que el precio se mueve a favor de la posición:

```python
# Ejemplo de uso de stop-loss dinámico
PIP_SL_PARAM = 50
sldyn = StopsDynamic()
sldyn.sl_follower(PIP_SL_PARAM)
```

## Uso del Sistema

Para ejecutar uno de los robots de trading, simplemente ejecuta el archivo Python correspondiente:

```bash
python robot1.py  # Ejecutar el robot basado en el oscilador estocástico
python robot2.py  # Ejecutar el robot basado en Triple SMA
python robot3.py  # Ejecutar el robot basado en Triple SMA y Alligator
```

## Recomendaciones y Mejores Prácticas

1. **Pruebas en Modo Demo**: Siempre prueba tus estrategias en una cuenta demo antes de operar con dinero real.
2. **Backtesting**: Realizar backtesting de tus estrategias.
3. **Gestión de Riesgo**: Implementa una sólida gestión de riesgo limitando el tamaño de las posiciones y utilizando stop-loss.
4. **Monitoreo Continuo**: Revisa regularmente los logs para asegurarte de que el robot está funcionando correctamente.
5. **Mejora Continua**: Ajusta y mejora tus estrategias basándote en los resultados obtenidos.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar este sistema, puedes:

1. Implementar nuevos indicadores técnicos
2. Mejorar las estrategias existentes
3. Añadir nuevas funcionalidades de gestión de riesgo
4. Optimizar el rendimiento del sistema

## <span style="color: red;">Descargo de Responsabilidad</span>

<p style="color: red; font-weight: bold;">
El trading automatizado conlleva riesgos. Este sistema se proporciona con fines educativos y no garantiza beneficios. Utilízalo bajo tu propia responsabilidad y siempre con precaución.
</p>