import os
import socket
import atexit
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from zeroconf import ServiceInfo, Zeroconf
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
CORS(app) # Libera o navegador do celular para fazer alterações

# Configuração da pasta de upload de imagens
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images', 'materiais')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configurações do Banco de Dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'estoque_jugaad')
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/materiais', methods=['GET'])
def get_materiais():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM materiais")
        materiais = cursor.fetchall()
        
        for mat in materiais:
            if 'valor' in mat and mat['valor'] is not None:
                mat['valor'] = float(mat['valor'])
                
        return jsonify(materiais), 200
    except Exception as e:
        print(f"[ERRO GET] {e}")
        return jsonify({'erro': str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/materiais', methods=['POST'])
def add_material():
    nome = request.form.get('nome', '').strip()
    codigo = (request.form.get('codigo') or request.form.get('id', '')).strip()
    tipo = request.form.get('tipo', 'Geral').strip() or 'Geral'

    if not nome or not codigo:
        return jsonify({'erro': 'Nome e ID são obrigatórios'}), 400

    if 'imagem' not in request.files:
        return jsonify({'erro': 'Nenhuma imagem foi enviada'}), 400

    imagem_file = request.files['imagem']
    if not imagem_file or imagem_file.filename == '':
        return jsonify({'erro': 'Arquivo de imagem inválido'}), 400

    try:
        # Obter extensão e gerar nome seguro baseado no código/ID
        _, ext = os.path.splitext(imagem_file.filename)
        ext = ext.lower() if ext else '.png'
        safe_code = "".join(c for c in codigo if c.isalnum() or c in ('-', '_')).strip() or 'material'
        nome_arquivo = f"{safe_code}{ext}"

        caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
        imagem_file.save(caminho_salvar)

        caminho_db = f"/static/images/materiais/{nome_arquivo}"

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO materiais (codigo, nome, imagem, tipo, qtd_sala_1302, qtd_laboratorio, valor)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (codigo, nome, caminho_db, tipo, 0, 0, 0.0))
        conn.commit()

        print(f"[NOVO MATERIAL] Inserido com sucesso: {codigo} - {nome} ({caminho_db})")
        return jsonify({
            'mensagem': 'Material adicionado com sucesso',
            'material': {
                'codigo': codigo,
                'nome': nome,
                'imagem': caminho_db,
                'tipo': tipo,
                'qtd_sala_1302': 0,
                'qtd_laboratorio': 0,
                'valor': 0.0
            }
        }), 201

    except mysql.connector.Error as err:
        print(f"[ERRO POST MYSQL] {err}")
        if err.errno == 1062:
            return jsonify({'erro': f'Já existe um material com o ID/Código "{codigo}".'}), 409
        return jsonify({'erro': f'Erro no banco de dados: {str(err)}'}), 500
    except Exception as e:
        print(f"[ERRO POST] {e}")
        return jsonify({'erro': str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Rota sem restrição de tipo e sem o 404 manual
@app.route('/api/materiais/<codigo>', methods=['PATCH'])
def update_quantidade(codigo):
    print(f"\n--- INÍCIO DA ATUALIZAÇÃO ---")
    print(f"Código do material alvo: {codigo}")
    
    dados = request.get_json()
    print(f"Dados recebidos do celular: {dados}")
    
    if not dados:
        return jsonify({'erro': 'Nenhum dado fornecido'}), 400

    campos_permitidos = ['qtd_sala_1302', 'qtd_laboratorio']
    campos_atualizar = []
    valores = []

    for campo in campos_permitidos:
        if campo in dados:
            campos_atualizar.append(f"{campo} = %s")
            valores.append(dados[campo])

    if not campos_atualizar:
        return jsonify({'erro': 'Nenhum campo válido para atualização'}), 400

    valores.append(codigo)
    query = f"UPDATE materiais SET {', '.join(campos_atualizar)} WHERE codigo = %s"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print(f"Executando SQL: {query} com valores {valores}")
        
        cursor.execute(query, tuple(valores))
        conn.commit()
        
        print(f"Sucesso! Linhas alteradas no MySQL: {cursor.rowcount}")
        print(f"--- FIM DA ATUALIZAÇÃO ---\n")
        
        # Mesmo se o rowcount for 0 (valor igual), retornamos 200 OK!
        return jsonify({
            'mensagem': 'Comando recebido e processado com sucesso', 
            'linhas_afetadas': cursor.rowcount
        }), 200
        
    except Exception as e:
        print(f"[ERRO PATCH] Falha no banco de dados: {e}")
        return jsonify({'erro': str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def setup_zeroconf(port):
    ip = get_local_ip()
    zeroconf = Zeroconf()
    info = ServiceInfo(
        "_http._tcp.local.",
        "Estoque Jugaad._http._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=port,
        server="estoque.local.",
        properties={"desc": "API de Estoque Maker"}
    )
    zeroconf.register_service(info)
    return zeroconf, info

if __name__ == '__main__':
    PORTA = int(os.getenv('SERVER_PORT', 5000))
    DEBUG_MODE = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    zc, info = setup_zeroconf(PORTA)
    atexit.register(lambda: zc.unregister_service(info))
    atexit.register(lambda: zc.close())
    
    # ATENÇÃO AQUI: debug=True fará o servidor reiniciar a cada mudança
    app.run(host='0.0.0.0', port=PORTA, debug=DEBUG_MODE, use_reloader=False)