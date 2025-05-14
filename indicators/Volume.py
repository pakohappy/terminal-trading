import logging
import pandas as pd

class Volume: #todo: Por revisar.
    def __init__(self, df: pd.DataFrame):
        self.df = df