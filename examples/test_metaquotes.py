"""
Script de prueba para la clase Metaquotes mejorada.

Este script prueba la funcionalidad básica de la clase Metaquotes
para asegurar que las mejoras funcionan correctamente.
"""
import logging
import MetaTrader5 as mt5
from trading_platform.Metaquotes import Metaquotes

# Configurar el registro (logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_initialization():
    """Prueba los métodos de inicialización y cierre."""
    print("\n=== Probando Inicialización ===")
    
    # Probar is_initialized antes de la inicialización
    if not Metaquotes.is_initialized():
        print("MetaTrader 5 no está inicializado (como se esperaba)")
    
    # Probar inicialización
    result = Metaquotes.initialize_mt5()
    print(f"Resultado de inicialización: {result}")
    
    # Probar is_initialized después de la inicialización
    if Metaquotes.is_initialized():
        print("MetaTrader 5 ahora está inicializado")
    
    # No es necesario cerrar ya que lo usaremos para otras pruebas

def test_market_data():
    """Prueba la recuperación de datos de mercado."""
    print("\n=== Probando Recuperación de Datos de Mercado ===")
    
    # Asegurar que MT5 está inicializado
    if not Metaquotes.is_initialized():
        Metaquotes.initialize_mt5()
    
    # Probar get_df con un símbolo común
    symbol = "EURUSD"
    timeframe = mt5.TIMEFRAME_M5
    last_candles = 10
    
    df = Metaquotes.get_df(symbol, timeframe, last_candles)
    if not df.empty:
        print(f"Se recuperaron con éxito {len(df)} velas para {symbol}")
        print("Primeras filas:")
        print(df.head(3))
    else:
        print(f"Error al recuperar datos para {symbol}")

def test_account_info():
    """Prueba la recuperación de información de la cuenta."""
    print("\n=== Probando Información de la Cuenta ===")
    
    # Asegurar que MT5 está inicializado
    if not Metaquotes.is_initialized():
        Metaquotes.initialize_mt5()
    
    # Obtener información de la cuenta
    account_info = Metaquotes.get_account_info()
    if account_info:
        print("Información de la cuenta recuperada con éxito:")
        for key, value in account_info.items():
            print(f"  {key}: {value}")
    else:
        print("Error al recuperar información de la cuenta")

def test_symbol_info():
    """Prueba la recuperación de información del símbolo."""
    print("\n=== Probando Información del Símbolo ===")
    
    # Asegurar que MT5 está inicializado
    if not Metaquotes.is_initialized():
        Metaquotes.initialize_mt5()
    
    # Probar con un símbolo común
    symbol = "EURUSD"
    
    symbol_info = Metaquotes.get_symbol_info(symbol)
    if symbol_info:
        print(f"Información del símbolo para {symbol} recuperada con éxito:")
        for key, value in symbol_info.items():
            print(f"  {key}: {value}")
    else:
        print(f"Error al recuperar información del símbolo para {symbol}")

def test_positions():
    """Prueba la recuperación de posiciones."""
    print("\n=== Probando Recuperación de Posiciones ===")
    
    # Asegurar que MT5 está inicializado
    if not Metaquotes.is_initialized():
        Metaquotes.initialize_mt5()
    
    # Obtener todas las posiciones
    positions = Metaquotes.get_positions()
    print(f"Se encontraron {len(positions)} posiciones abiertas")
    
    # Si hay posiciones, mostrar detalles de la primera
    if positions:
        position = positions[0]
        print(f"Detalles de la primera posición:")
        print(f"  Símbolo: {position.symbol}")
        print(f"  Tipo: {'Compra' if position.type == 0 else 'Venta'}")
        print(f"  Volumen: {position.volume}")
        print(f"  Precio de apertura: {position.price_open}")
        print(f"  Precio actual: {position.price_current}")
        print(f"  Beneficio: {position.profit}")

def main():
    """Ejecutar todas las pruebas."""
    print("=== PRUEBAS DE LA CLASE METAQUOTES ===")
    
    try:
        # Ejecutar pruebas
        test_initialization()
        test_market_data()
        test_account_info()
        test_symbol_info()
        test_positions()
        
        print("\n=== Todas las pruebas completadas ===")
    finally:
        # Siempre cerrar MT5 al final
        if Metaquotes.is_initialized():
            Metaquotes.shutdown_mt5()
            print("Conexión con MetaTrader 5 cerrada")

if __name__ == "__main__":
    main()