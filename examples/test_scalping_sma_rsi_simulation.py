# -*- coding: utf-8 -*-
"""
Simulación del Robot de Scalping con Triple SMA y RSI

Este script simula el funcionamiento del robot de scalping sin ejecutar operaciones reales,
permitiendo verificar la lógica de trading y las señales generadas.
"""
import sys
import os
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
from log.log_loader import setup_logging
setup_logging()

# Importar los indicadores
from indicators.Trend import Trend
from indicators.Oscillator import Oscillator

def generate_sample_data(periods=200):
    """
    Genera datos de muestra para simular un mercado.
    
    Args:
        periods: Número de periodos a generar.
        
    Returns:
        pd.DataFrame: DataFrame con datos de mercado simulados.
    """
    # Crear fechas para los últimos 'periods' minutos
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=periods)
    dates = pd.date_range(start=start_time, end=end_time, periods=periods)
    
    # Generar precios simulados
    np.random.seed(42)  # Para reproducibilidad
    
    # Precio inicial
    initial_price = 1.10000  # Por ejemplo, para EURUSD
    
    # Generar movimientos aleatorios pero con cierta tendencia
    price_changes = np.random.normal(0, 0.0002, periods)  # Pequeños cambios aleatorios
    
    # Añadir tendencia (por ejemplo, alcista al principio, bajista al final)
    trend = np.concatenate([
        np.linspace(0.0001, 0.0003, periods // 3),  # Tendencia alcista
        np.linspace(0.0003, -0.0001, periods // 3),  # Transición
        np.linspace(-0.0001, -0.0003, periods - 2*(periods // 3))  # Tendencia bajista
    ])
    
    price_changes = price_changes + trend
    
    # Calcular precios
    prices = initial_price + np.cumsum(price_changes)
    
    # Crear DataFrame
    df = pd.DataFrame({
        'time': dates,
        'open': prices,
        'high': prices + np.random.uniform(0, 0.0005, periods),
        'low': prices - np.random.uniform(0, 0.0005, periods),
        'close': prices + np.random.normal(0, 0.0002, periods),
        'tick_volume': np.random.randint(10, 100, periods),
        'spread': np.random.randint(1, 5, periods),
        'real_volume': np.random.randint(1000, 10000, periods)
    })
    
    return df

def simulate_trading_signals():
    """
    Simula las señales de trading generadas por la estrategia de scalping.
    """
    logging.info("=== Iniciando simulación de Robot de Scalping con Triple SMA y RSI ===")
    
    # Generar datos de muestra
    df = generate_sample_data(periods=200)
    logging.info(f"Datos de muestra generados: {len(df)} periodos")
    
    # Cargar configuración
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "configs", "scalping_sma_rsi_default.json")
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Parámetros de la estrategia
    periodo_lento = config["periodo_lento"]
    periodo_medio = config["periodo_medio"]
    periodo_rapido = config["periodo_rapido"]
    periodo_rsi = config["periodo_rsi"]
    rsi_sobreventa = config["rsi_sobreventa"]
    rsi_sobrecompra = config["rsi_sobrecompra"]
    
    logging.info(f"Parámetros de la estrategia: SMA({periodo_rapido},{periodo_medio},{periodo_lento}), RSI({periodo_rsi})")
    
    # Calcular indicadores
    trend_indicator = Trend(df)
    oscillator_indicator = Oscillator(df)
    
    # Calcular Triple SMA
    sma_signals = []
    for i in range(len(df)):
        # Usar un subconjunto de datos hasta el índice actual para simular datos en tiempo real
        df_subset = df.iloc[:i+1].copy()
        
        # Solo calcular si tenemos suficientes datos
        if len(df_subset) > periodo_lento:
            trend_subset = Trend(df_subset)
            signal = trend_subset.triple_sma(periodo_lento, periodo_medio, periodo_rapido, 0)
            sma_signals.append(signal)
        else:
            sma_signals.append(0)  # Sin señal si no hay suficientes datos
    
    # Calcular RSI
    rsi_values = []
    for i in range(len(df)):
        # Usar un subconjunto de datos hasta el índice actual
        df_subset = df.iloc[:i+1].copy()
        
        # Solo calcular si tenemos suficientes datos
        if len(df_subset) > periodo_rsi:
            oscillator_subset = Oscillator(df_subset)
            rsi = oscillator_subset.rsi(periodo_rsi, rsi_sobrecompra, rsi_sobreventa, 0)
            rsi_values.append(rsi)
        else:
            rsi_values.append(50)  # Valor neutral si no hay suficientes datos
    
    # Combinar señales según la lógica de trading
    combined_signals = []
    positions = []  # 1 para posición larga, -1 para posición corta, 0 para sin posición
    current_position = 0
    
    for i in range(len(df)):
        signal = 0  # Por defecto, no operar
        
        # Solo considerar señales después de tener suficientes datos para ambos indicadores
        if i > max(periodo_lento, periodo_rsi):
            sma_signal = sma_signals[i]
            rsi_value = rsi_values[i]
            
            # Señal de compra: Triple SMA indica compra y RSI confirma (no sobrecomprado)
            if sma_signal == 2 and rsi_value < rsi_sobrecompra:
                signal = 2  # Compra
            
            # Señal de venta: Triple SMA indica venta y RSI confirma (no sobrevendido)
            elif sma_signal == 1 and rsi_value > rsi_sobreventa:
                signal = 1  # Venta
        
        combined_signals.append(signal)
        
        # Simular gestión de posiciones
        if current_position == 0:  # Sin posición
            if signal == 2:  # Señal de compra
                current_position = 1
                logging.info(f"[{df['time'].iloc[i]}] APERTURA POSICIÓN LARGA a {df['close'].iloc[i]:.5f}")
            elif signal == 1:  # Señal de venta
                current_position = -1
                logging.info(f"[{df['time'].iloc[i]}] APERTURA POSICIÓN CORTA a {df['close'].iloc[i]:.5f}")
        
        elif current_position == 1:  # Posición larga
            # Cerrar si hay señal de venta o RSI sobrecomprado
            if signal == 1 or rsi_values[i] >= rsi_sobrecompra:
                current_position = 0
                reason = "señal de venta" if signal == 1 else "RSI sobrecomprado"
                logging.info(f"[{df['time'].iloc[i]}] CIERRE POSICIÓN LARGA a {df['close'].iloc[i]:.5f} por {reason}")
        
        elif current_position == -1:  # Posición corta
            # Cerrar si hay señal de compra o RSI sobrevendido
            if signal == 2 or rsi_values[i] <= rsi_sobreventa:
                current_position = 0
                reason = "señal de compra" if signal == 2 else "RSI sobrevendido"
                logging.info(f"[{df['time'].iloc[i]}] CIERRE POSICIÓN CORTA a {df['close'].iloc[i]:.5f} por {reason}")
        
        positions.append(current_position)
    
    # Añadir resultados al DataFrame
    df['sma_signal'] = sma_signals
    df['rsi_value'] = rsi_values
    df['combined_signal'] = combined_signals
    df['position'] = positions
    
    # Calcular resultados
    trades = 0
    for i in range(1, len(positions)):
        if positions[i] != positions[i-1]:
            trades += 1
    
    logging.info(f"Simulación completada. Total de operaciones: {trades//2}")  # Dividir por 2 porque cada ciclo completo es apertura+cierre
    
    # Mostrar resumen de resultados
    logging.info("=== Resumen de la simulación ===")
    logging.info(f"Periodo analizado: {df['time'].iloc[0]} a {df['time'].iloc[-1]}")
    logging.info(f"Precio inicial: {df['close'].iloc[0]:.5f}, Precio final: {df['close'].iloc[-1]:.5f}")
    logging.info(f"Cambio de precio: {(df['close'].iloc[-1] - df['close'].iloc[0])*10000:.1f} pips")
    logging.info(f"Señales de compra generadas: {combined_signals.count(2)}")
    logging.info(f"Señales de venta generadas: {combined_signals.count(1)}")
    logging.info("=== Fin de la simulación ===")
    
    return df

if __name__ == "__main__":
    # Ejecutar la simulación
    result_df = simulate_trading_signals()
    
    # Guardar resultados para análisis posterior (opcional)
    result_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulation_results.csv")
    result_df.to_csv(result_file, index=False)
    logging.info(f"Resultados guardados en {result_file}")