# -*- coding: utf-8 -*-
"""
Módulo para la gestión de la configuración del sistema de trading.

Este módulo proporciona funciones y clases para leer, escribir y manipular
la configuración del sistema almacenada en archivos .ini.
"""
import configparser
import logging
import os
from typing import Optional


def get_config_path(config_file: str = "config.ini") -> str:
    """
    Obtiene la ruta completa al archivo de configuración.
    
    Args:
        config_file: Nombre del archivo de configuración. Por defecto es 'config.ini'.
        
    Returns:
        La ruta completa al archivo de configuración.
    """
    # Asegura que la ruta sea relativa al directorio del proyecto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "configuracion", config_file)


def escribir_configuracion() -> None:
    """
    Permite al usuario modificar interactivamente la configuración del robot.
    
    Esta función muestra las secciones y claves disponibles en el archivo de configuración
    y permite al usuario modificar los valores existentes.
    
    Raises:
        FileNotFoundError: Si no se encuentra el archivo de configuración.
        PermissionError: Si no hay permisos para escribir en el archivo.
        Exception: Para cualquier otro error durante la escritura.
    """
    try:
        config_path = get_config_path()
        config = configparser.ConfigParser()
        
        # Verificar si el archivo existe
        if not os.path.exists(config_path):
            logging.error(f"El archivo de configuración no existe: {config_path}")
            print(f">>> Error: El archivo de configuración no existe: {config_path}")
            return
            
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

        logging.info(f"Configuración actualizada: [{seccion}] {clave} = {nuevo_valor}")
        print(f">>> Configuración actualizada: [{seccion}] {clave} = {nuevo_valor}")
    except FileNotFoundError as e:
        logging.error(f"No se encontró el archivo de configuración: {e}")
        print(f">>> Error: No se encontró el archivo de configuración.")
    except PermissionError as e:
        logging.error(f"Sin permisos para escribir en el archivo de configuración: {e}")
        print(f">>> Error: Sin permisos para escribir en el archivo de configuración.")
    except Exception as e:
        logging.error(f"Error al escribir la configuración: {e}")
        print(f">>> Error al escribir la configuración.")


def leer_configuracion() -> None:
    """
    Muestra las configuraciones actuales del archivo config.ini.
    
    Esta función lee y muestra todas las secciones y valores del archivo de configuración.
    
    Raises:
        FileNotFoundError: Si no se encuentra el archivo de configuración.
        Exception: Para cualquier otro error durante la lectura.
    """
    try:
        config_path = get_config_path()
        
        # Verificar si el archivo existe
        if not os.path.exists(config_path):
            logging.error(f"El archivo de configuración no existe: {config_path}")
            print(f">>> Error: El archivo de configuración no existe: {config_path}")
            return
            
        config = configparser.ConfigParser()
        config.read(config_path)

        print("\n### Configuración Actual ###")
        for seccion in config.sections():
            print(f"[{seccion}]")
            for clave, valor in config[seccion].items():
                print(f"{clave} = {valor}")
            print()
    except Exception as e:
        logging.error(f"Error al leer la configuración: {e}")
        print(f">>> Error al leer la configuración.")

