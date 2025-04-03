# -*- coding: utf-8 -*-
import configparser

class ConfigLoader:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def get(self, section, key):
        """Obtiene un valor de una sección y clave específica."""
        return self.config.get(section, key)

    def get_int(self, section, key):
        """Obtiene un valor entero."""
        return self.config.getint(section, key)

    def get_float(self, section, key):
        """Obtiene un valor flotante."""
        return self.config.getfloat(section, key)

    def get_boolean(self, section, key):
        """Obtiene un valor booleano."""
        return self.config.getboolean(section, key)
    
# ## Ejemplo de uso:
# from config_loader import ConfigLoader

# # Cargar configuraciones
# config = ConfigLoader('config.ini')

# # Acceder a valores específicos
# api_key = config.get('general', 'api_key')
# symbol = config.get('trading', 'symbol')
# lot_size = config.get_float('trading', 'lot_size')

# print(f"API Key: {api_key}")
# print(f"Trading Symbol: {symbol}")
# print(f"Lot Size: {lot_size}")

    def escribir_configuracion(self): # TODO: Añadir un try-except para manejar errores al escribir el archivo.
        """
        Permite al usuario modificar la configuración del robot.
        """
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

    def leer_configuracion(self):
        """
        Muestra las configuraciones actuales del archivo config.ini.
        """
        config_path = "configuracion/config.ini"
        config = configparser.ConfigParser()
        config.read(config_path)

        print("\n### Configuración Actual ###")
        for seccion in config.sections():
            print(f"[{seccion}]")
            for clave, valor in config[seccion].items():
                print(f"{clave} = {valor}")
            print()