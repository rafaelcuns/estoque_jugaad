# Estoque rápido Equipe Jugaad

wjrbwejrbewor

## Para fazer
- Continuar estoque jugaad no AUQ (git clone, enviar banco, rodar no startup)
- Fazer envio de dados periódicos para o Notebook
- Linkar com a planilha

## Como executar em um Debian

1. Instalar dependências de sistema

    ```console
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv git mariadb-server avahi-daemon avahi-utils
    ```

2. Prepare o Python

    ```console
    sudo systemclt start mysql # nao funcionou
    sudo systemctl enable --now avahi-daemon

    cd ~
    git clone https://github.com/rafaelcuns/estoque_jugaad.git
    
    cd estoque_jugaad
    
    python3 -m venv venv
    source venv/bin/activate

    pip install -r requirements.txt
    ```
3. Prepare o banco de dados

    ```console
    sudo systemctl enable mariadb

    sudo mysql -e "CREATE DATABASE IF NOT EXISTS estoque_jugaad;"

    sudo mysql estoque_jugaad < db/estrutura.sql

    # Importar dados caso necessário
    sudo mysql estoque_jugaad < db/dados.sql

    sudo mysql -e "CREATE USER 'usuario'@'localhost' IDENTIFIED BY 'senha123'; GRANT ALL PRIVILEGES ON nome_do_banco.* TO 'usuario'@'localhost'; FLUSH PRIVILEGES;"
    ```
4. Execute

    `python3 app.py`

### Iniciar ao ligar

1. Crie o arquivo de serviço no Systemd
    ```console
    sudo nano /etc/systemd/system/estoque.service
    ```

2. Cole essas informações, mudando USUARIO para o nome de usuario do sistema
    ```console
    [Unit]
    Description=Servico Flask Estoque Jugaad com mDNS
    After=network.target network-online.target avahi-daemon.service
    Wants=network-online.target

    [Service]
    Type=simple
    User=USUARIO
    WorkingDirectory=/home/USUARIO/estoque_jugaad
    ExecStartPre=/bin/sleep 5
    ExecStart=/home/USUARIO/estoque_jugaad/venv/bin/python /home/USUARIO/estoque_jugaad/app.py
    Restart=always
    RestartSec=5
    Environment=PYTHONUNBUFFERED=1

    [Install]
    WantedBy=multi-user.target
    ```

3. Habilite o serviço e reinicie
    ```console
    sudo systemctl daemon-reload
    sudo systemctl enable estoque.service
    sudo systemctl start estoque.service
    ```