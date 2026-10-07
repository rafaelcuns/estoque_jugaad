# Estoque Jugaad

Um site para guardar quantidades do estoque de materiais. O site vai estar dentro da placa Arduino Uno Q, sendo ofertada localmente pelo Flask com mDNS em Python e com seu banco na núvem operando como uma Single Page Application (SPA) com BaaS.

## Como instalar

1. Clonar repositório no Arduino Uno Q

2. Colar credenciais do `firebaseConfig.js` no código HTML

3. Adicionar servidor para executar na inicialização do sistema (Debian)

## Para fazer

- [x] Reformular app.py e index.html para novo modelo SPA com BaaS
- [ ] Importar imagens do backup para Firestore em base64 