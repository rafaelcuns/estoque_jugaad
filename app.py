import os
import socket
import atexit
from flask import Flask, render_template
from flask_cors import CORS
from zeroconf import ServiceInfo, Zeroconf
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
template_folder = TEMPLATES_DIR if os.path.exists(os.path.join(TEMPLATES_DIR, 'index.html')) else BASE_DIR

app = Flask(__name__, template_folder=template_folder)
CORS(app)  # Libera o navegador do celular para fazer alterações

@app.route('/')
def index():
    return render_template('index.html')

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