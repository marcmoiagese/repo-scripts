import subprocess
import socket
import sys
import os
import shutil
import tempfile

def check_connectivity(host, port):
    try:
        with socket.create_connection((host, port), timeout=5):
            return True
    except (socket.timeout, socket.error):
        return False
    
# Funció per descarregar el fitxer docker-compose.yml
def download_docker_compose():
    url = 'https://raw.githubusercontent.com/marcmoiagese/compose-repo/master/openmanage/docker-compose.yml'
    output = 'docker-compose.yml'
    subprocess.run(['wget', url, '-O', output], check=True)
    print(f"Fitxer {output} descarregat correctament.")


# Funció per crear el fitxer docker-compose.override.yml
def create_override():
    default_user = "admin"
    default_pass = "T3rr3N3170R"
    default_ports = "1311:1311"

    # Preguntar usuari
    user = input(f"Introdueix l'usuari (per defecte '{default_user}'): ").strip()

    # Preguntar contrasenya
    password = input(f"Introdueix la contrasenya (per defecte '{default_pass}'): ").strip()

    # Preguntar ports
    ports = input(f"Introdueix els ports a exportar (per defecte '{default_ports}'): ").strip()

    # Crear el contingut del docker-compose.override.yml
    override_content = f"""
version: '3.9'

services:
  omsa:
    environment:
"""

    # Afegir usuari si està definit
    if user:
        override_content += f"      OMSA_USER: \"{user}\"\n"
    else:
        override_content += f"      OMSA_USER: \"{default_user}\"\n"

    # Afegir contrasenya si està definida
    if password:
        override_content += f"      OMSA_PASS: \"{password}\"\n"
    else:
        override_content += f"      OMSA_PASS: \"{default_pass}\"\n"

    # Afegir ports si estan definits
    if ports:
        override_content += "    ports:\n"
        for port in ports.split(','):
            override_content += f"      - \"{port}\"\n"
    else:
        override_content += f"    ports:\n      - \"{default_ports}\"\n"

    # Escriure el fitxer docker-compose.override.yml
    with open('docker-compose.override.yml', 'w') as file:
        file.write(override_content)

    print("Fitxer docker-compose.override.yml creat correctament.")

def run_docker_compose_up(target_dir):
    try:
        subprocess.run(['docker', 'compose', 'up', '-d'], cwd=target_dir, check=True)
        print("Els serveis de Docker s'han iniciat correctament.")
    except subprocess.CalledProcessError as e:
        print(f"Error executant 'docker compose up -d': {e}")
        sys.exit(1)

def delete_yml_files():
    yml_files = glob.glob('*.yml')
    for file in yml_files:
        os.remove(file)
        print(f"Fitxer {file} eliminat correctament.")

# Executar les funcions
if __name__ == "__main__":
    if not check_connectivity('github.com', '443'):
        print("No hi ha connectivitat amb github.com")
        sys.exit(1)
    
    if not check_connectivity('hub.docker.com', '443'):
        print("No hi ha connectivitat amb github.com")
        sys.exit(1)
    
    download_docker_compose()
    create_override()
    run_docker_compose_up('./')
    delete_yml_files()