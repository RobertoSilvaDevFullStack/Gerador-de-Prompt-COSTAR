-- ========================================
-- RESET COMPLETO + DEPLOY LIMPO - SUPABASE
-- ========================================
-- Este script primeiro limpa tudo e depois recria o schema

-- ========================================
-- PARTE 1: LIMPEZA COMPLETA
-- ========================================

-- Remove políticas RLS (se existem)
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Users can view own prompts" ON public.prompts;
DROP POLICY IF EXISTS "Users can view public prompts" ON public.prompts;
DROP POLICY IF EXISTS "Users can insert own prompts" ON public.prompts;
DROP POLICY IF EXISTS "Users can update own prompts" ON public.prompts;
DROP POLICY IF EXISTS "Users can delete own prompts" ON public.prompts;
DROP POLICY IF EXISTS "Anyone can view active templates" ON public.prompt_templates;
DROP POLICY IF EXISTS "Users can view all ratings" ON public.template_ratings;
DROP POLICY IF EXISTS "Users can insert own ratings" ON public.template_ratings;
DROP POLICY IF EXISTS "Users can update own ratings" ON public.template_ratings;
DROP POLICY IF EXISTS "Users can view own ai logs" ON public.ai_usage_logs;
DROP POLICY IF EXISTS "Users can insert own ai logs" ON public.ai_usage_logs;

-- Remove triggers
DROP TRIGGER IF EXISTS handle_user_profiles_updated_at ON public.user_profiles;
DROP TRIGGER IF EXISTS handle_prompts_updated_at ON public.prompts;
DROP TRIGGER IF EXISTS handle_templates_updated_at ON public.prompt_templates;
DROP TRIGGER IF EXISTS handle_system_settings_updated_at ON public.system_settings;

-- Remove função de trigger
DROP FUNCTION IF EXISTS public.handle_updated_at();

-- Remove tabelas na ordem correta (dependências primeiro)
DROP TABLE IF EXISTS public.template_ratings CASCADE;
DROP TABLE IF EXISTS public.ai_usage_logs CASCADE;
DROP TABLE IF EXISTS public.prompts CASCADE;
DROP TABLE IF EXISTS public.prompt_templates CASCADE;
DROP TABLE IF EXISTS public.user_profiles CASCADE;
DROP TABLE IF EXISTS public.system_settings CASCADE;

-- ========================================
-- PARTE 2: RECRIAÇÃO COMPLETA DO SCHEMA
-- ========================================

-- 1. TABELA DE USUÁRIOS (estende auth.users)
CREATE TABLE public.user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    plan_type VARCHAR(20) DEFAULT 'free' CHECK (plan_type IN ('free', 'pro', 'enterprise')),
    subscription_status VARCHAR(20) DEFAULT 'active' CHECK (subscription_status IN ('active', 'inactive', 'cancelled')),
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    total_prompts_created INTEGER DEFAULT 0,
    total_prompts_analyzed INTEGER DEFAULT 0,
    api_calls_used INTEGER DEFAULT 0,
    api_calls_limit INTEGER DEFAULT 100,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. TABELA DE PROMPTS COSTAR
CREATE TABLE public.prompts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) DEFAULT 'geral',

    -- Dados do formulário COSTAR
    contexto TEXT NOT NULL,
    objetivo TEXT NOT NULL,
    estilo TEXT NOT NULL,
    tom TEXT NOT NULL,
    audiencia TEXT NOT NULL,
    resposta TEXT NOT NULL,

    -- Prompt gerado
    prompt_gerado TEXT NOT NULL,
    prompt_original_data JSONB,

    -- Metadados
    tags TEXT[] DEFAULT '{}',
    is_public BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,

    -- Análise (quando disponível)
    analysis_score INTEGER,
    analysis_quality VARCHAR(20),
    analysis_data JSONB,
    analyzed_at TIMESTAMP WITH TIME ZONE,

    -- Uso e estatísticas
    view_count INTEGER DEFAULT 0,
    copy_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. TABELA DE TEMPLATES PÚBLICOS
CREATE TABLE public.prompt_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,

    -- Template COSTAR
    contexto_template TEXT NOT NULL,
    objetivo_template TEXT NOT NULL,
    estilo_template TEXT NOT NULL,
    tom_template TEXT NOT NULL,
    audiencia_template TEXT NOT NULL,
    resposta_template TEXT NOT NULL,

    -- Metadados
    tags TEXT[] DEFAULT '{}',
    difficulty_level VARCHAR(20) DEFAULT 'beginner' CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    use_case VARCHAR(50),

    -- Estatísticas
    usage_count INTEGER DEFAULT 0,
    rating_average DECIMAL(3,2) DEFAULT 0.00,
    rating_count INTEGER DEFAULT 0,

    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. TABELA DE AVALIAÇÕES DE TEMPLATES
CREATE TABLE public.template_ratings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    template_id UUID REFERENCES public.prompt_templates(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(template_id, user_id)
);

