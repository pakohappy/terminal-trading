# -*- coding: utf-8 -*-
from configuracion.config_loader import ConfigLoader
from lib_bot.robot1 import Robot1

class Menu:
    def __init__(self):
        """
        Inicializa el menú principal y sus submenús.
        """
        self.opciones = {
            "1": self.configuracion,
            "2": self.ejecutar_robot,
            "S": self.salir
        }
        self.ejecutando = True

    def menu_principal(self):
        """
        Muestra el menú principal.
        """
        print("\n### Menú Principal ###")
        print("[1] - Configuración.")
        print("[2] - Ejecutar Robot.")
        print("[S] - Salir.")

    def ejecutar(self):
        """
        Ejecuta el menú principal en un bucle.
        """
        while self.ejecutando:
            self.menu_principal()
            opcion = input(">>> Selecciona una opción (1-2) o (S) para salir): ").strip().upper()
            accion = self.opciones.get(opcion)
            if accion:
                accion()
            else:
                print(">>> Opción no válida.")

###############################################################################
# Submenú Configuración                                                       #
###############################################################################

    def submenu_configuracion(self):
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
# Submenú ejecutar robot                                                       #
###############################################################################

    def submenu_ejecutar_robot(self): # TODO: Por acabar de implementar.
        submenu_opciones = {
            "1": self.ejecutar_robot1,
            #"2": self.ejecutar_robot2,
            "3": self.volver
        }
    
        while True:
            print("\n### Submenú ROBOT ###")
            print("[1] - Robot 1 (MACD).")
            print("[2] - Robot 2.")
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

    # Ejecutar el robot 1.
    def ejecutar_robot1(self):
        robot = Robot1()
        robot.ejecutar()

    # Ejecutar el robot 1.
    # def ejecutar_robot2(self):
    #     robot = Robot2()
    #     robot.ejecutar()


###############################################################################
# Otros                                                                       #
###############################################################################

    def volver(self):
        print(">>> Volviendo al menú principal...")

    # Finalizar el robot y salir del programa.
    def salir(self):
        print(">>> Saliendo del programa...")
        self.ejecutando = False

    def configuracion(self):
        self.submenu_configuracion()

    def ejecutar_robot(self):
        self.submenu_ejecutar_robot()
    
    
    