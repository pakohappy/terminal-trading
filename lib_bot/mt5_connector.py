import MetaTrader5 as mt5
from configuracion.config_loader import ConfigLoader
import logging
import pandas as pd
from datetime import datetime

class MT5Connector:
    def __init__(self, config_path='configuracion/config.ini'):
        """
        Inicializa la conexión con MetaTrader 5 al crear una instancia de la clase.
        """
        # Cargar configuraciones desde el archivo config.ini
        self.config = ConfigLoader(config_path)
        self.login = self.config.get_int('metatrader', 'login')
        self.password = self.config.get('metatrader', 'password')
        self.server = self.config.get('metatrader', 'server')

        # Iniciar conexión con MetaTrader 5
        if not mt5.initialize(login=self.login, password=self.password, server=self.server):
            logging.error("Error al inicializar MetaTrader 5")
            raise RuntimeError(f"Error al inicializar MetaTrader 5: {mt5.last_error()}")
            raise ConnectionError("No se pudo conectar a MetaTrader 5")
        else:
            logging.info("MetaTrader 5 inicializado correctamente")

    # Cierra la conexión con MetaTrader 5.
    def shutdown(self):
        mt5.shutdown()
        logging.info("MetaTrader 5 cerrado correctamente")

    # Devuelve la información de la cuenta.
    def info_cuenta(self):
        account = mt5.account_info()
        if account!=None:
            account_info_dict = mt5.account_info()._asdict()
    
            # Convertir la información de la cuenta a un diccionario.
            df=pd.DataFrame(list(account_info_dict.items()),columns=['property','value'])
            print("\n### Información de la cuenta como dataframe:")
            print(df)
        else:
            logging.error("MT5_CONNECTOR - Error al obtener información de la cuenta.")
            raise ConnectionError("No se pudo obtener información de la cuenta")
        
    # Devulve la información de la terminal.
    def info_terminal(self):
        terminal = mt5.terminal_info()
        if terminal!=None:
            terminal_info_dict = mt5.terminal_info()._asdict()
    
            # Convertir la información de la cuenta a un diccionario.
            df=pd.DataFrame(list(terminal_info_dict.items()),columns=['property','value'])
            print("\n### Información de la terminal como dataframe:")
            print(df)
        else:
            logging.error("MT5_CONNECTOR - Error al obtener información de la terminal.")
            raise ConnectionError("No se pudo obtener información de la terminal")
        
    # Obtiene las últimas velas de MetaTrader 5 y las devuelve en formato DataFrame.    
    def obtener_ultimas_velas(self, simbolo, timeframe, cantidad) -> pd.DataFrame:
        """
        Obtiene las últimas 'cantidad' velas de MetaTrader 5 en formato DataFrame.

        :param simbolo: El símbolo del mercado (por ejemplo, "EURUSD").
        :param timeframe: El marco temporal (por ejemplo, mt5.TIMEFRAME_M1 para 1 minuto).
        :param cantidad: El número de velas a obtener (por defecto 40).
        :return: DataFrame con las velas en formato OHLC.
        """
        try:
            # Diccionario para mapear cadenas a valores de MetaTrader5.
            TIMEFRAMES = {
                "M1": mt5.TIMEFRAME_M1,
                "M5": mt5.TIMEFRAME_M5,
                "M15": mt5.TIMEFRAME_M15,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1,
                "W1": mt5.TIMEFRAME_W1,
                "MN1": mt5.TIMEFRAME_MN1,
            }       

             # Convertir el marco temporal de cadena a valor de MetaTrader5.
            if timeframe not in TIMEFRAMES:
                raise ValueError(f"Timeframe '{timeframe}' no es válido.")
            mt5_timeframe = TIMEFRAMES[timeframe]

            # Seleccionar el símbolo
            if not mt5.symbol_select(simbolo, True):
                raise RuntimeError(f"Error al seleccionar el símbolo {simbolo}: {mt5.last_error()}")
            
            if not mt5.initialize():
                raise RuntimeError(f"Error al inicializar MetaTrader 5: {mt5.last_error()}")

            # Obtener las últimas 'cantidad' velas
            # Obtener las últimas velas desde la posición 0 (más recientes).
            rates = mt5.copy_rates_from_pos(simbolo, mt5_timeframe, 0, cantidad) # TODO: origen variables.

            # Convertir a DataFrame
            df = pd.DataFrame(rates)

            # Convertir la columna 'time' a formato datetime
            df['time'] = pd.to_datetime(df['time'], unit='s')

            return df
    
        except Exception as e:
            logging.error(f"MT5_CONNECTOR - Error al obtener las velas: {e}")
            raise RuntimeError(f"Error al obtener las velas: {e}")
        
    # Abrir una orden de compra.
    def abrir_orden_compra(self, simbolo, lotes, precio, sl, tp):
        """
        Abre una orden de compra en MetaTrader 5.

        :param simbolo: El símbolo del mercado (por ejemplo, "EURUSD").
        :param lotes: El número de lotes a comprar.
        :param precio: El precio al que se desea abrir la orden.
        :param sl: El nivel de stop loss.
        :param tp: El nivel de take profit.
        :return: True si la orden se abre correctamente, False en caso contrario.
        """
        try:
            # Configurar los parámetros de la orden
            order_type = mt5.ORDER_BUY
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "volume": lotes,
                "type": order_type,
                "price": precio,
                "sl": sl,
                "tp": tp,
                "deviation": 10,
                "magic": 234000,  # Número mágico para identificar la orden
                "comment": "Orden de compra desde Python",
                "type_time": mt5.ORDER_TIME_GTC,  # Tiempo de validez de la orden
                "type_filling": mt5.ORDER_FILLING_IOC,  # Tipo de ejecución
            }

            # Enviar la solicitud de apertura de orden
            result = mt5.order_send(request)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(f"Error al abrir la orden de compra: {result.retcode}")
                return False

            logging.info(f"Orden de compra abierta correctamente: {result}")
            return True

        except Exception as e:
            logging.error(f"Error al abrir la orden de compra: {e}")
            return False
        
    # Abrir una orden de venta.
    def abrir_orden_venta(self, simbolo, lotes, precio, sl, tp):
        """
        Abre una orden de venta en MetaTrader 5.

        :param simbolo: El símbolo del mercado (por ejemplo, "EURUSD").
        :param lotes: El número de lotes a vender.
        :param precio: El precio al que se desea abrir la orden.
        :param sl: El nivel de stop loss.
        :param tp: El nivel de take profit.
        :return: True si la orden se abre correctamente, False en caso contrario.
        """
        try:
            # Configurar los parámetros de la orden
            order_type = mt5.ORDER_SELL
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": simbolo,
                "volume": lotes,
                "type": order_type,
                "price": precio,
                "sl": sl,
                "tp": tp,
                "deviation": 10,
                "magic": 234000,  # Número mágico para identificar la orden
                "comment": "Orden de venta desde Python",
                "type_time": mt5.ORDER_TIME_GTC,  # Tiempo de validez de la orden
                "type_filling": mt5.ORDER_FILLING_IOC,  # Tipo de ejecución
            }

            # Enviar la solicitud de apertura de orden
            result = mt5.order_send(request)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(f"Error al abrir la orden de venta: {result.retcode}")
                return False

            logging.info(f"Orden de venta abierta correctamente: {result}")
            return True

        except Exception as e:
            logging.error(f"Error al abrir la orden de venta: {e}")
            return False
        
    # Cerrar una orden.
    def cerrar_orden(self, ticket):
        """
        Cierra una orden en MetaTrader 5.

        :param ticket: El número de ticket de la orden a cerrar.
        :return: True si la orden se cierra correctamente, False en caso contrario.
        """
        try:
            # Configurar los parámetros de cierre de la orden
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": ticket,
                "type": mt5.ORDER_BUY,  # Tipo de orden (compra o venta)
                "deviation": 10,
                "magic": 234000,  # Número mágico para identificar la orden
                "comment": "Cierre de orden desde Python",
            }

            # Enviar la solicitud de cierre de orden
            result = mt5.order_send(request)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(f"Error al cerrar la orden: {result.retcode}")
                return False

            logging.info(f"Orden cerrada correctamente: {result}")
            return True

        except Exception as e:
            logging.error(f"Error al cerrar la orden: {e}")
            return False
        
    # Actualización dinamica stop loss a el % definido en el config.ini.
    def actualizar_stop_loss(self, ticket, nuevo_sl):
        """
        Actualiza el stop loss de una orden en MetaTrader 5.

        :param ticket: El número de ticket de la orden a actualizar.
        :param nuevo_sl: El nuevo nivel de stop loss.
        :return: True si el stop loss se actualiza correctamente, False en caso contrario.
        """
        try:
            # Configurar los parámetros de actualización del stop loss
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": ticket,
                "sl": nuevo_sl,
                "deviation": 10,
                "magic": 234000,  # Número mágico para identificar la orden
                "comment": "Actualización de stop loss desde Python",
            }

            # Enviar la solicitud de actualización del stop loss
            result = mt5.order_send(request)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(f"Error al actualizar el stop loss: {result.retcode}")
                return False

            logging.info(f"Stop loss actualizado correctamente: {result}")
            return True

        except Exception as e:
            logging.error(f"Error al actualizar el stop loss: {e}")
            return False