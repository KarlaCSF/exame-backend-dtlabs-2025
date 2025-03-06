# Projeto com Prisma e FastAPI

Este projeto utiliza **FastAPI** com **Prisma** e um banco de dados PostgreSQL rodando em um container **Docker**.

## Requisitos
Antes de iniciar, certifique-se de ter os seguintes requisitos instalados em seu ambiente:

- [Docker](https://www.docker.com/get-started)
- [Python 3.8+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/)

## Instalação e Execução

1. **Subir o banco de dados com Docker**

   ```sh
   docker-compose up -d
   ```

2. **Executar o script de inicialização**

   Agora, basta rodar o script `start.sh` para instalar as dependências, sincronizar o banco e iniciar o servidor:

   ```sh
   chmod +x start.sh
   ./start.sh
   ```

## Acesso à Aplicação

Após iniciar o servidor, a API estará disponível em:

- **API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
``
