import re
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Inicializa o Firebase com a chave da conta de serviço 🔑
cred = credentials.Certificate('chave_firebase.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

ARQUIVO_SQL = 'dados_estoque_jugaad_20261005_223045.sql'

def importar_dados_sql():
    print(f"📖 Lendo o arquivo {ARQUIVO_SQL}...")
    
    with open(ARQUIVO_SQL, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Expressão regular para extrair as tuplas de inserção da tabela materiais
    # Formato: ('codigo', 'imagem', 'nome', 'tipo', qtd_sala, qtd_lab, valor)
    padrao = re.compile(
        r"\('([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*(\d+),\s*(\d+),\s*([\d\.]+)\)"
    )
    
    registros = padrao.findall(conteudo)
    
    if not registros:
        print("⚠️ Nenhum registro encontrado com o padrão especificado.")
        return

    print(f"📦 Foram encontrados {len(registros)} materiais para importação.")

    # 2. Utiliza Batch Writes para gravar em lote com alto desempenho ⚡
    batch = db.batch()
    contador = 0
    total_gravados = 0

    for item in registros:
        codigo, imagem, nome, tipo, qtd_sala, qtd_lab, valor = item
        
        # Como as imagens antigas eram caminhos locais (/static/images/...),
        # mantemos o caminho ou colocamos um fallback se necessário
        doc_ref = db.collection('materiais').document(codigo)
        
        dados = {
            'codigo': codigo,
            'nome': nome,
            'tipo': tipo,
            'imagem': imagem,
            'qtd_sala_1302': int(qtd_sala),
            'qtd_laboratorio': int(qtd_lab),
            'valor': float(valor),
            'atualizadoEm': datetime.utcnow().isoformat()
        }
        
        batch.set(doc_ref, dados)
        contador += 1
        total_gravados += 1

        # O Firestore aceita no máximo 500 operações por batch
        if contador >= 400:
            batch.commit()
            print(f"✅ Lote de {contador} itens gravado com sucesso.")
            batch = db.batch()
            contador = 0

    if contador > 0:
        batch.commit()
        print(f"✅ Último lote de {contador} itens gravado.")

    print(f"\n🎉 Concluído! Total de {total_gravados} materiais salvos no Firebase Firestore.")

if __name__ == '__main__':
    importar_dados_sql()