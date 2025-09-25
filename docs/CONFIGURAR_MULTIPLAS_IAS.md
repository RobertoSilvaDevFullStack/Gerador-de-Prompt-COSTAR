# 🔑 Guia de Configuração das APIs Gratuitas

## 📋 **APIs Suportadas no Sistema Multi-AI**

### 1. 🟢 **Groq** (Recomendado - Muito Rápido)

- **Website**: https://console.groq.com
- **Limite Gratuito**: 6,000 tokens/minuto
- **Modelos**: Llama 3.1, Mixtral, Gemma
- **Como obter**:
  1. Criar conta gratuita em https://console.groq.com
  2. Ir em "API Keys"
  3. Criar nova chave
  4. Adicionar no `.env`: `GROQ_API_KEY=gsk_xxxxxx`

### 2. 🟡 **Google Gemini** (Atual)

- **Website**: https://makersuite.google.com/app/apikey
- **Limite Gratuito**: 50 requisições/dia
- **Modelo**: Gemini 1.5 Flash
- **Como obter**:
  1. Ir em https://makersuite.google.com/app/apikey
  2. Criar API Key
  3. Adicionar no `.env`: `GEMINI_API_KEY=AIzaSyxxxxxx`

### 3. 🟠 **Hugging Face** (Boa Opção)

- **Website**: https://huggingface.co/settings/tokens
- **Limite Gratuito**: ~1000 requests/dia
- **Modelos**: Diversos modelos open source
- **Como obter**:
  1. Criar conta em https://huggingface.co
  2. Ir em Settings > Access Tokens
  3. Criar token com permissão "Read"
  4. Adicionar no `.env`: `HUGGINGFACE_API_KEY=hf_xxxxxx`

### 4. 🔵 **Cohere** (Qualidade Alta)

- **Website**: https://dashboard.cohere.ai/api-keys
- **Limite Gratuito**: 1,000 calls/mês
- **Modelo**: Command R+
- **Como obter**:
  1. Criar conta em https://dashboard.cohere.ai
  2. Ir em "API Keys"
  3. Copiar chave existente ou criar nova
  4. Adicionar no `.env`: `COHERE_API_KEY=xxxxxx`

### 5. 🟣 **Together AI** (Modelos Avançados)

- **Website**: https://api.together.xyz
- **Limite Gratuito**: $25 em créditos iniciais
- **Modelos**: Llama 2, Mistral, Code Llama
- **Como obter**:
  1. Criar conta em https://api.together.xyz
  2. Ir em "API Keys"
  3. Criar nova chave
  4. Adicionar no `.env`: `TOGETHER_API_KEY=xxxxxx`

## ⚙️ **Configuração Recomendada**

### 🥇 **Setup Ideal (Máxima Disponibilidade)**

Configure pelo menos 3 APIs para garantir disponibilidade 24/7:

```env
# Configuração Multi-AI Recomendada
GROQ_API_KEY=gsk_xxxxxx          # Principal (rápido)
GEMINI_API_KEY=AIzaSyxxxxxx      # Backup primário
HUGGINGFACE_API_KEY=hf_xxxxxx    # Backup secundário
COHERE_API_KEY=xxxxxx            # Emergência
TOGETHER_API_KEY=xxxxxx          # Qualidade especial
```

### 🥈 **Setup Mínimo (Funcional)**

Configure pelo menos 2 APIs:

```env
# Configuração Mínima
GROQ_API_KEY=gsk_xxxxxx          # Principal
GEMINI_API_KEY=AIzaSyxxxxxx      # Backup
```

### 🥉 **Setup Básico (Uma API)**

```env
# Apenas uma API (não recomendado)
GROQ_API_KEY=gsk_xxxxxx
```

## 🚀 **Como o Sistema Funciona**

### 📊 **Priorização Automática**

1. **Groq** (Prioridade 1) - Mais rápido
2. **Gemini** (Prioridade 2) - Boa qualidade
3. **Hugging Face** (Prioridade 3) - Confiável
4. **Cohere** (Prioridade 4) - Alta qualidade
5. **Together AI** (Prioridade 5) - Modelos especiais

### 🔄 **Balanceamento Inteligente**

- **Rotação automática** quando limites são atingidos
- **Detecção de falhas** e troca instantânea
- **Estatísticas de performance** para otimização
- **Fallback inteligente** quando todas as APIs falham

### 📈 **Monitoramento**

- Endpoint `/api/ai/status` mostra status de todas as APIs
- Endpoint `/api/ai/test` testa conectividade
- Logs detalhados de uso e performance

## 🎯 **Benefícios do Sistema Multi-AI**

### ✅ **Disponibilidade 99.9%**

- Se uma API falha, outra assume automaticamente
- Sem interrupção do serviço
- Continuidade garantida

### ⚡ **Performance Otimizada**

- Sempre usa a API mais rápida disponível
- Balanceamento baseado em performance real
- Otimização contínua

### 💰 **Economia de Custos**

- Maximiza uso de limites gratuitos
- Distribui carga entre provedores
- Evita ultrapassar quotas

### 🛡️ **Resiliência**

- Tolerante a falhas de API
- Recuperação automática
- Fallback inteligente

## 🔧 **Comandos de Teste**

### Testar Sistema Multi-AI:

```bash
curl https://seu-projeto.vercel.app/api/ai/test
```

### Ver Status das APIs:

```bash
curl https://seu-projeto.vercel.app/api/ai/status
```

### Resultado Esperado:

```json
{
  "ai_enabled": true,
  "total_providers": 5,
  "available_providers": 3,
  "next_available": "groq",
  "providers_status": [
    {
      "name": "groq",
      "is_active": true,
      "requests_used": "45/6000",
      "success_rate": "98.5%",
      "priority": 1
    }
  ]
}
```

## 🆘 **Solução de Problemas**

### ❌ **"Nenhuma API configurada"**

- Verifique se pelo menos uma chave está no `.env`
- Confirme que a chave não é o valor padrão
- Faça redeploy após adicionar chaves

### ❌ **"Todas as APIs falharam"**

- Verifique conectividade de internet
- Confirme se as chaves são válidas
- Verifique limites de quota

### ❌ **"Performance baixa"**

- Configure mais provedores
- Verifique status com `/api/ai/status`
- Considere usar Groq como principal

---

**💡 Dica**: Configure pelo menos 2-3 APIs para máxima confiabilidade!
