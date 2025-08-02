# -*- coding: utf-8 -*-
"""
Generate Robot Template Example: Ejemplo de uso del generador de plantillas de robots

Este script demuestra cómo utilizar el generador de plantillas de robots
para crear rápidamente un nuevo robot de trading personalizado.
"""
import os
from utils.factory.robot_factory import RobotFactory

def generate_example_template():
    """
    Genera una plantilla de ejemplo para un nuevo robot de trading.
    
    Esta función demuestra cómo utilizar el método generate_robot_template
    de la clase RobotFactory para crear rápidamente un nuevo robot.
    """
    # Nombre de la clase del nuevo robot
    template_name = "RSIRobot"
    
    # Ruta donde se guardará la plantilla
    output_path = "utils/robots/rsi_robot.py"
    
    print(f"Generando plantilla para el robot '{template_name}' en '{output_path}'...")
    
    # Generar la plantilla
    RobotFactory.generate_robot_template(template_name, output_path)
    
    # Verificar que se ha creado el archivo
    if os.path.exists(output_path):
        print(f"¡Plantilla generada con éxito!")
        print(f"Ahora puedes editar el archivo '{output_path}' para implementar tu estrategia.")
        
        # Mostrar los primeros pasos a seguir
        print("\nPasos a seguir:")
        print("1. Edita el archivo para implementar tu estrategia de trading.")
        print("2. Implementa el método analyze_market() con tu lógica de análisis.")
        print("3. Opcionalmente, personaliza el método manage_positions().")
        print("4. Registra el nuevo robot en la factory:")
        print("   RobotFactory.register_robot_type('rsi', 'utils.robots.rsi_robot.RSIRobot')")
        print("5. Establece una configuración predeterminada:")
        print("   RobotFactory.set_default_config('rsi', {...})")
        print("6. Crea una configuración JSON en el directorio 'configs/'.")
        print("7. ¡Prueba tu nuevo robot!")
    else:
        print("Error: No se pudo generar la plantilla.")

if __name__ == "__main__":
    generate_example_template()