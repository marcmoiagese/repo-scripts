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
    user = input(f"Introdueix l'usuari (per defecte '{default_user}'): ")
    if not user:
        user = default_user

    # Preguntar contrasenya
    password = input(f"Introdueix la contrasenya (per defecte '{default_pass}'): ")
    if not password:
        password = default_pass

    # Preguntar ports
    ports = input(f"Introdueix els ports a exportar (per defecte '{default_ports}'): ")
    if not ports:
        ports = default_ports

    # Crear el contingut del docker-compose.override.yml
    override_content = f"""
version: '3.9'

services:
  omsa:
    environment:
      OMSA_USER: "{user}"
      OMSA_PASS: "{password}"
    ports:
"""

    # Afegir ports al fitxer override
    for port in ports.split(','):
        override_content += f"      - \"{port}\"\n"

    # Escriure el fitxer docker-compose.override.yml
    with open('docker-compose.override.yml', 'w') as file:
        file.write(override_content)

    print("Fitxer docker-compose.override.yml creat correctament.")

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