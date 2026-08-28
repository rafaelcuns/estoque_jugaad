import os
import subprocess
import time
from datetime import datetime
import requests

# Tenta carregar usando python-dotenv, caso nao esteja instalado faz leitura manual
def load_parent_env():
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.exists(env_path):
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=env_path)
        except ImportError:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip("'\""))

load_parent_env()

# Configuracoes do Banco de Dados obtidas do .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "")

# Configuracoes do Windows Receptor
WINDOWS_HOSTNAME = os.getenv("WINDOWS_HOSTNAME", "pc.local")
WINDOWS_PORT = os.getenv("WINDOWS_PORT", "8000")
UPLOAD_URL = f"http://{WINDOWS_HOSTNAME}:{WINDOWS_PORT}/upload"
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "123456789098765432")

BACKUP_TEMP_DIR = "/tmp/mysql_backups"
os.makedirs(BACKUP_TEMP_DIR, exist_ok=True)

def generate_dump(filepath):
    # Executa o mysqldump e compacta com gzip para otimizar transferencia
    dump_cmd = (
        f"mysqldump -h {DB_HOST} -u {DB_USER} -p'{DB_PASS}' {DB_NAME} "
        f"| gzip > {filepath}"
    )
    result = subprocess.run(dump_cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def send_file(filepath):
    # Envia o arquivo para o Windows
    filename = os.path.basename(filepath)
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    with open(filepath, "rb") as f:
        files = {"file": (filename, f, "application/gzip")}
        response = requests.post(UPLOAD_URL, headers=headers, files=files, timeout=60)
        return response.status_code == 200

def main():
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dump_filename = f"backup_{DB_NAME}_{timestamp}.sql.gz"
        dump_path = os.path.join(BACKUP_TEMP_DIR, dump_filename)
        
        print(f"[{datetime.now()}] Iniciando dump do banco...")
        if generate_dump(dump_path):
            sent = False
            retry_count = 0
            while not sent:
                try:
                    print(f"[{datetime.now()}] Tentando enviar {dump_filename} para o Windows...")
                    if send_file(dump_path):
                        print(f"[{datetime.now()}] Backup enviado com sucesso!")
                        sent = True
                    else:
                        print(f"[{datetime.now()}] Servidor recusou o arquivo. Tentando em 60s...")
                except Exception as e:
                    print(f"[{datetime.now()}] Falha na conexao: {e}. Tentando novamente em 60s...")
                
                if not sent:
                    time.sleep(60)
                    retry_count += 1
                    if retry_count >= 60:
                        print(f"[{datetime.now()}] 1h sem conexao. Descartando dump antigo para gerar um novo...")
                        break
            
            if os.path.exists(dump_path):
                os.remove(dump_path)
        else:
            print(f"[{datetime.now()}] Erro ao gerar mysqldump. Tentando novamente em 60s...")
            time.sleep(60)
            continue
        
        print(f"[{datetime.now()}] Ciclo concluido. Proximo backup em 1 hora.")
        time.sleep(3600)

if __name__ == "__main__":
    main()