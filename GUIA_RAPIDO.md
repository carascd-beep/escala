# Guia Rápido - Sistema de Escalas

## ✅ Sistema Instalado e Funcionando!

O Sistema de Escalas da Paróquia São João Bosco está pronto para uso.

## 🚀 Acesso Imediato

### Aplicação Web
- **URL:** http://localhost:8000
- **Página Inicial:** http://localhost:8000/
- **Escalas Públicas:** http://localhost:8000/escala
- **Login Admin:** http://localhost:8000/login

### Credenciais Iniciais
- **Usuário:** admin
- **Senha:** admin123

⚠️ **IMPORTANTE:** Altere a senha em produção!

### Documentação API
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📊 Status Atual

### Banco de Dados
- ✓ Criado: `data/escala.db` (128 KB)
- ✓ Tabelas criadas
- ✓ Admin inicial criado
- ✓ 11 horários padrão cadastrados

### Dados de Exemplo
- ✓ 3 pessoas cadastradas (João, Maria, Carlos)
- ✓ 8 missas geradas (próximos 7 dias)
- ✓ 1 escala publicada com 3 pessoas

## 🎯 Fluxo de Uso

### 1. Login Administrativo
```
http://localhost:8000/login
Usuário: admin
Senha: admin123
```

### 2. Cadastrar Pessoas
```
Dashboard → Gerenciar Pessoas → Nova Pessoa
- Nome completo
- Nome para exibição
- Tipo (Coroinha/Acólito/Cerimoniário)
- Telefone (opcional)
```

### 3. Gerenciar Horários
```
Dashboard → Gerenciar Horários → Novo Horário
- Dia da semana
- Horário
- Descrição (opcional)
```

### 4. Gerar Missas
```
Dashboard → Gerenciar Escalas → Gerar Missas
- Selecione período (ex: 01/09/2026 a 30/09/2026)
- Sistema cria automaticamente as missas baseadas nos horários
```

### 5. Criar Escalas
```
Dashboard → Gerenciar Escalas
- Selecione uma missa
- Adicione pessoas (Coroinhas, Acólitos, Cerimoniários)
- Publique a escala
```

### 6. Visualização Pública
```
http://localhost:8000/escala
- Sem necessidade de login
- Filtros por data e tipo de servidor
- Compartilhe via WhatsApp
```

## 📱 Recursos Implementados

### ✅ Fase 1 (MVP) - COMPLETO
- [x] Cadastro de pessoas (Coroinhas, Acólitos, Cerimoniários)
- [x] Cadastro de horários de missa
- [x] Geração automática de missas por período
- [x] Criação e gerenciamento de escalas
- [x] Visualização pública das escalas
- [x] Interface responsiva (mobile-first)
- [x] Autenticação administrativa
- [x] API REST completa
- [x] Validação de conflitos de horário
- [x] Prevenção de duplicidade
- [x] Publicação de escalas

### ⏳ Próximas Fases
- [ ] Substituições com histórico
- [ ] Disponibilidade dos servidores
- [ ] Relatórios e estatísticas
- [ ] Exportação PDF/Excel
- [ ] Geração automática inteligente
- [ ] Notificações WhatsApp

## 🔧 Comandos Úteis

### Iniciar Aplicação
```bash
python run.py
# ou
uvicorn app.main:app --reload
```

### Inicializar Banco (primeira vez)
```bash
python -m app.init_db
```

### Executar Testes
```bash
python -m pytest tests/ -v
```

### Backup do Banco
```bash
# Windows
copy data\escala.db data\backup_%DATE:~-4%%DATE:~3,2%%DATE:~0,2%.db

# Linux/Mac
cp data/escala.db data/backup_$(date +%Y%m%d).db
```

## 🌐 Publicação Gratuita

### Opções Recomendadas

#### 1. Railway.app (Mais Simples)
- Gratuito com $5 de crédito mensal
- Persistência de arquivos
- Deploy automático do GitHub
- HTTPS automático

#### 2. Fly.io
- Gratuito com limites generosos
- Persistência de volumes
- HTTPS automático

#### 3. Oracle Cloud (Always Free)
- Controle total
- Persistência completa
- Requer configuração manual

### ⚠️ Atenção com SQLite em Produção
- Faça backup diário obrigatório
- Considere migrar para PostgreSQL se crescer
- Use volume persistente em containers

## 📁 Estrutura do Projeto

```
EscalaCoroinhas/
├── app/                    # Código da aplicação
│   ├── main.py            # FastAPI app
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/           # Schemas Pydantic
│   ├── services/          # Lógica de negócio
│   ├── routers/           # Rotas API e Web
│   ├── templates/         # Templates HTML
│   └── utils/             # Utilitários
├── data/                  # Banco SQLite
│   └── escala.db         # Banco de dados
├── tests/                 # Testes automatizados
├── .env                   # Configurações locais
├── requirements.txt       # Dependências
├── run.py                # Script de execução
└── README.md             # Documentação completa
```

## 🔒 Segurança

### Implementado
- ✅ Senhas com hash bcrypt
- ✅ Tokens JWT com expiração
- ✅ Cookies httponly
- ✅ Validação de input
- ✅ Proteção SQL Injection (ORM)

### Para Produção
- [ ] HTTPS obrigatório
- [ ] Alterar SECRET_KEY
- [ ] Alterar credenciais padrão
- [ ] Rate limiting
- [ ] Backup automático

## 📞 Suporte

### Documentação
- README completo: `README.md`
- API: http://localhost:8000/docs

### Problemas Comuns

**Porta 8000 em uso?**
```bash
# Editar .env e mudar PORT=8001
```

**Banco corrompido?**
```bash
# Deletar e recriar
rm data/escala.db
python -m app.init_db
```

**Esqueceu a senha?**
```bash
# Editar .env e reiniciar
python -m app.init_db
```

## 🎉 Pronto para Usar!

O sistema está funcionando perfeitamente. Acesse http://localhost:8000 e comece a gerenciar as escalas!

---

**Desenvolvido para a Paróquia São João Bosco**
