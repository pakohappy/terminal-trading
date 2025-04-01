from lib_bot.mt5_connector import MT5Connector
from configuracion.config_loader import ConfigLoader
class Menu:
    def __init__(self):
        """
        Inicializa el menú principal y sus submenús.
        """
        self.opciones = {
            "1": self.meta_trader_5,
            "2": self.configuracion,
            "3": self.ejecutar_robot,
            "S": self.salir
        }
        self.ejecutando = True

    def menu_principal(self):
        """
        Muestra el menú principal.
        """
        print("\n### Menú Principal ###")
        print("[1] - Metatrader 5.")
        print("[2] - Configuración.")
        print("[3] - Ejecutar Robot.")
        print("[S] - Salir.")

    def ejecutar(self):
        """
        Ejecuta el menú principal en un bucle.
        """
        while self.ejecutando:
            self.menu_principal()
            opcion = input(">>> Selecciona una opción (1-4) o (S) para salir): ").strip().upper()
            accion = self.opciones.get(opcion)
            if accion:
                accion()
            else:
                print(">>> Opción no válida.")

###############################################################################
# Submenú Configuración                                                       #
###############################################################################

    def submenu_configuracion(self):
        """
        Muestra un submenú relacionado con la configuración del robot.
        """
        submenu_opciones = {
            "1": self.modificar_configuracion,
            "2": self.ver_configuracion,
            "3": self.volver
        }
    
        while True:
            print("\n### Submenú Configuración ###")
            print("[1] - Modificar configuración.")
            print("[2] - Ver configuración actual.")
            print("[3] - Volver.")
            opcion = input(">>> Selecciona una opción (1-3): ")
            accion = submenu_opciones.get(opcion)
            if accion:
                accion()
                # Ajustar la opción para volver al menú principal.
                if opcion == "3":
                    break  # Salir del submenú y volver al menú principal

    def modificar_configuracion(self):
        conf = ConfigLoader()
        conf.escribir_configuracion()

    def ver_configuracion(self):
        conf = ConfigLoader()
        conf.leer_configuracion()

###############################################################################
# Submenú Metatrader 5                                                        #
###############################################################################

    def submenu_metatrader5(self):
        """
        Muestra un submenú relacionado con las opciones del robot.
        """
        submenu_opciones = {
            "1": self.info_cuenta,
            "2": self.info_terminal,
            "3": self.volver
        }
    
        while True:
            print("\n### Submenú Metatrader 5 ###")
            print("[1] - Información de la cuenta.")
            print("[2] - Información del terminal.")
            print("[3] - Volver.")
            opcion = input(">>> Selecciona una opción (1-3): ")
            accion = submenu_opciones.get(opcion)
            if accion:
                accion()
                # Ajunstar la opción para volver al menú principal.
                if opcion == "3":  # Salir del submenú
                    break
            else:
                print(">>> Opción no válida.")

    # Muestra información de la cuenta.
    def info_cuenta(self):
        mt5 = MT5Connector()
        print(mt5.info_cuenta())

    # Muestra información de la terminal.
    def info_terminal(self):
        mt5 = MT5Connector()
        print(mt5.info_terminal())

###############################################################################
# Otros                                                                       #
###############################################################################

    def volver(self):
        """
        Vuelve al menú principal.
        """
        print(">>> Volviendo al menú principal...")

    # Finalizar el robot y salir del programa.
    def salir(self):
        print(">>> Saliendo del programa...")
        self.ejecutando = False
    
    def meta_trader_5(self):
        self.submenu_metatrader5()

    def configuracion(self):
        self.submenu_configuracion()

    def ejecutar_robot(self):
        """
        Ejecuta el robot.
        """
        print(">>> Ejecutando el robot")
        # Aquí puedes agregar la lógica para ejecutar el robot
    
    
    