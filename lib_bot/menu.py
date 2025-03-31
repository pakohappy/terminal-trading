from lib_bot.mt5_connector import MT5Connector

class Menu:
    def __init__(self):
        """
        Inicializa el menú principal y sus submenús.
        """
        self.opciones = {
            "1": self.meta_trader_5,
            "2": self.configuracion,
            "3": self.ayuda,
            "4": self.ejecutar_robot,
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
        print("[4] - Ayuda.")
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
        """
        Permite al usuario modificar la configuración del robot.
        """
        # Cargar el archivo de configuración
        from configuracion.config_loader import ConfigLoader
        import configparser

        config_path = "configuracion/config.ini"
        config = configparser.ConfigParser()
        config.read(config_path)

        print("\n### Modificar Configuración ###")
        print("Secciones disponibles:", list(config.sections()))
        seccion = input(">>> Ingresa la sección que deseas modificar: ").strip()
        if seccion not in config:
            print(">>> La sección no existe.")
            return

        print("Claves disponibles en la sección:", list(config[seccion].keys()))
        clave = input(">>> Ingresa la clave que deseas modificar: ").strip()
        if clave not in config[seccion]:
            print(">>> La clave no existe.")
            return

        nuevo_valor = input(f">>> Ingresa el nuevo valor para '{clave}': ").strip()
        config[seccion][clave] = nuevo_valor

        # Guardar los cambios en el archivo
        with open(config_path, "w") as configfile:
            config.write(configfile)

        print(f">>> Configuración actualizada: [{seccion}] {clave} = {nuevo_valor}")

    def ver_configuracion(self):
        """
        Muestra las configuraciones actuales del archivo config.ini.
        """
        from configuracion.config_loader import ConfigLoader
        import configparser

        config_path = "configuracion/config.ini"
        config = configparser.ConfigParser()
        config.read(config_path)

        print("\n### Configuración Actual ###")
        for seccion in config.sections():
            print(f"[{seccion}]")
            for clave, valor in config[seccion].items():
                print(f"{clave} = {valor}")
            print()

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
            print("1. Información de la cuenta.")
            print("2. Información del terminal.")
            print("3. Volver al Menú Principal.")
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

    def ayuda(self):
        """
        Muestra el submenú de ayuda.
        """
        print(">>> Submenú de Ayuda")
        # Aquí puedes agregar opciones relacionadas con la ayuda del robot

    def ejecutar_robot(self):
        """
        Ejecuta el robot.
        """
        print(">>> Ejecutando el robot")
        # Aquí puedes agregar la lógica para ejecutar el robot
    
    
    