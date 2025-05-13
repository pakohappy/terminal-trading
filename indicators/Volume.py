import logging
import pandas as pd

class Estocastico: # TODO: Por revisar.
                   # TODO: Variables en configuración.
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa la clase Estocastico con un DataFrame.
        """
        self.df = df

    def calcular_estocastico(self, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """
        Calcula el Indicador Estocástico y detecta señales de sobrecompra y sobreventa.
        Agrega las columnas '%K', '%D', 'sobrecompra' y 'sobreventa' al DataFrame.
        
        :param k_period: Número de periodos para calcular %K (por defecto 14).
        :param d_period: Número de periodos para calcular %D (por defecto 3).
        :return: DataFrame con las columnas adicionales.
        """
        # Validar que el DataFrame tenga las columnas necesarias
        if not {'High', 'Low', 'Close'}.issubset(self.df.columns):
            logging.error(" ESTOCÁSTICO - El DataFrame debe contener las columnas 'High', 'Low' y 'Close' para calcular el Estocástico.")
            raise ValueError("El DataFrame debe contener las columnas 'High', 'Low' y 'Close' para calcular el Estocástico.")

        # Calcular el rango alto-bajo para el periodo %K
        self.df['low_min'] = self.df['Low'].rolling(window=k_period).min()
        self.df['high_max'] = self.df['High'].rolling(window=k_period).max()

        # Calcular %K
        self.df['%K'] = ((self.df['Close'] - self.df['low_min']) / (self.df['high_max'] - self.df['low_min'])) * 100

        # Calcular %D (media móvil simple de %K)
        self.df['%D'] = self.df['%K'].rolling(window=d_period).mean()

        # Detectar sobrecompra y sobreventa
        self.df['sobrecompra'] = self.df['%K'] > 80  # Sobrecompra si %K > 80
        self.df['sobreventa'] = self.df['%K'] < 20  # Sobreventa si %K < 20

        return self.df

    def detectar_tendencia(self) -> str:
        """
        Detecta si el último valor indica sobrecompra o sobreventa.
        :return: Mensaje indicando la condición actual.
        """
        ultimo_sobrecompra = self.df['sobrecompra'].iloc[-1]
        ultimo_sobreventa = self.df['sobreventa'].iloc[-1]

        if ultimo_sobrecompra:
            return "Condición de sobrecompra detectada. Posible oportunidad de venta."
        elif ultimo_sobreventa:
            return "Condición de sobreventa detectada. Posible oportunidad de compra."
        else:
            return "No se detectaron condiciones de sobrecompra o sobreventa."