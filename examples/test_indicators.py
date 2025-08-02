# -*- coding: utf-8 -*-
"""
Script para probar los indicadores implementados.

Este script crea datos de prueba y verifica que los indicadores
implementados funcionen correctamente.
"""
import pandas as pd
import numpy as np
import logging
from indicators.Volume import Volume
from indicators.BillWilliams import BillWilliams
from indicators.Oscillator import Oscillator
from indicators.Trend import Trend

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def crear_datos_prueba(n_periodos=100):
    """Crea un DataFrame con datos de prueba para los indicadores."""
    # Crear fechas
    fechas = pd.date_range(start='2023-01-01', periods=n_periodos)
    
    # Crear precios simulados con tendencia alcista y algo de volatilidad
    close = np.linspace(100, 150, n_periodos) + np.random.normal(0, 5, n_periodos)
    high = close + np.random.uniform(1, 5, n_periodos)
    low = close - np.random.uniform(1, 5, n_periodos)
    open_price = close - np.random.uniform(-3, 3, n_periodos)
    
    # Crear volumen simulado
    volume = np.random.uniform(1000, 5000, n_periodos)
    
    # Crear DataFrame
    df = pd.DataFrame({
        'time': fechas,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    
    return df

def probar_indicadores_volumen():
    """Prueba los indicadores de volumen implementados."""
    logging.info("Probando indicadores de volumen...")
    
    # Crear datos de prueba
    df = crear_datos_prueba()
    
    # Crear instancia de Volume
    vol = Volume(df)
    
    # Probar OBV
    try:
        señal_obv = vol.obv()
        logging.info(f"OBV - Señal generada: {señal_obv}")
    except Exception as e:
        logging.error(f"Error al calcular OBV: {e}")
    
    # Probar VPT
    try:
        señal_vpt = vol.vpt()
        logging.info(f"VPT - Señal generada: {señal_vpt}")
    except Exception as e:
        logging.error(f"Error al calcular VPT: {e}")
    
    # Probar CMF
    try:
        señal_cmf = vol.cmf()
        logging.info(f"CMF - Señal generada: {señal_cmf}")
    except Exception as e:
        logging.error(f"Error al calcular CMF: {e}")
    
    # Probar MFI
    try:
        señal_mfi = vol.mfi()
        logging.info(f"MFI - Señal generada: {señal_mfi}")
    except Exception as e:
        logging.error(f"Error al calcular MFI: {e}")
    
    # Probar EOM
    try:
        señal_eom = vol.eom()
        logging.info(f"EOM - Señal generada: {señal_eom}")
    except Exception as e:
        logging.error(f"Error al calcular EOM: {e}")
    
    logging.info("Prueba de indicadores de volumen completada.")

def probar_indicadores_tendencia():
    """Prueba los indicadores de tendencia implementados."""
    logging.info("Probando indicadores de tendencia...")
    
    # Crear datos de prueba
    df = crear_datos_prueba()
    
    # Crear instancia de Trend
    trend = Trend(df)
    
    # Probar MACD
    try:
        señal_macd = trend.macd()
        logging.info(f"MACD - Señal generada: {señal_macd}")
    except Exception as e:
        logging.error(f"Error al calcular MACD: {e}")
    
    # Probar SMA
    try:
        señal_sma = trend.sma()
        logging.info(f"SMA - Señal generada: {señal_sma}")
    except Exception as e:
        logging.error(f"Error al calcular SMA: {e}")
    
    # Probar Triple SMA
    try:
        señal_triple_sma = trend.triple_sma()
        logging.info(f"Triple SMA - Señal generada: {señal_triple_sma}")
    except Exception as e:
        logging.error(f"Error al calcular Triple SMA: {e}")
    
    logging.info("Prueba de indicadores de tendencia completada.")

def probar_indicadores_oscillator():
    """Prueba los indicadores de oscilador implementados."""
    logging.info("Probando indicadores de oscilador...")
    
    # Crear datos de prueba
    df = crear_datos_prueba()
    
    # Crear instancia de Oscillator
    osc = Oscillator(df)
    
    # Probar Stochastic
    try:
        señal_stoch = osc.stochastic()
        logging.info(f"Stochastic - Señal generada: {señal_stoch}")
    except Exception as e:
        logging.error(f"Error al calcular Stochastic: {e}")
    
    # Probar RSI
    try:
        señal_rsi = osc.rsi()
        logging.info(f"RSI - Señal generada: {señal_rsi}")
    except Exception as e:
        logging.error(f"Error al calcular RSI: {e}")
    
    logging.info("Prueba de indicadores de oscilador completada.")

def probar_indicadores_billwilliams():
    """Prueba los indicadores de Bill Williams implementados."""
    logging.info("Probando indicadores de Bill Williams...")
    
    # Crear datos de prueba
    df = crear_datos_prueba()
    
    # Crear instancia de BillWilliams
    bw = BillWilliams(df)
    
    # Probar Alligator
    try:
        señal_alligator = bw.alligator()
        logging.info(f"Alligator - Señal generada: {señal_alligator}")
    except Exception as e:
        logging.error(f"Error al calcular Alligator: {e}")
    
    logging.info("Prueba de indicadores de Bill Williams completada.")

if __name__ == "__main__":
    logging.info("Iniciando pruebas de indicadores...")
    
    # Probar todos los indicadores
    probar_indicadores_volumen()
    probar_indicadores_tendencia()
    probar_indicadores_oscillator()
    probar_indicadores_billwilliams()
    
    logging.info("Todas las pruebas completadas.")