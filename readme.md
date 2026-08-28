# Estoque rápido Equipe Jugaad

Um pequeno servidor em Python com banco de dados MySQL rodando dentro da placa embarcada Arduino Uno Q para contar estoque de materiais maker de maneira facilitada.

## Tecnologias

- Servidor Flask com mDNS para descoberta .local na rede
- Scripts para envio e recebimento de backups periódicos para um computador central
- Utilização de Shell e Systemd para funcionamento na inicialização

## Para fazer
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
3. Prepare o banco de dados (altere o usuario e a senha)

    ```console
    sudo systemctl enable mariadb

    sudo mysql -e "CREATE DATABASE IF NOT EXISTS estoque_jugaad;"

    sudo mysql estoque_jugaad < db/estrutura.sql

    # Importar dados caso necessário
    sudo mysql estoque_jugaad < db/dados.sql

    sudo mysql -e "CREATE USER 'usuario'@'localhost' IDENTIFIED BY 'senha123'; GRANT ALL PRIVILEGES ON nome_do_banco.* TO 'usuario'@'localhost'; FLUSH PRIVILEGES;"
    ```

4. Renomeie o arquivo `.env.example` para apenas `.env` e altere os dados necessários (como usuario e senha do banco)

5. Execute

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

### Backup para notebook periódico

#### Sender (Linux)
1. Crie o arquivo do serviço do backup com `sudo nano /etc/systemd/system/estoque_sender.service`

2. Cole no arquivo a configuração (Mudando o USUARIO e o CAMINHO_DO_PROJETO para o local do repositório):

    ```console
    [Unit]
    Description=Serviço de Backup Contínuo MySQL
    After=network.target mariadb.service

    [Service]
    Type=simple
    User=rafael
    WorkingDirectory=/home/USUARIO/estoque_jugaad/scripts
    ExecStart=/usr/bin/python3 /home/USUARIO/estoque_jugaad/scripts/sender.py
    Restart=always
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```
3. Altere o `.env` com a informação de hostname do computador para onde vai o backup. Altere também o token caso julgar necessário

4. Habilite o serviço

    ```console
    sudo systemctl daemon-reload
    sudo systemctl enable estoque_sender.service
    sudo systemctl start estoque_sender.service
    ```

#### Receiver (Windows)

1. Registre a tarefa pelo Powershell (Alterando CAMINHO)

    ```console
    Register-ScheduledTask -TaskName "MySQLBackupReceiver" -Action (New-ScheduledTaskAction -Execute (Get-Command pythonw.exe).Source -Argument '"C:\CAMINHO\receiver.py"') -Trigger (New-ScheduledTaskTrigger -AtStartup) -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)) -User "NT AUTHORITY\SYSTEM" -RunLevel Highest -Force
    ```

2. Libere no Firewall

    ```console
    New-NetFirewallRule -DisplayName "MySQL Backup Receiver (8000)" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
    ```

3. Altere no `.env` o AUTH_TOKEN