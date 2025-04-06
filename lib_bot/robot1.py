from configuracion.config_loader import ConfigLoader
from indicadores.tendencia import Tendencia
import MetaTrader5 as mt5
import pandas as pd
import logging
import time
import os

class Robot1:
    def __init__(self, config_path='configuracion/config.ini'):
        """
        Inicializa el robot con la configuración del archivo config.ini.
        """
        self.config = ConfigLoader(config_path)
        self.login = self.config.get_int('metatrader', 'login')
        self.password = self.config.get('metatrader', 'password')
        self.server = self.config.get('metatrader', 'server')

        self.simbolo = self.config.get('parametros', 'simbolo')
        self.timeframe = self.config.get('parametros', 'timeframe')
        self.cantidad = self.config.get_int('parametros', 'cantidad')
        self.porcentaje_trailing = self.config.get_float('parametros', 'stop_loss') / 100

        # Iniciar conexión con MetaTrader 5
        if not mt5.initialize(login=self.login, password=self.password, server=self.server):
            logging.error(f"Error al inicializar MetaTrader 5: %s", mt5.last_error())
            quit()
        else:
            logging.info("MetaTrader 5 inicializado correctamente")

    def ejecutar(self):
        """
        Ejecuta el robot para abrir posiciones según la señal del MACD.
        """
        while True:
            # Limpiar la consola.
            os.system('cls' if os.name == 'nt' else 'clear')
            print("### Robot1 - Ejecutando ###")
            print(f"Símbolo: {self.simbolo}")
            print(f"Timeframe: {self.timeframe}")
            print(f"Cantidad: {self.cantidad}")
            print(f"Porcentaje Trailing Stop: {self.porcentaje_trailing * 100}%")
            print("Esperando señal del MACD...")

            # Obtener las últimas velas
            #mt5C = MT5Connector()
            df = self.obtener_ultimas_velas(simbolo=self.simbolo, timeframe=self.timeframe, cantidad=self.cantidad)

            # Calcular la señal del MACD
            tendencia = Tendencia(df)
            señal_macd = tendencia.macd()

            # Abrir posición según la señal del MACD
            if señal_macd == 1:
                self.abrir_posicion(tipo="compra")
            elif señal_macd == 0:
                self.abrir_posicion(tipo="venta")
            else:
                logging.info("ROBOT1 - No se detectaron señales para abrir posiciones.")

            # Ejecutar la gestión del trailing stop
            self.gestionar_trailing_stop()

            # Esperar un tiempo antes de la próxima iteración
            time.sleep(5)

    def abrir_posicion(self, tipo):
        """
        Abre una posición en MetaTrader 5 según el tipo especificado.
        :param tipo: 'compra' para abrir una posición larga, 'venta' para abrir una posición corta.
        """
        # Verificar si el símbolo está disponible
        if not mt5.symbol_select(self.simbolo, True):
            logging.error(f"ROBOT1 - El símbolo {self.simbolo} no está disponible.")	

        # Obtener el precio actual del símbolo
        tick = mt5.symbol_info_tick(self.simbolo)
        if tick is None:
            logging.error(f"ROBOT1 - Error al obtener el precio del símbolo {self.simbolo}.")
            print(f"Error: No se pudo obtener el precio del símbolo {self.simbolo}")
        else:
            logging.info(f"ROBOT1 - Precio actual del símbolo {self.simbolo}: Precio Bid: {tick.bid}, Precio Ask: {tick.ask}")
            print(f"Precio Bid: {tick.bid}, Precio Ask: {tick.ask}")
        
        simbolo_info = mt5.symbol_info(self.simbolo)
        if simbolo_info is None:
            logging.error(f"ROBOT1 - Error al obtener información del símbolo {self.simbolo}.")
            logging.error(f"ROBOT - Distancia mínima de Stop Loss/Take Profit: {simbolo_info.trade_stops_level}")
        else:
            logging.info(f"ROBOT1 - Información del símbolo {self.simbolo}:Tamaño mínimo del lote: {simbolo_info.volume_min}, Incremento del lote: {simbolo_info.volume_step}")
            print(f"Tamaño mínimo del lote: {simbolo_info.volume_min}")
            print(f"Incremento del lote: {simbolo_info.volume_step}")

        # Configurar los parámetros de la orden
        precio = tick.ask if tipo == "compra" else tick.bid
        solicitud = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.simbolo,
            "volume": self.config.get_float('parametros', 'lote'),  # Tamaño del lote
            "type": mt5.ORDER_TYPE_BUY if tipo == "compra" else mt5.ORDER_TYPE_SELL,
            "price": precio,
            "sl": 0.0,  # Stop loss (puedes calcularlo dinámicamente)
            "tp": 0.0,  # Take profit (puedes calcularlo dinámicamente)
            "deviation": 10,  # Desviación máxima en puntos
            "magic": 235711,  # Identificador único para la orden
            "comment": f"Orden {tipo} basada en MACD",
            "type_time": mt5.ORDER_TIME_GTC,  # Orden válida hasta que se cancele
            "type_filling": mt5.ORDER_FILLING_IOC,  # Tipo de llenado
        }

        # Enviar la orden
        resultado = mt5.order_send(solicitud)
        if resultado.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(f"Error al abrir la posición: {resultado.retcode}")
        else:
            logging.info(f"Posición {tipo} abierta con éxito. Ticket: {resultado.order}")

    def gestionar_trailing_stop(self):
        """
        Gestiona el trailing stop basado en porcentaje para la posición abierta.
        """
        # Obtener información de la posición abierta
        posiciones = mt5.positions_get(symbol=self.simbolo)
        if posiciones is None or len(posiciones) == 0:
            logging.info(f"No hay posiciones abiertas para el símbolo {self.simbolo}.")
            print(f"No hay posiciones abiertas para el símbolo {self.simbolo}.")
            return

        # Obtener la posición actual
        posicion = posiciones[0]
        precio_entrada = posicion.price_open
        tipo_posicion = posicion.type  # 0 = Compra, 1 = Venta
        stop_loss_actual = posicion.sl

        # Obtener el precio actual del símbolo
        tick = mt5.symbol_info_tick(self.simbolo)
        if tick is None:
            logging.error(f"Error al obtener el precio actual del símbolo {self.simbolo}.")
            logging.error(f"ROBOT1 - Error al obtener el precio actual del símbolo {self.simbolo}.")
            print(f"Error al obtener el precio actual del símbolo {self.simbolo}.")
            return

        precio_actual = tick.bid if tipo_posicion == 0 else tick.ask

        # Calcular el nuevo nivel de stop loss basado en porcentaje
        if tipo_posicion == 0:  # Compra
            nuevo_stop_loss = precio_actual * (1 - self.porcentaje_trailing)
            if stop_loss_actual is None or nuevo_stop_loss > stop_loss_actual:
                self.actualizar_stop_loss(posicion.ticket, nuevo_stop_loss)

        elif tipo_posicion == 1:  # Venta
            nuevo_stop_loss = precio_actual * (1 + self.porcentaje_trailing)
            if stop_loss_actual is None or nuevo_stop_loss < stop_loss_actual:
                self.actualizar_stop_loss(posicion.ticket, nuevo_stop_loss)

    def actualizar_stop_loss(self, ticket, nuevo_stop_loss):
        """
        Actualiza el nivel de stop loss para una posición.
        :param ticket: El ticket de la posición.
        :param nuevo_stop_loss: El nuevo nivel de stop loss.
        """
        solicitud = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl": nuevo_stop_loss,
            "tp": 0.0,  # No se modifica el take profit
            "symbol": self.simbolo,
        }

        resultado = mt5.order_send(solicitud)
        if resultado.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(f"Error al actualizar el stop loss: {resultado.retcode}")
            # Si el error es de tipo TRADE_RETCODE_INVALID_SL, significa que el stop loss no es válido.
        else:
            logging.info(f"Stop loss actualizado a {nuevo_stop_loss} para la posición {ticket}.")
            # Si la actualización del stop loss fue exitosa, se imprime el nuevo nivel de stop loss.

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
            rates = mt5.copy_rates_from_pos(simbolo, mt5_timeframe, 0, cantidad)

            # Convertir a DataFrame
            df = pd.DataFrame(rates)

            # Convertir la columna 'time' a formato datetime
            df['time'] = pd.to_datetime(df['time'], unit='s')

            # print("\n### Últimas velas como dataframe:")
            # print(df)

            return df
    
        except Exception as e:
            logging.error(f"MT5_CONNECTOR - Error al obtener las velas: {e}")
            raise RuntimeError(f"Error al obtener las velas: {e}")