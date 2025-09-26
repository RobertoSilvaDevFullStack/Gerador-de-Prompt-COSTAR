# 🚀 Guia de Configuração Supabase - COSTAR Prompt Generator

## 📋 **PASSO A PASSO COMPLETO**

### 1️⃣ **Criar Projeto no Supabase**

1. Acesse https://supabase.com
2. Clique em "Start your project"
3. Faça login ou crie uma conta
4. Clique em "New Project"
5. Escolha:
   - **Name**: COSTAR Prompt Generator
   - **Database Password**: Crie uma senha segura (salve!)
   - **Region**: Escolha a mais próxima do Brasil (ex: South America)
6. Clique em "Create new project"
7. **Aguarde 2-3 minutos** para o projeto inicializar

### 2️⃣ **Obter Credenciais**

No painel do seu projeto:

1. Vá em **Settings** → **API**
2. Copie as seguintes informações:

```bash
# URL do projeto
Project URL: https://xxxxxxxxxxxxx.supabase.co

# Chave anônima (public)
anon public: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Chave de serviço (service_role) - SECRETA!
service_role: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

⚠️ **IMPORTANTE**: A chave `service_role` é SECRETA e dá acesso total ao banco!

### 3️⃣ **Configurar Arquivo .env**

Crie/edite o arquivo `.env` na raiz do projeto:

```bash
# Configurações do Supabase
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Suas outras configurações de IA (manter)
GEMINI_API_KEY=sua_chave_gemini
GROQ_API_KEY=sua_chave_groq
# etc...
```

### 4️⃣ **Testar Conexão**

Execute o teste:

```bash
python tests/test_supabase_connection.py
```

Deve exibir: ✅ **Conexão estabelecida com sucesso!**

### 5️⃣ **Próximos Passos Automáticos**

Após configurar, executaremos automaticamente:

- ✅ Criação das tabelas do banco
- ✅ Configuração de autenticação
- ✅ Políticas de segurança (Row Level Security)
- ✅ Integração com o frontend

---

## 🔒 **Segurança**

- ✅ Nunca commite o arquivo `.env` no Git
- ✅ Use `.env.example` como template
- ✅ A chave `service_role` deve ser mantida secreta
- ✅ Use HTTPS sempre em produção

---

## 📞 **Suporte**

Se encontrar problemas:

1. Verifique se o projeto Supabase está "Active"
2. Confirme se copiou as chaves corretamente
3. Teste a conexão com o script fornecido

**Configure as credenciais e execute o teste novamente!** 🚀
