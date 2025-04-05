from configuracion.config_loader import ConfigLoader
from indicadores.tendencia import Tendencia
from lib_bot.mt5_connector import MT5Connector as mt5C
import MetaTrader5 as mt5
import logging
import time
import os

class Robot1:
    def __init__(self, config_path='configuracion/config.ini'):
        """
        Inicializa el robot con la configuración del archivo config.ini.
        """
        self.config = ConfigLoader(config_path)
        self.simbolo = self.config.get('parametros', 'simbolo')
        self.timeframe = self.config.get('parametros', 'timeframe')
        self.cantidad = self.config.get_int('parametros', 'cantidad')
        self.porcentaje_trailing = self.config.get_float('parametros', 'stop_loss') / 100

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
            df = mt5C.obtener_ultimas_velas(self, simbolo=self.simbolo, timeframe=self.timeframe, cantidad=self.cantidad)

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
            time.sleep(0.25)

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
            logging.info(f"ROBOT1 - Precio actual del símbolo {self.simbolo}:")
            print(f"Precio Bid: {tick.bid}, Precio Ask: {tick.ask}")
        
        simbolo_info = mt5.symbol_info(self.simbolo)
        if simbolo_info is None:
            logging.error(f"ROBOT1 - Error al obtener información del símbolo {self.simbolo}.")
            logging.error(f"ROBOT - Distancia mínima de Stop Loss/Take Profit: {simbolo_info.trade_stops_level}")
        else:
            logging.info(f"ROBOT1 - Información del símbolo {self.simbolo}:")
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
            print(f"Posición {tipo} abierta con éxito. Ticket: {resultado.order}")

    def gestionar_trailing_stop(self):
        """
        Gestiona el trailing stop basado en porcentaje para la posición abierta.
        """
        # Obtener información de la posición abierta
        posiciones = mt5.positions_get(symbol=self.simbolo)
        if posiciones is None or len(posiciones) == 0:
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
            print(f"Error al actualizar el stop loss: {resultado.retcode}")
        else:
            print(f"Stop loss actualizado a {nuevo_stop_loss} para la posición {ticket}.")