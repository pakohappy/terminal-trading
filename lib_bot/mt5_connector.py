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

    def shutdown(self):
        """
        Cierra la conexión con MetaTrader 5.
        """
        mt5.shutdown()
        logging.info("MetaTrader 5 cerrado correctamente")

    def account_info(self):
        """
        Devuelve la información de la cuenta.
        """
        account = mt5.account_info()
        if account!=None:
            # display trading account data 'as is'
            print(account)
            # display trading account data in the form of a dictionary
            print("Show account_info()._asdict():")
            account_info_dict = mt5.account_info()._asdict()
            for prop in account_info_dict:
                print("  {}={}".format(prop, account_info_dict[prop]))
            print()
    
            # convert the dictionary into DataFrame and print
            df=pd.DataFrame(list(account_info_dict.items()),columns=['property','value'])
            print("account_info() as dataframe:")
            print(df)
        else:
            logging.error("Error al obtener información de la cuenta")
            raise ConnectionError("No se pudo obtener información de la cuenta")