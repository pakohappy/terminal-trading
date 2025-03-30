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