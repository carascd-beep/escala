# Sistema de Escalas - Paróquia São João Bosco

Sistema web completo para gerenciamento e publicação de escalas de serviço dos Coroinhas, Acólitos e Cerimoniários da Paróquia São João Bosco.

## 🎯 Funcionalidades

### MVP (Fase 1)
- ✅ Cadastro de pessoas (Coroinhas, Acólitos, Cerimoniários)
- ✅ Cadastro de horários de missa
- ✅ Geração automática de missas por período
- ✅ Criação e gerenciamento de escalas
- ✅ Visualização pública das escalas
- ✅ Interface responsiva (mobile-first)
- ✅ Autenticação administrativa
- ✅ API REST completa
- ✅ Validação de conflitos de horário

### Próximas Fases
- ⏳ Substituições com histórico
- ⏳ Disponibilidade dos servidores
- ⏳ Relatórios e estatísticas
- ⏳ Exportação PDF/Excel
- ⏳ Geração automática inteligente de escalas
- ⏳ Notificações WhatsApp

## Arquitetura de execução e publicação

Este projeto possui dois componentes, com responsabilidades separadas:

- **Render:** publica somente o serviço `escala`, que executa a API FastAPI e utiliza o PostgreSQL configurado em `DATABASE_URL`.
- **Streamlit:** é apenas uma interface de visualização local. Não deve ser criado nem publicado como serviço no Render.

### Execução local

Inicie a API:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Em outro terminal, inicie o Streamlit apontando para a API local:

```bash
API_BASE_URL=http://127.0.0.1:8001 python -m streamlit run streamlit_app/app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

Endereços locais:

- API: http://127.0.0.1:8001
- Swagger: http://127.0.0.1:8001/docs
- Streamlit: http://127.0.0.1:8501

Validação rápida:

```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8001/docs').status)"
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health').read().decode())"
```

> Importante: `localhost` ou `127.0.0.1` no Streamlit significa o computador onde o Streamlit está executando. Não use essa URL como `API_BASE_URL` em uma aplicação hospedada publicamente.

### Publicação no Render

O arquivo `render.yaml` declara intencionalmente apenas a API:

```text
serviço: escala-coroinhas-api
runtime: Python 3.11
plano: Free
start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Variáveis obrigatórias no Render:

- `DATABASE_URL`: URI completa do PostgreSQL, cadastrada diretamente como segredo no Render.
- `SECRET_KEY`: gerada pelo Render.
- `ADMIN_USERNAME`, `ADMIN_PASSWORD` e `ADMIN_EMAIL`: cadastradas diretamente como segredos.

Nunca registrar no Git, chat, logs ou screenshots os valores de `DATABASE_URL`, `SECRET_KEY` ou `ADMIN_PASSWORD`.

Fluxo de publicação:

1. Rodar `pytest -q` localmente.
2. Confirmar `git status` limpo e fazer push para `main`.
3. Aguardar o deploy do serviço `escala` no Render.
4. Verificar `/docs`, `/openapi.json` e um endpoint representativo da API pública.
5. Confirmar nos logs que a API conectou no PostgreSQL.
6. Testar criação, edição e persistência de cadastro após reinício.

O status `Deployed` sozinho não comprova conexão com o PostgreSQL; é necessário validar logs e endpoints.

## 🚀 Instalação

### Pré-requisitos
- Python 3.11+
- pip

### Passos

1. **Clone ou baixe o projeto**
```bash
cd EscalaCoroinhas
```

2. **Crie um ambiente virtual**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
# IMPORTANTE: Altere SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD
```

5. **Inicialize o banco de dados**
```bash
python -m app.init_db
```

6. **Execute a aplicação**
```bash
# Opção 1: Usando o script
python run.py