-- 5. TABELA DE HISTÓRICO DE USO DE IA
CREATE TABLE public.ai_usage_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    prompt_id UUID REFERENCES public.prompts(id) ON DELETE SET NULL,

    ai_provider VARCHAR(20) NOT NULL,
    operation_type VARCHAR(20) NOT NULL CHECK (operation_type IN ('generate', 'analyze', 'enhance')),

    -- Dados da requisição
    input_data JSONB,
    output_data JSONB,

    -- Métricas
    tokens_used INTEGER,
    processing_time_ms INTEGER,
    cost_credits DECIMAL(10,4),

    success BOOLEAN NOT NULL,
    error_message TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. TABELA DE CONFIGURAÇÕES DO SISTEMA
CREATE TABLE public.system_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- ÍNDICES PARA PERFORMANCE
-- ========================================

-- Índices para prompts
CREATE INDEX idx_prompts_user_id ON public.prompts(user_id);
CREATE INDEX idx_prompts_category ON public.prompts(category);
CREATE INDEX idx_prompts_created_at ON public.prompts(created_at DESC);
CREATE INDEX idx_prompts_is_public ON public.prompts(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_prompts_tags ON public.prompts USING GIN(tags);

-- Índices para templates
CREATE INDEX idx_templates_category ON public.prompt_templates(category);
CREATE INDEX idx_templates_featured ON public.prompt_templates(is_featured) WHERE is_featured = TRUE;
CREATE INDEX idx_templates_usage ON public.prompt_templates(usage_count DESC);

-- Índices para logs
CREATE INDEX idx_ai_logs_user_id ON public.ai_usage_logs(user_id);
CREATE INDEX idx_ai_logs_created_at ON public.ai_usage_logs(created_at DESC);
CREATE INDEX idx_ai_logs_provider ON public.ai_usage_logs(ai_provider);

-- ========================================
-- TRIGGERS PARA UPDATED_AT
-- ========================================
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger em tabelas relevantes
CREATE TRIGGER handle_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_prompts_updated_at
    BEFORE UPDATE ON public.prompts
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_templates_updated_at
    BEFORE UPDATE ON public.prompt_templates
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_system_settings_updated_at
    BEFORE UPDATE ON public.system_settings
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- ========================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================

-- Habilitar RLS nas tabelas
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prompt_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.template_ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_usage_logs ENABLE ROW LEVEL SECURITY;

-- Políticas para user_profiles
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Políticas para prompts
CREATE POLICY "Users can view own prompts" ON public.prompts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view public prompts" ON public.prompts
    FOR SELECT USING (is_public = TRUE);

CREATE POLICY "Users can insert own prompts" ON public.prompts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own prompts" ON public.prompts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own prompts" ON public.prompts
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para templates (todos podem ler, apenas admins podem modificar)
CREATE POLICY "Anyone can view active templates" ON public.prompt_templates
    FOR SELECT USING (is_active = TRUE);

-- Políticas para ratings
CREATE POLICY "Users can view all ratings" ON public.template_ratings
    FOR SELECT USING (TRUE);

CREATE POLICY "Users can insert own ratings" ON public.template_ratings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own ratings" ON public.template_ratings
    FOR UPDATE USING (auth.uid() = user_id);

-- Políticas para ai_usage_logs
CREATE POLICY "Users can view own ai logs" ON public.ai_usage_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own ai logs" ON public.ai_usage_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ========================================
-- DADOS INICIAIS
-- ========================================

-- Configurações iniciais do sistema
INSERT INTO public.system_settings (key, value, description, is_public) VALUES
('app_version', '"1.0.0"', 'Versão atual da aplicação', TRUE),
('maintenance_mode', 'false', 'Modo de manutenção ativo/inativo', TRUE),
('ai_providers_enabled', '["groq", "gemini", "huggingface", "cohere", "together"]', 'Provedores de IA habilitados', FALSE),
('default_ai_provider', '"groq"', 'Provedor de IA padrão', FALSE),
('max_prompts_free', '50', 'Máximo de prompts para usuários gratuitos', TRUE),
('max_prompts_pro', '500', 'Máximo de prompts para usuários pro', TRUE);

-- Template exemplo
INSERT INTO public.prompt_templates (
    title, description, category,
    contexto_template, objetivo_template, estilo_template,
    tom_template, audiencia_template, resposta_template,
    tags, difficulty_level, use_case, is_featured
) VALUES (
    'Análise de Dados Empresariais',
    'Template para criar prompts de análise de dados focados em insights empresariais e tomada de decisão.',
    'business',
    'Análise de dados empresariais em [SETOR/EMPRESA]',
    'Criar relatório com insights e recomendações estratégicas',
    'Formal e técnico com linguagem acessível',
    'Profissional e autoritativo',
    'Executivos e gestores de alto nível',
    'Relatório estruturado com gráficos e métricas',
    ARRAY['business', 'análise', 'dados', 'relatório'],
    'intermediate',
    'business_analysis',
    TRUE
);

-- ========================================
-- ✅ RESET + DEPLOY COMPLETO FINALIZADO!
-- ========================================