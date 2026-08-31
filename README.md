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
