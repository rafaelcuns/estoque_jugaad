# Exportar estrutura do banco e os dados
mysqldump -u root -p -d estoque_jugaad --result-file=estruturar.sql
mysqldump -u root -p -t estoque_jugaad --result-file=dados.sql