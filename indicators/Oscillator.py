import logging
import pandas as pd

class Oscillator:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def stochastic(self,
                   k_period: int = 5,
                   d_period: int = 3,
                   smooth_k: int = 3,
                   overbought_level: int = 80,
                   oversold_level: int = 20,
                   mode: int = 0) -> int:
        """
        Calcula el Indicador Estocástico con suavizado adicional, detecta señales de
        sobrecompra/sobreventa, divergencias y cruces de líneas. Permite ajustar niveles dinámicamente.

        :param k_period: Número de periodos para calcular %K inicial (por defecto 5).
        :param d_period: Número de periodos para calcular %D inicial (por defecto 3).
        :param smooth_k: Período de suavizado adicional aplicado a la línea %K (por defecto 3).
        :param overbought_level: Nivel de sobrecompra personalizado (por defecto 80).
        :param oversold_level: Nivel de sobreventa personalizado (por defecto 20).
        :param mode: Especifica la información que queremos que retorne (por defecto 0).
                    Por defecto devuelve la señal cuando hay un cruce de %K_suavizado y %D,
                    bajista en sobrecompra y alcista en sobreventa.
                    "mode = 1": Detecta precios en zona de sobreventa/sobrecompra.
        """
        # Validaciones generales.
        if not {'high', 'low', 'close'}.issubset(self.df.columns):
            logging.error("STOCHASTIC - El DataFrame debe contener las columnas 'High', 'Low' y 'Close'.")
            raise ValueError("STOCHASTIC - El DataFrame debe contener las columnas 'High', 'Low' y 'Close'.")
        if len(self.df) < k_period:
            logging.error("STOCHASTIC - El número de filas no es suficiente para calcular el Indicador Estocástico.")
            raise ValueError("STOCHASTIC - El número de filas no es suficiente para calcular el Indicador Estocástico.")
        if k_period <= 0 or d_period <= 0 or smooth_k <= 0:
            logging.error("STOCHASTIC - Los períodos deben ser mayores que 0.")
            raise ValueError("STOCHASTIC - Los períodos deben ser mayores que 0.")

        # Calcular valores mínimos y máximos (rango para %K).
        self.df['low_min'] = self.df['low'].rolling(window=k_period).min()
        self.df['high_max'] = self.df['high'].rolling(window=k_period).max()

        # Calcular %K inicial.
        self.df['%K'] = ((self.df['close'] - self.df['low_min']) /
                         (self.df['high_max'] - self.df['low_min'])) * 100

        # Suavizar %K.
        self.df['%K_suavizado'] = self.df['%K'].rolling(window=smooth_k).mean()

        # Calcular %D (media móvil de %K_suavizado).
        self.df['%D'] = self.df['%K_suavizado'].rolling(window=d_period).mean()

        # Eliminar valores NaN.
        self.df.dropna(subset=['%K_suavizado', '%D'], inplace=True)

        # Detectar sobrecompra/sobreventa.
        self.df['sobrecompra'] = self.df['%K_suavizado'] > overbought_level
        self.df['sobreventa'] = self.df['%K_suavizado'] < oversold_level

        # Detectar cruces de %K_suavizado y %D.
        self.df['cruce_al_alza'] = (self.df['%K_suavizado'].shift(1) < self.df['%D'].shift(1)) & \
                                   (self.df['%K_suavizado'] > self.df['%D'])
        self.df['cruce_a_la_baja'] = (self.df['%K_suavizado'].shift(1) > self.df['%D'].shift(1)) & \
                                     (self.df['%K_suavizado'] < self.df['%D'])

        # Detectar cruces en sobrecompra/sobreventa.
        self.df['cruce_al_alza_en_sobrecompra'] = self.df['sobrecompra'] & self.df['cruce_al_alza']
        self.df['cruce_a_la_baja_en_sobrecompra'] = self.df['sobrecompra'] & self.df['cruce_a_la_baja']
        self.df['cruce_al_alza_en_sobreventa'] = self.df['sobreventa'] & self.df['cruce_al_alza']
        self.df['cruce_a_la_baja_en_sobreventa'] = self.df['sobreventa'] & self.df['cruce_a_la_baja']

        # Detectar divergencias.
        self.df['divergencia_alcista'] = (
            (self.df['close'] < self.df['close'].shift(1)) &  # Mínimo más bajo en precio
            (self.df['%K_suavizado'] > self.df['%K_suavizado'].shift(1))  # Mínimo más alto en %K
        )
        self.df['divergencia_bajista'] = (
            (self.df['close'] > self.df['close'].shift(1)) &  # Máximo más alto en precio
            (self.df['%K_suavizado'] < self.df['%K_suavizado'].shift(1))  # Máximo más bajo en %K
        )

        # Señales basadas en cruces y divergencias.
        # ultimo_cruce_al_alza_sobrecompra = self.df['cruce_al_alza_en_sobrecompra'].iloc[-1]
        ultimo_cruce_a_la_baja_sobrecompra = self.df['cruce_a_la_baja_en_sobrecompra'].iloc[-1]
        ultimo_cruce_al_alza_sobreventa = self.df['cruce_al_alza_en_sobreventa'].iloc[-1]
        # ultimo_cruce_a_la_baja_sobreventa = self.df['cruce_a_la_baja_en_sobreventa'].iloc[-1]
        # ultima_divergencia_alcista = self.df['divergencia_alcista'].iloc[-1]
        # ultima_divergencia_bajista = self.df['divergencia_bajista'].iloc[-1]
        ultima_sobrecompra = self.df['sobrecompra'].iloc[-1]
        ultima_sobreventa = self.df['sobreventa'].iloc[-1]

        columnas_print = ['time',
                          'cruce_a_la_baja_en_sobrecompra',
                          'cruce_al_alza_en_sobreventa',
                          'sobrecompra',
                          'sobreventa']
        print(self.df[columnas_print])

        # Detectamos cruces en zonas de sobrecompra/sobreventa.
        if mode == 0:
            if ultimo_cruce_al_alza_sobreventa:
                return 2
            elif ultimo_cruce_a_la_baja_sobrecompra:
                return 1
            else:
                return -1

        # Detectamos zona de sobrecompra/sobreventa.
        if mode == 1:
            if ultima_sobreventa:
                return 2
            elif ultima_sobrecompra:
                return 1
            else:
                return -1

        else:
            return -1