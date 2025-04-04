from lib_bot.mt5_connector import MT5Connector
from configuracion.config_loader import ConfigLoader
import logging
import time
import os

class Robot:
    def __init__(self, config_path='configuracion/config.ini'):
        """
        Inicializa el robot de trading.
        """
        self.config = ConfigLoader(config_path)
        self.mt5 = MT5Connector(config_path=config_path)
        self.simbolo = self.config.get('parametros', 'simbolo')
        self.timeframe = self.config.get('parametros', 'timeframe')
        self.cantidad = self.config.get_int('parametros', 'ultimas_velas')

    def imprimir_ultimas_velas_terminal(self):
        """
        Obtiene y muestra las últimas velas en un bucle, refrescando el terminal.
        Permite salir del bucle al presionar 's'.
        """
        print("Presiona 's' para salir del bucle.")
        while True:
            try:
                # Obtener las últimas velas
                df = self.mt5.obtener_ultimas_velas(self.simbolo, self.timeframe, self.cantidad)

                # Limpiar el terminal
                os.system('cls' if os.name == 'nt' else 'clear')

                # Imprimir las velas
                print("\n### Últimas Velas ###")
                print(df)

                # Pausa antes de refrescar
                time.sleep(5)

                # Verificar si el usuario desea salir
                if input("Presiona 's' para salir o Enter para continuar: ").lower() == 's':
                    print("Saliendo del bucle...")
                    break
            except Exception as e:
                logging.error(f"Error al obtener las últimas velas: {e}")
                break