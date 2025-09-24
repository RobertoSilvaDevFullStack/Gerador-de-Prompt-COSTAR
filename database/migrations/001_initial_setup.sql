-- Migração inicial para COSTAR Prompt Generator
-- Execute este SQL no Supabase para criar as tabelas necessárias

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criação da tabela de prompts
CREATE TABLE IF NOT EXISTS prompts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    contexto TEXT NOT NULL,
    objetivo TEXT NOT NULL,
    estilo TEXT NOT NULL,
    tom TEXT NOT NULL,
    audiencia TEXT NOT NULL,
    resposta TEXT NOT NULL,
    prompt_completo TEXT NOT NULL,
    usuario_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    categoria VARCHAR(100) DEFAULT 'geral',
    tags TEXT[] DEFAULT '{}',
    favorito BOOLEAN DEFAULT FALSE,
    compartilhado BOOLEAN DEFAULT FALSE,
    usos INTEGER DEFAULT 0,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criação da tabela de templates
CREATE TABLE IF NOT EXISTS templates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    contexto TEXT NOT NULL,
    objetivo TEXT NOT NULL,
    estilo TEXT NOT NULL,
    tom TEXT NOT NULL,
    audiencia TEXT NOT NULL,
    resposta TEXT NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    publico BOOLEAN DEFAULT TRUE,
    usuario_criador UUID REFERENCES auth.users(id),
    usos INTEGER DEFAULT 0,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criação da tabela de histórico de uso
CREATE TABLE IF NOT EXISTS historico_prompts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    prompt_id UUID REFERENCES prompts(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    acao VARCHAR(50) NOT NULL, -- 'gerado', 'copiado', 'enviado_gemini'
    metadados JSONB,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_prompts_usuario_id ON prompts(usuario_id);
CREATE INDEX IF NOT EXISTS idx_prompts_categoria ON prompts(categoria);
CREATE INDEX IF NOT EXISTS idx_prompts_criado_em ON prompts(criado_em DESC);
CREATE INDEX IF NOT EXISTS idx_templates_categoria ON templates(categoria);
CREATE INDEX IF NOT EXISTS idx_templates_publico ON templates(publico);
CREATE INDEX IF NOT EXISTS idx_historico_usuario_id ON historico_prompts(usuario_id);

-- Políticas de segurança (RLS - Row Level Security)
ALTER TABLE prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE historico_prompts ENABLE ROW LEVEL SECURITY;

-- Política para prompts - usuários só podem gerenciar seus próprios prompts
CREATE POLICY "Usuários podem gerenciar seus próprios prompts" ON prompts
    FOR ALL USING (auth.uid() = usuario_id);

-- Política para templates - usuários podem ver templates públicos e gerenciar os próprios
CREATE POLICY "Usuários podem ver templates públicos" ON templates
    FOR SELECT USING (publico = TRUE OR auth.uid() = usuario_criador);

CREATE POLICY "Usuários podem gerenciar seus próprios templates" ON templates
    FOR INSERT WITH CHECK (auth.uid() = usuario_criador);

CREATE POLICY "Usuários podem atualizar seus próprios templates" ON templates
    FOR UPDATE USING (auth.uid() = usuario_criador);

CREATE POLICY "Usuários podem deletar seus próprios templates" ON templates
    FOR DELETE USING (auth.uid() = usuario_criador);

-- Política para histórico - usuários só podem gerenciar seu próprio histórico
CREATE POLICY "Usuários podem gerenciar seu próprio histórico" ON historico_prompts
    FOR ALL USING (auth.uid() = usuario_id);

-- Função para incrementar contador de usos
CREATE OR REPLACE FUNCTION incrementar_usos_prompt(prompt_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE prompts 
    SET usos = usos + 1, 
        atualizado_em = NOW()
    WHERE id = prompt_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para incrementar contador de usos de templates
CREATE OR REPLACE FUNCTION incrementar_usos_template(template_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE templates 
    SET usos = usos + 1, 
        atualizado_em = NOW()
    WHERE id = template_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para atualizar timestamp automaticamente
CREATE OR REPLACE FUNCTION atualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualizar timestamps automaticamente
CREATE TRIGGER trigger_prompts_atualizar_timestamp
    BEFORE UPDATE ON prompts
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_timestamp();

CREATE TRIGGER trigger_templates_atualizar_timestamp
    BEFORE UPDATE ON templates
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_timestamp();

-- Inserir templates iniciais
INSERT INTO templates (nome, descricao, contexto, objetivo, estilo, tom, audiencia, resposta, categoria, publico, usuario_criador) VALUES
('Marketing Digital', 'Template para campanhas de marketing, copywriting e estratégias de vendas', 'Você é um especialista em marketing digital com 10 anos de experiência em campanhas de alta conversão', 'Criar uma estratégia de marketing completa para aumentar vendas', 'Profissional e orientado a resultados, com dados e métricas', 'Persuasivo e confiante, mas não agressivo', 'Empresários e profissionais de marketing', 'Plano estruturado com estratégias, táticas e métricas de acompanhamento', 'marketing', true, null),

('Criação de Conteúdo', 'Para blogs, artigos, posts em redes sociais e materiais educativos', 'Você é um redator criativo e estratégico especializado em conteúdo engajante', 'Produzir conteúdo de alta qualidade que eduque e engaje o público', 'Criativo, educativo e envolvente', 'Amigável e acessível, mas autoritativo no assunto', 'Público interessado em aprender sobre o tema', 'Conteúdo estruturado com introdução, desenvolvimento e conclusão clara', 'conteudo', true, null),

('Desenvolvimento', 'Código, documentação técnica e soluções de programação', 'Você é um desenvolvedor sênior com expertise em múltiplas linguagens e frameworks', 'Fornecer soluções técnicas eficientes e bem documentadas', 'Técnico e preciso, com boas práticas de programação', 'Profissional e didático', 'Desenvolvedores e profissionais de TI', 'Código funcional com explicações e documentação adequada', 'tecnologia', true, null),

('Negócios', 'Estratégias empresariais, análises e relatórios profissionais', 'Você é um consultor empresarial com MBA e experiência em estratégia corporativa', 'Desenvolver análises e estratégias de negócio eficazes', 'Analítico e estruturado, baseado em dados', 'Profissional e objetivo', 'Executivos e gestores empresariais', 'Relatório executivo com análises, recomendações e próximos passos', 'negocios', true, null);