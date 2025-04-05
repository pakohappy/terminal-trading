from lib_bot.mt5_connector import MT5Connector
from configuracion.config_loader import ConfigLoader
import logging
import os
import time

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
        self.salir = False  # Variable para controlar la salida del bucle

    def esperar_entrada(self):
        """
        Espera la entrada del usuario durante 5 segundos.
        Si el usuario presiona 's', se establece self.salir = True.
        """
        entrada = input("Presiona 's' para salir o Enter para continuar: ").lower()
        if entrada == 's':
            self.salir = True

    def imprimir_ultimas_velas_terminal(self):
        """
        Obtiene y muestra las últimas velas en un bucle, refrescando el terminal.
        Permite salir del bucle al presionar 's' o actualizar manualmente al presionar 'a'.
        """
        print("Presiona 's' para salir o 'a' para actualizar manualmente.")
        while not self.salir:
            try:
                # Obtener las últimas velas
                df = self.mt5.obtener_ultimas_velas(self.simbolo, self.timeframe, self.cantidad)

                # Limpiar el terminal
                os.system('cls' if os.name == 'nt' else 'clear')

                # Imprimir las velas
                print("\n### Últimas Velas ###")
                print(df)

                # Esperar la entrada del usuario
                print("Presiona 's' para salir o 'a' para actualizar manualmente.")
                entrada = input(">>> ").lower()

                if entrada == 's':
                    self.salir = True
                    print("Saliendo del bucle...")
                    break
                elif entrada == 'a':
                    # Actualizar manualmente (el bucle continuará)
                    continue
                else:
                    print("Opción no válida. Presiona 's' para salir o 'a' para actualizar.")

            except Exception as e:
                logging.error(f"Error al obtener las últimas velas: {e}")
                break