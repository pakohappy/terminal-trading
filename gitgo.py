import subprocess
import argparse

def git_push(commit_message):
    try:
        # Ejecutar "git add --all"
        subprocess.run(["git", "add", "--all"], check=True)
        print(">>> Archivos añadidos al índice.")

        # Ejecutar "git commit -m 'mensaje'"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print(f">>> Commit realizado con mensaje: '{commit_message}'")

        # Ejecutar "git push"
        subprocess.run(["git", "push"], check=True)
        print(">>> Cambios enviados al repositorio remoto.")
    except subprocess.CalledProcessError as e:
        print(f">>> Error al ejecutar el comando: {e}")
    except Exception as e:
        print(f">>> Error inesperado: {e}")

if __name__ == "__main__":
    # Configurar argparse para recibir el mensaje del commit como argumento
    parser = argparse.ArgumentParser(description=">>> Script para automatizar git add, commit y push.")
    parser.add_argument("mensaje", type=str, help="Mensaje del commit")
    args = parser.parse_args()

    # Pasar el mensaje al método git_push
    git_push(args.mensaje)