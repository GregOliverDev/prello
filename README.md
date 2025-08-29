# Sistema de Gerenciamento de Tarefas Web

Este projeto é uma aplicação web desenvolvida com Python e Flask, simulando funcionalidades básicas de um sistema de gerenciamento de tarefas, similar ao Trello.

## Funcionalidades

- **Cadastro e autenticação de usuários**
- **Gerenciamento de tarefas**: criar, editar, excluir, atribuir tarefas
- **Status das tarefas**: pendente, em andamento, concluída (com filtro)
- **Dashboard**: tarefa do grupo e/ou pessoais

## Tecnologias

- Python 3.x
- Flask
- Flask-Login
- SQLite
- Bootstrap 5

## Instalação

1. Clone o repositório:
   ```bash
   git clone <url-do-repo>
   cd <pasta-do-projeto>
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install flask flask_sqlalchemy flask_login werkzeug
   ```

4. Rode o sistema:
   ```bash
   python app.py
   ```
   Acesse [http://localhost:5000](http://localhost:5000) no navegador.

## Estrutura

- `app.py` — aplicação principal Flask e rotas
- `templates/` — HTMLs do sistema
- `tarefas.db` — banco SQLite gerado automaticamente

## Observações

- O sistema cria o banco automaticamente na primeira execução.
- Usuários podem criar tarefas, atribuir tarefas para outros, editar e excluir suas próprias tarefas.
- Apenas o dono pode excluir uma tarefa.

## Screenshots

> Adicione prints da tela do sistema rodando aqui!

## Licença

MIT