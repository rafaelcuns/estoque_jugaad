import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Inicialização
if not firebase_admin._apps:
    cred = credentials.Certificate('chave_firebase.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def exportar_backup():
    print("⏳ Coletando dados da coleção 'materiais'...")
    colecao = db.collection('materiais').stream()
    
    lista_materiais = []
    for doc in colecao:
        dados = doc.to_dict()
        dados['id'] = doc.id
        lista_materiais.append(dados)
    
    nome_arquivo = f"backup_estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(lista_materiais, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Backup concluído com sucesso! {len(lista_materiais)} itens salvos em: {nome_arquivo}")

if __name__ == '__main__':
    exportar_backup()