# Opção 2: Usando uvicorn diretamente
uvicorn app.main:app --reload
```

7. **Acesse a aplicação**
- Aplicação: http://localhost:8000
- Documentação API: http://localhost:8000/docs
- Dashboard Admin: http://localhost:8000/login

## 🔐 Credenciais Iniciais

Após executar `python -m app.init_db`, use:
- **Usuário:** admin (ou o valor configurado em ADMIN_USERNAME)
- **Senha:** admin123 (ou o valor configurado em ADMIN_PASSWORD)

**IMPORTANTE:** Altere as credenciais em produção!

## 📱 Uso

### Administrador
1. Acesse http://localhost:8000/login
2. Faça login com as credenciais
3. Cadastre pessoas em `/admin/pessoas`
4. Gerencie horários em `/admin/horarios`
5. Gere missas e crie escalas em `/admin/escalas`
6. Publique as escalas para visualização pública

### Público
1. Acesse http://localhost:8000/escala
2. Visualize as escalas publicadas
3. Filtre por data ou tipo de servidor
4. Compartilhe o link via WhatsApp

## 🏗️ Estrutura do Projeto

```
EscalaCoroinhas/
├── app/
│   ├── main.py              # Aplicação FastAPI
│   ├── config.py            # Configurações
│   ├── database.py          # Configuração do banco
│   ├── init_db.py           # Inicialização do banco
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── person.py
│   │   ├── mass.py
│   │   └── scale.py
│   ├── schemas/             # Schemas Pydantic
│   │   ├── user.py
│   │   ├── person.py
│   │   ├── mass.py
│   │   └── scale.py
│   ├── services/            # Lógica de negócio
│   │   ├── auth_service.py
│   │   ├── person_service.py
│   │   ├── mass_service.py
│   │   └── scale_service.py
│   ├── routers/             # Rotas da API
│   │   ├── api.py           # API REST
│   │   ├── web.py           # Páginas web
│   │   └── auth.py          # Autenticação
│   ├── templates/           # Templates Jinja2
│   │   ├── base.html
│   │   ├── admin/
│   │   └── public/
│   ├── static/              # Arquivos estáticos
│   └── utils/               # Utilitários
│       └── security.py
├── data/                    # Banco SQLite (criado automaticamente)
├── tests/                   # Testes
├── .env.example             # Exemplo de variáveis de ambiente
├── requirements.txt         # Dependências
├── run.py                   # Script de execução
└── README.md                # Este arquivo
```

## 🔧 API REST

A API está documentada automaticamente pelo FastAPI. Acesse:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints Principais

#### Pessoas
- `GET /api/pessoas` - Listar pessoas
- `POST /api/pessoas` - Criar pessoa
- `GET /api/pessoas/{id}` - Buscar pessoa
- `PUT /api/pessoas/{id}` - Atualizar pessoa
- `DELETE /api/pessoas/{id}` - Desativar pessoa

#### Horários
- `GET /api/horarios` - Listar horários
- `POST /api/horarios` - Criar horário
- `PUT /api/horarios/{id}` - Atualizar horário

#### Missas
- `GET /api/missas?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Listar missas
- `POST /api/missas` - Criar missa
- `POST /api/missas/gerar?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Gerar missas

#### Escalas
- `GET /api/escalas?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Listar escalas
- `POST /api/escalas/{mass_id}` - Criar escala
- `POST /api/escalas/{scale_id}/atribuicoes` - Adicionar pessoa
- `PUT /api/escalas/atribuicoes/{id}` - Atualizar atribuição
- `DELETE /api/escalas/atribuicoes/{id}` - Remover atribuição
- `POST /api/escalas/{scale_id}/publicar` - Publicar escala

## 💾 Backup do Banco de Dados

O banco SQLite está em `data/escala.db`. Para fazer backup:

```bash
# Windows
copy data\escala.db data\escala_backup_%DATE:~-4%%DATE:~3,2%%DATE:~0,2%.db

# Linux/Mac
cp data/escala.db data/escala_backup_$(date +%Y%m%d).db
```

**Recomendação:** Faça backup diário em produção!

## 🌐 Publicação Gratuita

### Opções Avaliadas

#### 1. Render.com (Recomendado)
- ✅ Gratuito para aplicações web
- ✅ Deploy automático do GitHub
- ✅ HTTPS automático
- ⚠️ **Problema:** Sistema de arquivos efêmero (SQLite não persiste)
- **Solução:** Usar banco externo ou backup automático

#### 2. Railway.app
- ✅ Gratuito com $5 de crédito mensal
- ✅ Persistência de arquivos
- ✅ HTTPS automático
- ⚠️ Limite de 500 horas/mês

#### 3. Fly.io
- ✅ Gratuito com limites generosos
- ✅ Persistência de volumes
- ✅ HTTPS automático
- ⚠️ Requer configuração mais complexa

#### 4. VPS Gratuito (Oracle Cloud)
- ✅ Always Free Tier
- ✅ Controle total
- ✅ Persistência completa
- ⚠️ Requer configuração manual

### Recomendação

Para MVP, use **Railway.app** ou **Fly.io** com volume persistente para o SQLite.

**Alternativa mais simples:** Hospede localmente e use ngrok para acesso externo temporário.

### WordPress

**Não recomendado** para este projeto porque:
- WordPress é CMS, não framework de aplicação
- Dificuldade de integração com FastAPI
- Complexidade desnecessária para o caso de uso
- Melhor manter WordPress (site institucional) separado do sistema de escalas

Se necessário, integre via iframe ou link externo:
```html
<a href="https://escalas.paroquia.com">Ver Escalas</a>
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app

# Ver relatório
pytest --cov=app --cov-report=html
```

## 🔒 Segurança

### Implementado
- ✅ Senhas com hash bcrypt
- ✅ Tokens JWT com expiração
- ✅ Cookies httponly
- ✅ Validação de input com Pydantic
- ✅ Proteção contra SQL Injection (ORM)
- ✅ Variáveis de ambiente para secrets

### Recomendações para Produção
- [ ] HTTPS obrigatório
- [ ] Rate limiting
- [ ] CORS configurado
- [ ] Backup automático
- [ ] Monitoramento de logs
- [ ] Alterar SECRET_KEY
- [ ] Alterar credenciais padrão

## 📊 Tecnologias

- **Backend:** FastAPI 0.115.0
- **Banco:** SQLite + SQLAlchemy 2.0.36
- **Autenticação:** JWT (python-jose)
- **Templates:** Jinja2
- **Frontend:** Bootstrap 5.3.2
- **Servidor:** Uvicorn

## 🤝 Contribuição

Este é um projeto interno da Paróquia São João Bosco. Para sugestões ou problemas, entre em contato com a equipe de TI.

## 📄 Licença

Projeto interno - Uso restrito à Paróquia São João Bosco.

## 📞 Suporte

Para dúvidas ou suporte:
- Documentação da API: http://localhost:8000/docs
- Issues: (repositório interno)

---

**Desenvolvido com ❤️ para a Paróquia São João Bosco**
