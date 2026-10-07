import os
import io
import base64
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Conexão com o Firebase Firestore 🔑
cred = credentials.Certificate('chave_firebase.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

PASTA_IMAGENS = 'materiais'
MAX_DIMENSAO = (300, 300)  # Largura e altura máximas em pixels
QUALIDADE = 75             # Compressão JPEG (mantém ótima nitidez e fica leve)

def otimizar_e_converter_base64(caminho_imagem):
    """Abre a imagem, redimensiona, comprime em JPEG e retorna a string Data URL Base64."""
    with Image.open(caminho_imagem) as img:
        # Converte formatos com transparência (RGBA/P) para RGB para salvar em JPEG
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Redimensiona proporcionalmente para não distorcer
        img.thumbnail(MAX_DIMENSAO, Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=QUALIDADE, optimize=True)
        bytes_imagem = buffer.getvalue()
        
        base64_str = base64.b64encode(bytes_imagem).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_str}"

def atualizar_fotos_firestore():
    if not os.path.exists(PASTA_IMAGENS):
        print(f"❌ A pasta '{PASTA_IMAGENS}' não foi encontrada no diretório atual.")
        return

    # Filtra apenas os arquivos no padrão de imagem esperado
    arquivos = [
        f for f in os.listdir(PASTA_IMAGENS) 
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ]

    total_arquivos = len(arquivos)
    print(f"🔍 Foram encontradas {total_arquivos} imagens na pasta '{PASTA_IMAGENS}'.")

    batch = db.batch()
    contador_lote = 0
    total_atualizados = 0

    for index, arquivo in enumerate(arquivos, start=1):
        # Extrai o código do material removendo a extensão (ex: 'P00000.png' -> 'P00000')
        codigo = os.path.splitext(arquivo)[0].strip().upper()
        caminho_completo = os.path.join(PASTA_IMAGENS, arquivo)

        try:
            foto_base64 = otimizar_e_converter_base64(caminho_completo)
            
            # Atualiza o documento no Firestore com set(merge=True)
            doc_ref = db.collection('materiais').document(codigo)
            batch.set(doc_ref, {'imagem': foto_base64}, merge=True)
            
            contador_lote += 1
            total_atualizados += 1
            print(f"[{index}/{total_arquivos}] 🖼️ Processado: {codigo} ({arquivo})")

            # O Firestore permite até 500 operações por commit
            if contador_lote >= 400:
                print("⏳ Gravando lote no Firebase Firestore...")
                batch.commit()
                batch = db.batch()
                contador_lote = 0

        except Exception as erro:
            print(f"⚠️ Erro ao processar o arquivo {arquivo}: {erro}")

    if contador_lote > 0:
        print("⏳ Gravando lote final no Firebase Firestore...")
        batch.commit()

    print(f"\n🎉 Concluído com sucesso! {total_atualizados} fotos foram atualizadas no Firestore.")

if __name__ == '__main__':
    atualizar_fotos_firestore()