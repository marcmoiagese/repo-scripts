import os
import subprocess
import sys
import shutil
import tempfile
import getpass

# Ruta base
REPO_URL = "https://github.com/marcmoiagese/restoreEC2fromBucket.git" 
WORK_DIR = tempfile.mkdtemp()
DOCKERFILE_CONTENT = """FROM golang:1.22 as builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o /restore-instance restore_ec2.go

FROM ubuntu:latest
COPY --from=builder /restore-instance /restore-instance
"""

def run_cmd(cmd, shell=False, check=True):
    print(f"[+] Executant: {cmd}")
    result = subprocess.run(cmd if not shell else " ".join(cmd), shell=shell, check=check)
    return result

def install_prerequisites():
    missing = []
    for cmd in ["git", "docker", "python3"]:
        if shutil.which(cmd) is None:
            missing.append(cmd)
    if missing:
        print(f"[-] Falten requisits: {', '.join(missing)}")
        sys.exit(1)

def clone_repo():
    print("[+] Clonant repositori...")
    os.chdir(WORK_DIR)
    run_cmd(["git", "clone", REPO_URL, "."])

def create_dockerfile():
    with open("Dockerfile", "w") as f:
        f.write(DOCKERFILE_CONTENT)

def build_docker_image():
    print("[+] Construint imatge Docker...")
    run_cmd(["docker", "build", "-t", "restore-builder", "."])

def extract_executable():
    print("[+] Extraint executable...")
    container_id = (
        subprocess.check_output(["docker", "create", "restore-builder"])
        .decode()
        .strip()
    )
    os.makedirs("/etc/ec2restore", exist_ok=True)
    run_cmd(
        ["docker", "cp", f"{container_id}:/restore-instance", "/etc/ec2restore/restore-instance"]
    )
    run_cmd(["docker", "rm", container_id])
    run_cmd(["docker", "rmi", "restore-builder"])

def ask_config():
    print("[+] Configuració: Llegint des de variables d'entorn")
    config = {
        "bucketName": os.getenv("BUCKET_NAME"),
        "prefix": os.getenv("PREFIX", "exported-images/"),
        "subnetID": os.getenv("SUBNET_ID"),
        "iamRole": os.getenv("IAM_ROLE"),
        "instanceType": os.getenv("INSTANCE_TYPE"),
        "region": os.getenv("AWS_REGION"),
        "projectTag": os.getenv("PROJECT_TAG"),
        "nameTag": os.getenv("NAME_TAG"),
    }

    # Validar camps obligatoris
    required_fields = ["bucketName", "subnetID", "iamRole", "instanceType", "region"]
    missing = [k for k, v in config.items() if v is None and k in required_fields]
    if missing:
        print(f"[-] Falten variables d'entorn: {', '.join(missing)}")
        sys.exit(1)

    with open("/etc/ec2restore/restore.cfg", "w") as f:
        for key, value in config.items():
            if value is not None:
                f.write(f"{key}={value}\n")
    print("[+] Fitxer de configuració creat a /etc/ec2restore/restore.cfg")

def create_launcher_script():
    launcher_path = "/usr/local/bin/restore-ec2"
    script_content = """#!/bin/bash
nohup /etc/ec2restore/restore-instance | tee /var/log/restoreec2-output.log 2>&1 &
echo "[+] Procés iniciat. Vegeu el log: /var/log/restoreec2-output.log"
"""
    with open(launcher_path, "w") as f:
        f.write(script_content)
    os.chmod(launcher_path, 0o755)
    print(f"[+] Script disponible com 'restore-ec2' a {launcher_path}")

def main():
    print("[+] Iniciant procés de compilació...")

    # Comprova prerequisits
    install_prerequisites()

    # Crear directori temporal
    os.chdir(WORK_DIR)
    print(f"[+] Treballant a {WORK_DIR}")

    # Clonar repositori
    clone_repo()

    # Crear Dockerfile si no existeix
    if not os.path.exists("Dockerfile"):
        create_dockerfile()

    # Construir imatge
    build_docker_image()

    # Extreure executable
    extract_executable()

    # Demanar configuració
    ask_config()

    # Crear script de llançament
    create_launcher_script()

    # Netegar
    shutil.rmtree(WORK_DIR)
    print("[+] Procés completat correctament.")
    print("[+] Pots executar el programa amb: restore-ec2")
    print("[+] El log es troba a: /var/log/restoreec2-output.log")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] Aquest script ha d'executar-se com a root.")
        sys.exit(1)

    try:
        main()
    finally:
        # Atexit ja fa cleanup(), però podem cridar-ho manualment també
        pass