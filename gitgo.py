import subprocess
import argparse
from colorama import Fore

def git_push(commit_message):
    try:
        # Ejecutar "git add --all"
        subprocess.run(["git", "add", "--all"], check=True)
        print(Fore.GREEN + ">>> Archivos añadidos al índice.")

        # Ejecutar "git commit -m 'mensaje'"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print(Fore.GREEN + f">>> Commit realizado con mensaje: '{commit_message}'")

        # Ejecutar "git push"
        subprocess.run(["git", "push"], check=True)
        print(Fore.GREEN + ">>> Cambios enviados al repositorio remoto.")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f">>> Error al ejecutar el comando: {e}")
    except Exception as e:
        print(Fore.RED + f">>> Error inesperado: {e}")

if __name__ == "__main__":
    # Configurar argparse para recibir el mensaje del commit como argumento
    parser = argparse.ArgumentParser(description=">>> Script para automatizar git add, commit y push.")
    parser.add_argument("mensaje", type=str, help="Mensaje del commit")
    args = parser.parse_args()

    # Pasar el mensaje al método git_push
    git_push(args.mensaje)