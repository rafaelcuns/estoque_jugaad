# Estoque Jugaad

Um site para guardar quantidades do estoque de materiais. O site vai estar dentro da placa Arduino Uno Q, sendo ofertada localmente pelo Flask com mDNS em Python e com seu banco de dados na núvem pelo Firebase operando como uma Single Page Application (SPA) com BaaS.

## Como instalar

1. Clonar repositório no Arduino Uno Q

2. Colar credenciais do `firebaseConfig.js` do Firebase no código HTML

3. Programar servidor para executar na inicialização do sistema (Debian)

### Iniciar ao ligar

1. Crie o arquivo de serviço no Systemd
    ```bash
    sudo nano /etc/systemd/system/estoque.service
    ```

2. Cole essas informações, mudando USUARIO para o nome de usuario do sistema
    ```ini
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
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable estoque.service
    sudo systemctl start estoque.service
    ```

## Para fazer

- [x] Reformular app.py e index.html para novo modelo SPA com BaaS
- [x] Importar imagens do backup para Firestore em base64 