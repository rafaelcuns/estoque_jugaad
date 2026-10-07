import json
import sys
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate('chave_firebase.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def restaurar_backup(nome_arquivo):
    print(f"📖 Lendo arquivo de backup: {nome_arquivo}...")
    
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            materiais = json.load(f)
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo {nome_arquivo} não encontrado.")
        return

    batch = db.batch()
    contador = 0
    total = 0

    for item in materiais:
        codigo = item.get('codigo') or item.get('id')
        if not codigo:
            continue
        
        doc_ref = db.collection('materiais').document(codigo)
        batch.set(doc_ref, item)
        contador += 1
        total += 1

        if contador >= 400:
            batch.commit()
            batch = db.batch()
            contador = 0

    if contador > 0:
        batch.commit()

    print(f"♻️ Restauração concluída! {total} itens foram restaurados no Firestore.")

if __name__ == '__main__':
    # Você pode passar o nome do arquivo json via argumento: python restaurar_firestore.py backup_xxx.json
    if len(sys.argv) > 1:
        arquivo = sys.argv[1]
    else:
        arquivo = input("Digite o nome do arquivo JSON de backup a ser restaurado: ").strip()
    
    restaurar_backup(arquivo)