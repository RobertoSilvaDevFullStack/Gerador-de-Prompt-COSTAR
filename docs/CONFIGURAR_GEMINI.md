# 🔑 Como Configurar o Gemini AI

## Passo 1: Obter API Key do Google

1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada (começa com "AIza...")

## Passo 2: Configurar no Projeto

1. Abra o arquivo `.env` na raiz do projeto
2. Substitua a linha:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   Por:
   ```
   GEMINI_API_KEY=sua_chave_real_aqui
   ```

## Passo 3: Reiniciar o Projeto

```bash
# Pare o Docker
docker-compose down

# Reconstrua e inicie
docker-compose up --build -d
```

## Passo 4: Testar

Acesse: http://localhost:8000/api/gemini/test

Deve retornar:

```json
{
  "gemini_enabled": true,
  "connection_test": {
    "status": "success",
    "working": true
  }
}
```

## ✅ Funcionalidades que serão habilitadas:

- **Geração Inteligente**: Prompts COSTAR expandidos e melhorados
- **Análise Avançada**: Feedback detalhado sobre qualidade dos prompts
- **Sugestões Personalizadas**: Recomendações específicas para melhorar

## 🚨 Importante:

- A API do Google tem limites gratuitos generosos
- Mantenha sua chave segura (não compartilhe)
- O projeto funciona sem a chave, mas com funcionalidades limitadas

## 🔍 Status Atual:

Verifique em: http://localhost:8000/api/health

- `"gemini": "demo mode"` = Não configurado
- `"gemini": "available"` = Configurado e funcionando