class ConfigLoader:
    """
    Clase para cargar y acceder a la configuración del sistema.
    
    Esta clase proporciona una interfaz para acceder a los valores de configuración
    almacenados en archivos .ini, con métodos específicos para diferentes tipos de datos.
    
    Attributes:
        config (configparser.ConfigParser): El objeto parser de configuración.
    """
    
    def __init__(self, config_file: str = None):
        """
        Inicializa el cargador de configuración.
        
        Args:
            config_file: Ruta al archivo de configuración. Si es None, se usa la ruta por defecto.
                         Por defecto es None.
        
        Raises:
            FileNotFoundError: Si no se encuentra el archivo de configuración.
        """
        self.config = configparser.ConfigParser()
        
        if config_file is None:
            config_file = get_config_path()
        
        # Verificar si el archivo existe
        if not os.path.exists(config_file):
            error_msg = f"El archivo de configuración no existe: {config_file}"
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        self.config.read(config_file)
        logging.info(f"Configuración cargada desde: {config_file}")

    def get(self, section: str, key: str, fallback: Optional[str] = None) -> str:
        """
        Obtiene un valor de texto de una sección y clave específica.
        
        Args:
            section: Nombre de la sección en el archivo de configuración.
            key: Nombre de la clave dentro de la sección.
            fallback: Valor a devolver si la sección o clave no existe. Por defecto es None.
            
        Returns:
            El valor de la configuración como texto.
            
        Raises:
            KeyError: Si la sección o clave no existe y no se proporciona un valor fallback.
        """
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            if fallback is not None:
                logging.warning(f"No se encontró [{section}] {key}, usando valor por defecto: {fallback}")
                return fallback
            logging.error(f"Error al obtener configuración: {e}")
            raise KeyError(f"No se encontró la configuración [{section}] {key}")

    def get_int(self, section: str, key: str, fallback: Optional[int] = None) -> int:
        """
        Obtiene un valor entero de una sección y clave específica.
        
        Args:
            section: Nombre de la sección en el archivo de configuración.
            key: Nombre de la clave dentro de la sección.
            fallback: Valor a devolver si la sección o clave no existe. Por defecto es None.
            
        Returns:
            El valor de la configuración como entero.
            
        Raises:
            KeyError: Si la sección o clave no existe y no se proporciona un valor fallback.
            ValueError: Si el valor no puede convertirse a entero.
        """
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            if fallback is not None:
                logging.warning(f"No se encontró [{section}] {key}, usando valor por defecto: {fallback}")
                return fallback
            logging.error(f"Error al obtener configuración: {e}")
            raise KeyError(f"No se encontró la configuración [{section}] {key}")
        except ValueError as e:
            logging.error(f"Error al convertir a entero [{section}] {key}: {e}")
            raise ValueError(f"El valor de [{section}] {key} no es un entero válido")

    def get_float(self, section: str, key: str, fallback: Optional[float] = None) -> float:
        """
        Obtiene un valor flotante de una sección y clave específica.
        
        Args:
            section: Nombre de la sección en el archivo de configuración.
            key: Nombre de la clave dentro de la sección.
            fallback: Valor a devolver si la sección o clave no existe. Por defecto es None.
            
        Returns:
            El valor de la configuración como flotante.
            
        Raises:
            KeyError: Si la sección o clave no existe y no se proporciona un valor fallback.
            ValueError: Si el valor no puede convertirse a flotante.
        """
        try:
            return self.config.getfloat(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            if fallback is not None:
                logging.warning(f"No se encontró [{section}] {key}, usando valor por defecto: {fallback}")
                return fallback
            logging.error(f"Error al obtener configuración: {e}")
            raise KeyError(f"No se encontró la configuración [{section}] {key}")
        except ValueError as e:
            logging.error(f"Error al convertir a flotante [{section}] {key}: {e}")
            raise ValueError(f"El valor de [{section}] {key} no es un flotante válido")

    def get_boolean(self, section: str, key: str, fallback: Optional[bool] = None) -> bool:
        """
        Obtiene un valor booleano de una sección y clave específica.
        
        Args:
            section: Nombre de la sección en el archivo de configuración.
            key: Nombre de la clave dentro de la sección.
            fallback: Valor a devolver si la sección o clave no existe. Por defecto es None.
            
        Returns:
            El valor de la configuración como booleano.
            
        Raises:
            KeyError: Si la sección o clave no existe y no se proporciona un valor fallback.
            ValueError: Si el valor no puede convertirse a booleano.
        """
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            if fallback is not None:
                logging.warning(f"No se encontró [{section}] {key}, usando valor por defecto: {fallback}")
                return fallback
            logging.error(f"Error al obtener configuración: {e}")
            raise KeyError(f"No se encontró la configuración [{section}] {key}")
        except ValueError as e:
            logging.error(f"Error al convertir a booleano [{section}] {key}: {e}")
            raise ValueError(f"El valor de [{section}] {key} no es un booleano válido")