import MetaTrader5 as mt5
from configuracion.config_loader import ConfigLoader
import logging
import pandas as pd

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
            logging.error("Error al obtener información de la cuenta.")
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
            logging.error("Error al obtener información de la terminal.")
            raise ConnectionError("No se pudo obtener información de la terminal")