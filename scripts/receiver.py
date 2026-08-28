import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
import uvicorn

# Resolve caminhos relativos ao local do script
BASE_DIR = Path(__file__).resolve().parent          # Pasta onde o receiver.py está
PARENT_DIR = BASE_DIR.parent                        # Pasta anterior (..)

# Carrega o .env da pasta anterior
ENV_PATH = PARENT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Obtém variáveis do .env com fallback padrão
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "seu_token_secreto_padrao")

DEFAULT_BACKUP_DIR = str(PARENT_DIR / "db" / "backups")
BACKUP_DIR = os.getenv("BACKUP_DIR", DEFAULT_BACKUP_DIR)

# Garante que o diretório de destino exista
os.makedirs(BACKUP_DIR, exist_ok=True)

app = FastAPI()

@app.post("/upload")
async def receive_backup(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    if authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="Não autorizado")
    
    destination_path = os.path.join(BACKUP_DIR, file.filename)
    
    with open(destination_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"status": "sucesso", "arquivo": file.filename}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)