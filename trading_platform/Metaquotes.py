"""
-*- coding: utf-8 -*-
Módulo de Interfaz para la Plataforma MetaQuotes

Este módulo proporciona una interfaz estandarizada para interactuar con la plataforma MetaTrader 5.
Gestiona la inicialización, recuperación de datos y operaciones de gestión de órdenes.
"""
import MetaTrader5 as mt5
import logging
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional, Union

class Metaquotes:
    """
    Una clase que proporciona acceso estandarizado a la plataforma MetaTrader 5.
    
    Esta clase encapsula todas las interacciones con la plataforma MetaTrader 5,
    proporcionando métodos para inicialización, recuperación de datos y gestión de órdenes.
    """
    
    # Números mágicos predeterminados para diferentes tipos de órdenes
    DEFAULT_MAGIC_BUY = 235711
    DEFAULT_MAGIC_SELL = 235712
    DEFAULT_MAGIC_CLOSE = 2357
    
    # Zona horaria predeterminada para la conversión de tiempo
    DEFAULT_TIMEZONE = 'Europe/Madrid'
    
    @staticmethod
    def is_initialized() -> bool:
        """
        Verifica si el terminal MetaTrader 5 ya está inicializado.
        
        Returns:
            bool: True si MetaTrader 5 está inicializado, False en caso contrario.
        """
        return mt5.terminal_info() is not None
    
    @staticmethod
    def initialize_mt5() -> bool:
        """
        Inicializa la conexión con MetaTrader 5.
        
        Returns:
            bool: True si la inicialización fue exitosa, False en caso contrario.
        """
        if Metaquotes.is_initialized():
            logging.info("MetaTrader 5 ya está inicializado.")
            return True
            
        if not mt5.initialize():
            error_code = mt5.last_error()
            logging.error(f"Error al inicializar MetaTrader 5, código de error = {error_code}")
            return False
        
        logging.info("MetaTrader 5 inicializado correctamente.")
        return True
    
    @staticmethod
    def shutdown_mt5() -> None:
        """
        Cierra la conexión con MetaTrader 5.
        """
        mt5.shutdown()
        logging.info("Conexión con MetaTrader 5 cerrada.")
    
    @staticmethod
    def get_df(symbol: str, timeframe: int, last_candles: int) -> pd.DataFrame:
        """
        Obtiene un DataFrame con las últimas velas desde MetaTrader 5.
        
        Args:
            symbol: El símbolo de trading (por ejemplo, 'EURUSD').
            timeframe: El marco temporal a utilizar (por ejemplo, mt5.TIMEFRAME_M5).
            last_candles: Número de velas a recuperar.
            
        Returns:
            pd.DataFrame: DataFrame con los datos de precio.
        """
        # Obtener precios para las últimas velas
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, last_candles)
        if rates is None or len(rates) == 0:
            error_code = mt5.last_error()
            logging.error(f"Error al obtener tasas para {symbol}, código de error = {error_code}")
            return pd.DataFrame()
            
        rates_df = pd.DataFrame(rates)
        
        # Convertir la columna 'time' al formato datetime
        rates_df['time'] = pd.to_datetime(rates_df['time'], unit='s')
        rates_df['time'] = rates_df['time'].dt.tz_localize('UTC').dt.tz_convert(Metaquotes.DEFAULT_TIMEZONE)
        rates_df['time'] = rates_df['time'].dt.strftime('%d-%m-%Y %H:%M:%S')
        
        return rates_df
    
    @staticmethod
    def get_account_info() -> Dict[str, Any]:
        """
        Obtiene información de la cuenta desde MetaTrader 5.
        
        Returns:
            Dict[str, Any]: Diccionario con información de la cuenta.
        """
        account_info = mt5.account_info()
        if account_info is None:
            error_code = mt5.last_error()
            logging.error(f"Error al obtener información de la cuenta, código de error = {error_code}")
            return {}
            
        return {
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'free_margin': account_info.margin_free,
            'leverage': account_info.leverage,
            'profit': account_info.profit
        }
    
    @staticmethod
    def get_positions(symbol: Optional[str] = None) -> List:
        """
        Obtiene posiciones abiertas desde MetaTrader 5.
        
        Args:
            symbol: Símbolo opcional para filtrar posiciones.
            
        Returns:
            List: Lista de posiciones abiertas.
        """
        if symbol:
            positions = mt5.positions_get(symbol=symbol)
        else:
            positions = mt5.positions_get()
            
        if positions is None:
            error_code = mt5.last_error()
            logging.error(f"Error al obtener posiciones, código de error = {error_code}")
            return []
            
        return list(positions)
    
    @staticmethod
    def _prepare_order_request(
        symbol: str, 
        volume: float, 
        order_type: int, 
        price: float, 
        sl: float, 
        tp: float, 
        deviation: int, 
        magic: int, 
        comment: str
    ) -> Dict[str, Any]:
        """
        Prepara un diccionario de solicitud de orden.
        
        Args:
            symbol: El símbolo de trading.
            volume: El volumen de la orden en lotes.
            order_type: El tipo de orden (mt5.ORDER_TYPE_BUY o mt5.ORDER_TYPE_SELL).
            price: El precio de la orden.
            sl: El precio del stop loss.
            tp: El precio del take profit.
            deviation: La desviación máxima de precio.
            magic: El número mágico para la orden.
            comment: El comentario de la orden.
            
        Returns:
            Dict[str, Any]: La solicitud de orden preparada.
        """
        return {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
    
    @staticmethod
    def open_order(
        symbol: str, 
        volume: float, 
        order_type: int, 
        signal: int, 
        pips_sl: int, 
        pips_tp: int, 
        deviation: int, 
        comment: str,
        magic: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Abre una orden de trading (compra o venta).
        
        Args:
            symbol: El símbolo de trading.
            volume: El volumen de la orden en lotes.
            order_type: El tipo de orden (mt5.ORDER_TYPE_BUY o mt5.ORDER_TYPE_SELL).
            signal: El tipo de señal (2 para compra, 1 para venta).
            pips_sl: Stop loss en pips.
            pips_tp: Take profit en pips.
            deviation: La desviación máxima de precio.
            comment: El comentario de la orden.
            magic: Número mágico opcional para la orden.
            
        Returns:
            Dict[str, Any]: El resultado de la orden.
        """
        # Obtener información del símbolo
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            error_code = mt5.last_error()
            logging.error(f"Error al obtener información de tick para {symbol}, código de error = {error_code}")
            return {"retcode": -1, "comment": f"Error al obtener información de tick, código de error = {error_code}"}
            
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            error_code = mt5.last_error()
            logging.error(f"Error al obtener información del símbolo para {symbol}, código de error = {error_code}")
            return {"retcode": -1, "comment": f"Error al obtener información del símbolo, código de error = {error_code}"}
            
        price_dict = {2: tick.ask, 1: tick.bid}
        point = symbol_info.point
        
        # Establecer número mágico predeterminado si no se proporciona
        if magic is None:
            magic = Metaquotes.DEFAULT_MAGIC_BUY if order_type == mt5.ORDER_TYPE_BUY else Metaquotes.DEFAULT_MAGIC_SELL
        
        # Calcular stop loss y take profit
        if order_type == mt5.ORDER_TYPE_BUY:
            stop_loss = price_dict[signal] - pips_sl * point
            take_profit = price_dict[signal] + pips_tp * point
        else:  # SELL
            stop_loss = price_dict[signal] + pips_sl * point
            take_profit = price_dict[signal] - pips_tp * point
        
        # Preparar y enviar la solicitud de orden
        request = Metaquotes._prepare_order_request(
            symbol, volume, order_type, price_dict[signal], 
            stop_loss, take_profit, deviation, magic, comment
        )
        
        order_result = mt5.order_send(request)
        
        # Registrar el resultado
        if order_result.retcode == mt5.TRADE_RETCODE_DONE:
            order_type_str = "COMPRA" if order_type == mt5.ORDER_TYPE_BUY else "VENTA"
            logging.info(f"Orden {order_type_str} ejecutada correctamente: {order_result}")
        else:
            logging.error(f"Orden fallida: {order_result}")
        
        return order_result._asdict()
    
    @staticmethod
    def open_order_buy(
        symbol: str, 
        volume: float, 
        signal: int, 
        pips_sl: int, 
        pips_tp: int, 
        deviation: int, 
        comment: str,
        magic: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Abre una orden de compra.
        
        Args:
            symbol: El símbolo de trading.
            volume: El volumen de la orden en lotes.
            signal: El tipo de señal (normalmente 2 para compra).
            pips_sl: Stop loss en pips.
            pips_tp: Take profit en pips.
            deviation: La desviación máxima de precio.
            comment: El comentario de la orden.
            magic: Número mágico opcional para la orden.
            
        Returns:
            Dict[str, Any]: El resultado de la orden.
        """
        return Metaquotes.open_order(
            symbol, volume, mt5.ORDER_TYPE_BUY, signal, 
            pips_sl, pips_tp, deviation, comment, 
            magic or Metaquotes.DEFAULT_MAGIC_BUY
        )
    
    @staticmethod
    def open_order_sell(
        symbol: str, 
        volume: float, 
        signal: int, 
        pips_sl: int, 
        pips_tp: int, 
        deviation: int, 
        comment: str,
        magic: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Abre una orden de venta.
        
        Args:
            symbol: El símbolo de trading.
            volume: El volumen de la orden en lotes.
            signal: El tipo de señal (normalmente 1 para venta).
            pips_sl: Stop loss en pips.
            pips_tp: Take profit en pips.
            deviation: La desviación máxima de precio.
            comment: El comentario de la orden.
            magic: Número mágico opcional para la orden.
            
        Returns:
            Dict[str, Any]: El resultado de la orden.
        """
        return Metaquotes.open_order(
            symbol, volume, mt5.ORDER_TYPE_SELL, signal, 
            pips_sl, pips_tp, deviation, comment, 
            magic or Metaquotes.DEFAULT_MAGIC_SELL
        )
    
    @staticmethod
    def close_position(
        position, 
        deviation: int = 20, 
        comment: str = "cierre por script python",
        magic: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Cierra una posición abierta.
        
        Args:
            position: La posición a cerrar.
            deviation: La desviación máxima de precio.
            comment: El comentario de la orden.
            magic: Número mágico opcional para la orden.
            
        Returns:
            Dict[str, Any]: El resultado de la orden.
        """
        tick = mt5.symbol_info_tick(position.symbol)
        if tick is None:
            error_code = mt5.last_error()
            logging.error(f"Error al obtener información de tick para {position.symbol}, código de error = {error_code}")
            return {"retcode": -1, "comment": f"Error al obtener información de tick, código de error = {error_code}"}
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
            "price": tick.ask if position.type == 1 else tick.bid,
            "deviation": deviation,
            "magic": magic or Metaquotes.DEFAULT_MAGIC_CLOSE,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        # Registrar el resultado
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info(f"Posición {position.ticket} cerrada correctamente: {result}")
        else:
            logging.error(f"Error al cerrar posición {position.ticket}: {result}")
        
        return result._asdict()
    
    @staticmethod
    def modify_position(
        position, 
        sl: Optional[float] = None, 
        tp: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Modifica el stop loss y/o take profit de una posición abierta.
        
        Args:
            position: La posición a modificar.
            sl: Nuevo precio de stop loss (None para mantener el actual).
            tp: Nuevo precio de take profit (None para mantener el actual).
            
        Returns:
            Dict[str, Any]: El resultado de la orden.
        """
        request = {
            "action": mt5.TRADE_ACTION_MODIFY,
            "position": position.ticket,
            "symbol": position.symbol,
            "sl": sl if sl is not None else position.sl,
            "tp": tp if tp is not None else position.tp,
        }
        
        result = mt5.order_send(request)
        
        # Registrar el resultado
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info(f"Posición {position.ticket} modificada correctamente: {result}")
        else:
            logging.error(f"Error al modificar posición {position.ticket}: {result}")
        
        return result._asdict()
    
    @staticmethod
    def get_symbol_info(symbol: str) -> Dict[str, Any]:
        """
        Obtiene información detallada sobre un símbolo de trading.
        
        Args:
            symbol: El símbolo de trading.
            
        Returns:
            Dict[str, Any]: Diccionario con información del símbolo.
        """
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            error_code = mt5.last_error()
            logging.error(f"Error al obtener información del símbolo para {symbol}, código de error = {error_code}")
            return {}
            
        return {
            'name': symbol_info.name,
            'point': symbol_info.point,
            'digits': symbol_info.digits,
            'spread': symbol_info.spread,
            'tick_size': symbol_info.trade_tick_size,
            'contract_size': symbol_info.trade_contract_size,
            'volume_min': symbol_info.volume_min,
            'volume_max': symbol_info.volume_max,
            'volume_step': symbol_info.volume_step
        }