# Exportar estrutura do banco e os dados no Linux
mysqldump -u root -p -d estoque_jugaad --result-file=estrutura.sql
mysqldump -u root -p -t estoque_jugaad --result-file=dados.sql