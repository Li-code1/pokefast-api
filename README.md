# 🚀 PokeFast API

Uma API RESTful de alta performance desenvolvida com **FastAPI**, focada no consumo otimizado da PokéAPI original utilizando concorrência paralela, gerenciamento estratégico de cache com Redis e persistência local de dados com SQLite.

O projeto foi totalmente expandido para suportar um ecossistema híbrido: consumo dinâmico e otimizado de microsserviços externos e um repositório relacional local para operações completas de CRUD.

---

## 🔗 Links do Projeto em Produção (Deploy)

A aplicação está publicada de forma totalmente funcional e pode ser acessada nos seguintes endereços:

* **API Online (Render):** [https://pokefast-api-ebac.onrender.com](https://pokefast-api-ebac.onrender.com)
* **Documentação Interativa (Swagger UI):** [https://pokefast-api-ebac.onrender.com/docs](https://pokefast-api-ebac.onrender.com/docs)

---

## 📋 Funcionalidades e Requisitos Atendidos

* **FastAPI & Python 3.10+**: Desenvolvimento estruturado utilizando tipagem estrita (*type hints*) e injeção de dependências corporativa.
* **Processamento Concorrente**: Otimização drástica do tempo de resposta na listagem utilizando `asyncio.gather()` para disparar requisições simultâneas em um pool de conexões reutilizável (`httpx.AsyncClient`).
* **Gerenciamento de Cache**: Integração ativa com o **Redis** para armazenamento temporário estratégico (TTL) de listagens e detalhes de Pokémons, poupando requisições repetidas à API externa.
* **Persistência Relacional Local (CRUD)**: Mapeamento ORM completo com **SQLAlchemy** e banco de dados **SQLite** para criação, leitura, atualização e deleção física de registros customizados.
* **Tratamento Resiliente de Strings**: Sanitização forçada e automática em todos os parâmetros de entrada utilizando métodos nativos (`.strip().lower()`).
* **Testes Automatizados**: Suíte de testes unitários com validação de status HTTP, payloads de resposta e fluxos de exceção usando `pytest` e `pytest-cov`.
* **CI/CD Pipeline**: Automação total integrada ao GitHub Actions para verificação de testes e integridade do código a cada push na branch principal.

---

## ⚙️ Estrutura Modular do Projeto

```text
pokefast-api/
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # Configuração da esteira de CI/CD (GitHub Actions)
│
├── app/
│   ├── main.py                 # Inicializador da API e criação automática das tabelas SQL
│   ├── database.py             # Configuração da Engine SessionLocal e conexão SQLite
│   ├── __init__.py             # Inicializador do pacote app
│   │
│   ├── models/
│   │   ├── __init__.py         # Esquemas de validação e tipagem Pydantic
│   │   └── pokemon.py          # Modelo de Tabela Relacional ORM (SQLAlchemy)
│   │
│   ├── routes/
│   │   └── pokemons.py         # Endpoints da PokéAPI e Rotas de CRUD Local (/local)
│   │
│   ├── services/
│   │   └── poke_service.py     # Lógica assíncrona com asyncio.gather e cache no Redis
│   │
│   └── utils/
│       └── formatters.py       # Funções auxiliares de formatação de strings
│
├── tests/
│   ├── conftest.py             # Configuração de fixtures do pytest para o banco de dados
│   └── test_pokemons.py        # Suíte de testes unitários com pytest
│
├── .gitignore                  # Arquivos ignorados pelo Git (incluindo pokemons.db)
├── pytest.ini                  # Configuração de caminhos do pytest
├── celery_app.py               # Configuração da instância e broker do Celery
├── docker-compose.yml          # Orquestração dos containers (API e Redis)
├── Dockerfile                  # Instruções de montagem da imagem Docker
├── requirements.txt            # Dependências estruturadas do projeto (com SQLAlchemy)
├── tasks.py                    # Definição das tarefas em background e cache
└── README.md                   # Documentação oficial do projeto

```

---

## 🔧 Como Rodar Localmente

### Pré-requisitos

* Python 3.10 ou superior instalado.
* Serviço do Redis rodando localmente (ou via Docker).

### Passo a Passo

1. **Clone o repositório:**

```bash
git clone [https://github.com/Li-code1/pokefast-api.git](https://github.com/Li-code1/pokefast-api.git)
cd pokefast-api

```

2. **Crie e ative um ambiente virtual:**

```bash
python -m venv .venv
# No Windows:
.venv\Scripts\activate
# No Linux/macOS:
source .venv/bin/activate

```

3. **Instale as dependências atualizadas:**

```bash
pip install -r requirements.txt

```

4. **Inicie o servidor de desenvolvimento:**

```bash
python -m uvicorn app.main:app --reload

```

O banco de dados SQLite `pokemons.db` será criado de forma 100% automática na raiz do projeto assim que o servidor for inicializado.

---

## 🧪 Como Executar os Testes e Cobertura

Para rodar a suíte de testes unitários e verificar a integridade das rotas fundamentais, execute:

```bash
PYTHONPATH=. pytest --cov=app tests/ --cov-report=term-missing

```

---

## 📸 Demonstração da API e Evidências do Sistema

Abaixo estão documentadas as evidências visuais coletadas diretamente da interface do Swagger UI e dos ambientes operacionais, comprovando a eficácia e a conformidade técnica com o que foi exigido pelo corpo docente:

### 1. Integração Externa e Links Paginados (`GET /pokemons`)
Consumo em lote paralelo dos dados da PokéAPI externa, gerando links dinâmicos de paginação de forma automatizada:
![Listagem Paginada](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/listagem.JPG)

### 2. Busca Detalhada com Sucesso (`GET /pokemons/{id_or_name}`)
Mapeamento de tipos estruturados com tratamento completo para desconsiderar espaços e caixas altas:
![Busca Detalhada por Nome](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/detalhes.JPG)

### 3. Resiliência e Erro Tratado (Status 404 Not Found)
Tratamento nativo de exceções emitindo o código HTTP correto e o payload limpo esperado pelos testes unitários:
![Erro Pokémon Não Encontrado](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/erro-404.JPG)

### 4. Documentação Automatizada Interativa (Swagger UI)
Interface interativa mapeando claramente as rotas de consumo externo e os endpoints dedicados ao gerenciamento do repositório persistente local:
![Swagger UI](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/swagger.JPG)

### 5. Persistência de Dados - Inserção Local (`POST /pokemons/local`)
**[CREATE]** Endpoint responsável por criar e gravar um novo registro customizado fisicamente no banco de dados SQLite através do SQLAlchemy:
![Cadastro Local](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/1-create-local.jpg)

### 6. Tratamento de Erro - Inserção de Registro Duplicado (Status 400)
Garante a integridade do banco de dados local impedindo que registros com nomes idênticos sejam duplicados:
![Erro Pokémon Repetido](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/pokemon-repetido.JPG)

### 7. Consulta Geral do Repositório (`GET /pokemons/local/all`)
**[READ ALL]** Recuperação em tempo real de todos os Pokémons customizados salvos localmente:
![Listagem Local](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/2-read-all-local.jpg)

### 8. Erro de Consulta Local - Registro Inexistente (Status 404)
Validação do comportamento do endpoint ao tentar buscar por uma chave primária ou nome que não constam na base de dados relacional:
![Erro Consulta Local Não Encontrado](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/pokemon-nao-encontrado.JPG)

### 9. Atualização de Propriedades (`PUT /pokemons/local/{pokemon_id}`)
**[UPDATE]** Edição completa de um registro relacional referenciado por sua respectiva chave primária:
![Atualização Local](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/3-update-local.jpg)

### 10. Erro de Atualização - ID Inexistente (Status 404)
Resposta estruturada emitida quando o usuário tenta alterar atributos de um Pokémon cujo identificador não existe:
![Erro Atualização Não Encontrado](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/atualizacao-nao-encontrado.JPG)

### 11. Exclusão Física de Registro (`DELETE /pokemons/local/{pokemon_id}`)
**[DELETE]** Remoção definitiva de um Pokémon do banco de dados local com retorno apropriado de status `204 No Content`:
![Exclusão Local](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/4-delete-local.jpg)

### 12. Erro de Remoção - ID Inexistente (Status 404)
Validação de segurança impedindo a execução de deleções inválidas em registros inexistentes na base relacional:
![Erro Deleção Não Encontrado](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/deletar-nao-encontrado.JPG)

### 13. Cobertura de Código Local (Pytest-Cov)
Execução local da suite de testes alcançando alto índice de cobertura da lógica implementada no ecossistema:
![Cobertura de Testes](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/teste-passou.JPG)

### 14. Integração Contínua (GitHub Actions Pipeline)
Esteira de CI/CD automatizada validando com absoluto sucesso todas as builds e testes a cada modificação submetida:
![Pipeline de CI/CD](https://raw.githubusercontent.com/Li-code1/pokefast-api/main/screenshots/teste-ci.JPG)