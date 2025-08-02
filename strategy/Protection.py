# -*- coding: utf-8 -*-
"""
Módulo de estrategias de protección de capital.

Este módulo implementa diversas estrategias de protección de capital
que ayudan a limitar las pérdidas y preservar el capital del trader. Las estrategias de
protección son fundamentales para la gestión de riesgos en trading.

Las estrategias implementadas incluyen:
- Límites de pérdida diaria/semanal/mensual
- Reducción automática del tamaño de posición después de pérdidas consecutivas
- Parada temporal de operaciones después de alcanzar un umbral de pérdida
- Ajuste dinámico de la exposición al riesgo basado en la volatilidad del mercado
- Protección basada en correlación entre instrumentos
- Restricciones de trading basadas en horarios
- Protección contra drawdown máximo
"""
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import datetime
import time
import logging
from typing import Optional, Union, Dict, Any, List, Tuple


class Protection:
    """
    Clase que implementa estrategias de protección de capital.
    
    Esta clase proporciona diversos mecanismos de protección para ayudar
    a proteger el capital del trader y gestionar el riesgo de manera efectiva.
    
    Attributes:
        account_info (Dict): Información de la cuenta de trading
        trading_allowed (bool): Indica si el trading está permitido según las protecciones
        last_check_time (datetime): Última vez que se verificaron las protecciones
    """
    
    def __init__(self):
        """
        Inicializa la clase de protección con valores predeterminados.
        """
        self.account_info = self._get_account_info()
        self.trading_allowed = True
        self.last_check_time = datetime.datetime.now()
        self.consecutive_losses = 0
        self.daily_loss = 0
        self.weekly_loss = 0
        self.monthly_loss = 0
        self.initial_balance = self.account_info['balance'] if self.account_info else 0
        self.max_balance = self.initial_balance
        
    def _get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene la información de la cuenta de trading.
        
        Returns:
            Optional[Dict[str, Any]]: Información de la cuenta o None si hay un error
        """
        try:
            account_info = mt5.account_info()
            if account_info is None:
                logging.error("PROTECTION - No se pudo obtener la información de la cuenta")
                return None
            
            return {
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'profit': account_info.profit,
                'leverage': account_info.leverage
            }
        except Exception as e:
            logging.error(f"PROTECTION - Error al obtener información de la cuenta: {e}")
            return None
    
    def update_account_info(self) -> None:
        """
        Actualiza la información de la cuenta y registra cambios importantes.
        """
        previous_info = self.account_info
        current_info = self._get_account_info()
        
        if not current_info or not previous_info:
            return
            
        # Actualizar balance máximo
        if current_info['equity'] > self.max_balance:
            self.max_balance = current_info['equity']
            
        # Calcular pérdidas del período
        if current_info['equity'] < previous_info['equity']:
            loss = previous_info['equity'] - current_info['equity']
            self.daily_loss += loss
            self.weekly_loss += loss
            self.monthly_loss += loss
            
        # Actualizar información de la cuenta
        self.account_info = current_info
        
    def breakdown(self, percentage: float) -> Dict[str, Any]:
        """
        Implementa una estrategia de protección basada en un porcentaje de breakdown.
        
        Este método detiene o modifica las operaciones cuando las pérdidas
        alcanzan un cierto porcentaje del capital.
        
        Args:
            percentage: Porcentaje de pérdida que activará la protección.
            
        Returns:
            Dict[str, Any]: Información sobre las acciones de protección tomadas
        """
        self.update_account_info()
        
        if not self.account_info:
            return {'allowed': False, 'reason': 'No se pudo obtener información de la cuenta'}
            
        current_equity = self.account_info['equity']
        initial_balance = self.initial_balance
        
        # Calcular el porcentaje de pérdida
        if initial_balance > 0:
            loss_percentage = ((initial_balance - current_equity) / initial_balance) * 100
        else:
            loss_percentage = 0
            
        # Verificar si se ha alcanzado el umbral de pérdida
        if loss_percentage >= percentage:
            self.trading_allowed = False
            return {
                'allowed': False,
                'reason': f'Se ha alcanzado el umbral de pérdida ({loss_percentage:.2f}% > {percentage:.2f}%)',
                'loss_percentage': loss_percentage,
                'threshold': percentage,
                'initial_balance': initial_balance,
                'current_equity': current_equity
            }
        
        return {
            'allowed': True,
            'loss_percentage': loss_percentage,
            'threshold': percentage,
            'initial_balance': initial_balance,
            'current_equity': current_equity
        }
    
    def max_drawdown(self, max_percentage: float) -> Dict[str, Any]:
        """
        Protección contra drawdown máximo.
        
        Detiene el trading cuando el drawdown supera un porcentaje máximo
        desde el balance más alto alcanzado.
        
        Args:
            max_percentage: Porcentaje máximo de drawdown permitido.
            
        Returns:
            Dict[str, Any]: Información sobre las acciones de protección tomadas
        """
        self.update_account_info()
        
        if not self.account_info:
            return {'allowed': False, 'reason': 'No se pudo obtener información de la cuenta'}
            
        current_equity = self.account_info['equity']
        
        # Calcular el drawdown actual
        if self.max_balance > 0:
            drawdown_percentage = ((self.max_balance - current_equity) / self.max_balance) * 100
        else:
            drawdown_percentage = 0
            
        # Verificar si se ha superado el drawdown máximo
        if drawdown_percentage >= max_percentage:
            self.trading_allowed = False
            return {
                'allowed': False,
                'reason': f'Se ha superado el drawdown máximo ({drawdown_percentage:.2f}% > {max_percentage:.2f}%)',
                'drawdown_percentage': drawdown_percentage,
                'threshold': max_percentage,
                'max_balance': self.max_balance,
                'current_equity': current_equity
            }
        
        return {
            'allowed': True,
            'drawdown_percentage': drawdown_percentage,
            'threshold': max_percentage,
            'max_balance': self.max_balance,
            'current_equity': current_equity
        }
    
    def daily_loss_limit(self, max_loss_percentage: float) -> Dict[str, Any]:
        """
        Limita las pérdidas diarias a un porcentaje máximo del balance inicial.
        
        Args:
            max_loss_percentage: Porcentaje máximo de pérdida diaria permitido.
            
        Returns:
            Dict[str, Any]: Información sobre las acciones de protección tomadas
        """
        self.update_account_info()
        
        if not self.account_info:
            return {'allowed': False, 'reason': 'No se pudo obtener información de la cuenta'}
            
        # Verificar si es un nuevo día
        current_time = datetime.datetime.now()
        if current_time.date() > self.last_check_time.date():
            self.daily_loss = 0
            
        self.last_check_time = current_time
        
        # Calcular el porcentaje de pérdida diaria
        if self.initial_balance > 0:
            daily_loss_percentage = (self.daily_loss / self.initial_balance) * 100
        else:
            daily_loss_percentage = 0
            
        # Verificar si se ha superado el límite de pérdida diaria
        if daily_loss_percentage >= max_loss_percentage:
            self.trading_allowed = False
            return {
                'allowed': False,
                'reason': f'Se ha superado el límite de pérdida diaria ({daily_loss_percentage:.2f}% > {max_loss_percentage:.2f}%)',
                'daily_loss_percentage': daily_loss_percentage,
                'threshold': max_loss_percentage,
                'daily_loss': self.daily_loss,
                'initial_balance': self.initial_balance
            }
        
        return {
            'allowed': True,
            'daily_loss_percentage': daily_loss_percentage,
            'threshold': max_loss_percentage,
            'daily_loss': self.daily_loss,
            'initial_balance': self.initial_balance
        }
    
    def weekly_loss_limit(self, max_loss_percentage: float) -> Dict[str, Any]:
        """
        Limita las pérdidas semanales a un porcentaje máximo del balance inicial.
        
        Args:
            max_loss_percentage: Porcentaje máximo de pérdida semanal permitido.
            
        Returns:
            Dict[str, Any]: Información sobre las acciones de protección tomadas
        """
        self.update_account_info()
        
        if not self.account_info:
            return {'allowed': False, 'reason': 'No se pudo obtener información de la cuenta'}
            
        # Verificar si es una nueva semana
        current_time = datetime.datetime.now()
        if current_time.isocalendar()[1] > self.last_check_time.isocalendar()[1]:
            self.weekly_loss = 0
            
        self.last_check_time = current_time
        
        # Calcular el porcentaje de pérdida semanal
        if self.initial_balance > 0:
            weekly_loss_percentage = (self.weekly_loss / self.initial_balance) * 100
        else:
            weekly_loss_percentage = 0
            
        # Verificar si se ha superado el límite de pérdida semanal
        if weekly_loss_percentage >= max_loss_percentage:
            self.trading_allowed = False
            return {
                'allowed': False,
                'reason': f'Se ha superado el límite de pérdida semanal ({weekly_loss_percentage:.2f}% > {max_loss_percentage:.2f}%)',
                'weekly_loss_percentage': weekly_loss_percentage,
                'threshold': max_loss_percentage,
                'weekly_loss': self.weekly_loss,
                'initial_balance': self.initial_balance
            }
        
        return {
            'allowed': True,
            'weekly_loss_percentage': weekly_loss_percentage,
            'threshold': max_loss_percentage,
            'weekly_loss': self.weekly_loss,
            'initial_balance': self.initial_balance
        }
    
    def monthly_loss_limit(self, max_loss_percentage: float) -> Dict[str, Any]:
        """
        Limita las pérdidas mensuales a un porcentaje máximo del balance inicial.
        
        Args:
            max_loss_percentage: Porcentaje máximo de pérdida mensual permitido.
            
        Returns:
            Dict[str, Any]: Información sobre las acciones de protección tomadas
        """
        self.update_account_info()
        
        if not self.account_info:
            return {'allowed': False, 'reason': 'No se pudo obtener información de la cuenta'}
            
        # Verificar si es un nuevo mes
        current_time = datetime.datetime.now()
        if current_time.month > self.last_check_time.month or current_time.year > self.last_check_time.year:
            self.monthly_loss = 0
            
        self.last_check_time = current_time
        
        # Calcular el porcentaje de pérdida mensual
        if self.initial_balance > 0:
            monthly_loss_percentage = (self.monthly_loss / self.initial_balance) * 100
        else:
            monthly_loss_percentage = 0
            
        # Verificar si se ha superado el límite de pérdida mensual
        if monthly_loss_percentage >= max_loss_percentage:
            self.trading_allowed = False
            return {
                'allowed': False,
                'reason': f'Se ha superado el límite de pérdida mensual ({monthly_loss_percentage:.2f}% > {max_loss_percentage:.2f}%)',
                'monthly_loss_percentage': monthly_loss_percentage,
                'threshold': max_loss_percentage,
                'monthly_loss': self.monthly_loss,
                'initial_balance': self.initial_balance
            }
        
        return {
            'allowed': True,
            'monthly_loss_percentage': monthly_loss_percentage,
            'threshold': max_loss_percentage,
            'monthly_loss': self.monthly_loss,
            'initial_balance': self.initial_balance
        }
    
    def consecutive_losses_protection(self, max_consecutive_losses: int, volume_reduction_factor: float = 0.5) -> Dict[str, Any]:
        """
        Reduce el tamaño de posición después de un número de pérdidas consecutivas.
        
        Args:
            max_consecutive_losses: Número máximo de pérdidas consecutivas permitidas.
            volume_reduction_factor: Factor de reducción del volumen (0.5 = 50% de reducción).
            
        Returns:
            Dict[str, Any]: Información sobre las acciones de protección tomadas
        """
        # Obtener historial de órdenes cerradas
        try:
            from_date = datetime.datetime.now() - datetime.timedelta(days=7)
            to_date = datetime.datetime.now()
            
            # Obtener historial de órdenes
            history_orders = mt5.history_deals_get(from_date, to_date)
            
            if history_orders is None or len(history_orders) == 0:
                return {
                    'allowed': True,
                    'consecutive_losses': 0,
                    'max_consecutive_losses': max_consecutive_losses,
                    'volume_factor': 1.0
                }
                
            # Convertir a DataFrame
            orders_df = pd.DataFrame(list(history_orders), columns=history_orders[0]._asdict().keys())
            
            # Filtrar solo órdenes cerradas
            closed_orders = orders_df[orders_df['type'].isin([1, 0])]  # 0=BUY, 1=SELL
            
            # Ordenar por tiempo
            closed_orders = closed_orders.sort_values('time', ascending=False)
            
            # Contar pérdidas consecutivas
            self.consecutive_losses = 0
            for _, order in closed_orders.iterrows():
                if order['profit'] < 0:
                    self.consecutive_losses += 1
                else:
                    break
                    
        except Exception as e:
            logging.error(f"PROTECTION - Error al obtener historial de órdenes: {e}")
            return {'allowed': True, 'reason': f'Error al obtener historial: {e}'}
        
        # Calcular factor de volumen
        volume_factor = 1.0
        if self.consecutive_losses >= max_consecutive_losses:
            volume_factor = volume_reduction_factor
            
        return {
            'allowed': True,
            'consecutive_losses': self.consecutive_losses,
            'max_consecutive_losses': max_consecutive_losses,
            'volume_factor': volume_factor
        }
    
    def volatility_based_position_sizing(self, symbol: str, timeframe: int, lookback_periods: int = 20, 
                                        max_volatility_multiplier: float = 2.0) -> Dict[str, Any]:
        """
        Ajusta el tamaño de posición basado en la volatilidad del mercado.
        
        Reduce el tamaño de posición cuando la volatilidad es alta y lo aumenta cuando es baja.
        
        Args:
            symbol: Símbolo del instrumento.
            timeframe: Marco temporal para el análisis.
            lookback_periods: Número de períodos para calcular la volatilidad.
            max_volatility_multiplier: Multiplicador máximo de volatilidad para reducir el tamaño.
            
        Returns:
            Dict[str, Any]: Información sobre el ajuste de tamaño de posición
        """
        try:
            # Obtener datos históricos
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, lookback_periods + 1)
            
            if rates is None or len(rates) == 0:
                return {'allowed': True, 'volume_factor': 1.0, 'reason': 'No se pudieron obtener datos históricos'}
                
            # Convertir a DataFrame
            df = pd.DataFrame(rates)
            
            # Calcular la volatilidad (ATR - Average True Range)
            df['high_low'] = df['high'] - df['low']
            df['high_close'] = abs(df['high'] - df['close'].shift(1))
            df['low_close'] = abs(df['low'] - df['close'].shift(1))
            df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
            current_atr = df['tr'].mean()
            
            # Calcular ATR promedio de los últimos períodos
            average_atr = df['tr'].rolling(window=lookback_periods).mean().iloc[-1]
            
            if pd.isna(average_atr) or average_atr == 0:
                return {'allowed': True, 'volume_factor': 1.0, 'reason': 'No se pudo calcular el ATR'}
                
            # Calcular el ratio de volatilidad actual vs promedio
            volatility_ratio = current_atr / average_atr
            
            # Ajustar el tamaño de posición inversamente proporcional a la volatilidad
            if volatility_ratio > 1.0:
                # Alta volatilidad, reducir tamaño
                volume_factor = 1.0 / min(volatility_ratio, max_volatility_multiplier)
            else:
                # Baja volatilidad, mantener o aumentar ligeramente
                volume_factor = min(1.2, 1.0 / volatility_ratio) if volatility_ratio > 0 else 1.0
                
            return {
                'allowed': True,
                'volume_factor': volume_factor,
                'volatility_ratio': volatility_ratio,
                'current_atr': current_atr,
                'average_atr': average_atr
            }
            
        except Exception as e:
            logging.error(f"PROTECTION - Error al calcular el ajuste basado en volatilidad: {e}")
            return {'allowed': True, 'volume_factor': 1.0, 'reason': f'Error: {e}'}
    
    def correlation_protection(self, symbols: List[str], timeframe: int, 
                              max_correlation: float = 0.7, lookback_periods: int = 50) -> Dict[str, Any]:
        """
        Protección basada en la correlación entre instrumentos.
        
        Evita abrir múltiples posiciones en instrumentos altamente correlacionados.
        
        Args:
            symbols: Lista de símbolos a analizar.
            timeframe: Marco temporal para el análisis.
            max_correlation: Correlación máxima permitida entre instrumentos.
            lookback_periods: Número de períodos para calcular la correlación.
            
        Returns:
            Dict[str, Any]: Información sobre la correlación y acciones tomadas
        """
        try:
            # Verificar que hay al menos 2 símbolos
            if len(symbols) < 2:
                return {'allowed': True, 'reason': 'Se necesitan al menos 2 símbolos para calcular correlación'}
                
            # Obtener datos históricos para cada símbolo
            symbol_data = {}
            for symbol in symbols:
                rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, lookback_periods)
                if rates is not None and len(rates) > 0:
                    df = pd.DataFrame(rates)
                    symbol_data[symbol] = df['close']
                    
            if len(symbol_data) < 2:
                return {'allowed': True, 'reason': 'No se pudieron obtener datos suficientes'}
                
            # Crear DataFrame con los precios de cierre
            prices_df = pd.DataFrame(symbol_data)
            
            # Calcular matriz de correlación
            correlation_matrix = prices_df.corr()
            
            # Buscar pares con alta correlación
            high_correlation_pairs = []
            for i, symbol1 in enumerate(correlation_matrix.index):
                for j, symbol2 in enumerate(correlation_matrix.columns):
                    if i < j:  # Evitar duplicados y comparaciones consigo mismo
                        correlation = correlation_matrix.loc[symbol1, symbol2]
                        if abs(correlation) > max_correlation:
                            high_correlation_pairs.append((symbol1, symbol2, correlation))
            
            # Verificar posiciones abiertas en símbolos correlacionados
            positions = mt5.positions_get()
            if positions is not None and len(positions) > 0:
                positions_df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
                open_symbols = positions_df['symbol'].unique()
                
                # Verificar si hay posiciones abiertas en símbolos correlacionados
                for symbol1, symbol2, correlation in high_correlation_pairs:
                    if symbol1 in open_symbols and symbol2 in open_symbols:
                        return {
                            'allowed': False,
                            'reason': f'Alta correlación entre {symbol1} y {symbol2}: {correlation:.2f}',
                            'correlation_pairs': high_correlation_pairs
                        }
            
            return {
                'allowed': True,
                'correlation_pairs': high_correlation_pairs,
                'correlation_matrix': correlation_matrix.to_dict()
            }
            
        except Exception as e:
            logging.error(f"PROTECTION - Error al calcular la protección por correlación: {e}")
            return {'allowed': True, 'reason': f'Error: {e}'}
    
    def time_based_restrictions(self, allowed_hours: List[Tuple[int, int]] = None, 
                               allowed_days: List[int] = None) -> Dict[str, Any]:
        """
        Restricciones de trading basadas en horarios y días de la semana.
        
        Args:
            allowed_hours: Lista de tuplas con horas permitidas (inicio, fin) en formato 24h.
                          Por defecto, permite trading las 24 horas.
            allowed_days: Lista de días permitidos (0=lunes, 6=domingo).
                         Por defecto, permite trading todos los días.
            
        Returns:
            Dict[str, Any]: Información sobre las restricciones de tiempo
        """
        current_time = datetime.datetime.now()
        current_hour = current_time.hour
        current_day = current_time.weekday()  # 0=lunes, 6=domingo
        
        # Valores predeterminados
        if allowed_hours is None:
            allowed_hours = [(0, 23)]  # 24 horas
            
        if allowed_days is None:
            allowed_days = list(range(7))  # Todos los días
            
        # Verificar si el día actual está permitido
        if current_day not in allowed_days:
            return {
                'allowed': False,
                'reason': f'Trading no permitido en día {current_day} (0=lunes, 6=domingo)',
                'current_day': current_day,
                'allowed_days': allowed_days
            }
            
        # Verificar si la hora actual está permitida
        hour_allowed = False
        for start_hour, end_hour in allowed_hours:
            if start_hour <= current_hour <= end_hour:
                hour_allowed = True
                break
                
        if not hour_allowed:
            return {
                'allowed': False,
                'reason': f'Trading no permitido a la hora {current_hour}',
                'current_hour': current_hour,
                'allowed_hours': allowed_hours
            }
            
        return {
            'allowed': True,
            'current_day': current_day,
            'current_hour': current_hour,
            'allowed_days': allowed_days,
            'allowed_hours': allowed_hours
        }
    
    def check_all_protections(self, 
                             breakdown_percentage: float = 10.0,
                             max_drawdown_percentage: float = 15.0,
                             daily_loss_percentage: float = 5.0,
                             weekly_loss_percentage: float = 10.0,
                             monthly_loss_percentage: float = 15.0,
                             max_consecutive_losses: int = 3,
                             volume_reduction_factor: float = 0.5,
                             symbol: str = None,
                             timeframe: int = mt5.TIMEFRAME_H1,
                             max_volatility_multiplier: float = 2.0,
                             symbols_correlation: List[str] = None,
                             max_correlation: float = 0.7,
                             allowed_hours: List[Tuple[int, int]] = None,
                             allowed_days: List[int] = None) -> Dict[str, Any]:
        """
        Verifica todas las protecciones configuradas y devuelve un resultado consolidado.
        
        Args:
            breakdown_percentage: Porcentaje de pérdida que activará la protección.
            max_drawdown_percentage: Porcentaje máximo de drawdown permitido.
            daily_loss_percentage: Porcentaje máximo de pérdida diaria permitido.
            weekly_loss_percentage: Porcentaje máximo de pérdida semanal permitido.
            monthly_loss_percentage: Porcentaje máximo de pérdida mensual permitido.
            max_consecutive_losses: Número máximo de pérdidas consecutivas permitidas.
            volume_reduction_factor: Factor de reducción del volumen.
            symbol: Símbolo para el cálculo de volatilidad.
            timeframe: Marco temporal para los cálculos.
            max_volatility_multiplier: Multiplicador máximo de volatilidad.
            symbols_correlation: Lista de símbolos para verificar correlación.
            max_correlation: Correlación máxima permitida.
            allowed_hours: Lista de tuplas con horas permitidas.
            allowed_days: Lista de días permitidos.
            
        Returns:
            Dict[str, Any]: Resultado consolidado de todas las protecciones
        """
        results = {}
        
        # Verificar protección de breakdown
        results['breakdown'] = self.breakdown(breakdown_percentage)
        
        # Verificar protección de drawdown máximo
        results['max_drawdown'] = self.max_drawdown(max_drawdown_percentage)
        
        # Verificar límites de pérdida por período
        results['daily_loss'] = self.daily_loss_limit(daily_loss_percentage)
        results['weekly_loss'] = self.weekly_loss_limit(weekly_loss_percentage)
        results['monthly_loss'] = self.monthly_loss_limit(monthly_loss_percentage)
        
        # Verificar protección de pérdidas consecutivas
        results['consecutive_losses'] = self.consecutive_losses_protection(
            max_consecutive_losses, volume_reduction_factor
        )
        
        # Verificar ajuste basado en volatilidad
        if symbol:
            results['volatility'] = self.volatility_based_position_sizing(
                symbol, timeframe, 20, max_volatility_multiplier
            )
        
        # Verificar protección por correlación
        if symbols_correlation and len(symbols_correlation) >= 2:
            results['correlation'] = self.correlation_protection(
                symbols_correlation, timeframe, max_correlation
            )
        
        # Verificar restricciones de tiempo
        results['time_restrictions'] = self.time_based_restrictions(allowed_hours, allowed_days)
        
        # Determinar si el trading está permitido
        trading_allowed = True
        reasons = []
        
        for protection, result in results.items():
            if 'allowed' in result and not result['allowed']:
                trading_allowed = False
                if 'reason' in result:
                    reasons.append(f"{protection}: {result['reason']}")
        
        # Calcular factor de volumen combinado
        volume_factor = 1.0
        if 'consecutive_losses' in results and 'volume_factor' in results['consecutive_losses']:
            volume_factor *= results['consecutive_losses']['volume_factor']
        
        if 'volatility' in results and 'volume_factor' in results['volatility']:
            volume_factor *= results['volatility']['volume_factor']
        
        return {
            'trading_allowed': trading_allowed,
            'reasons': reasons,
            'volume_factor': volume_factor,
            'details': results
        }