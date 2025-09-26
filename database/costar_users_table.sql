-- CONFIGURAÇÃO DA TABELA COSTAR_USERS
-- Execute este SQL no SQL Editor do Supabase

-- Criar tabela personalizada de usuários se não existir
CREATE TABLE IF NOT EXISTS public.costar_users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT NOT NULL DEFAULT 'free' CHECK (role IN ('free', 'pro', 'enterprise', 'admin')),
    is_active BOOLEAN DEFAULT true,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Habilitar RLS
ALTER TABLE public.costar_users ENABLE ROW LEVEL SECURITY;

-- Política para usuários verem apenas seus dados
DROP POLICY IF EXISTS "Users can view own data" ON public.costar_users;
CREATE POLICY "Users can view own data" ON public.costar_users
    FOR SELECT USING (
        auth.uid()::text = id::text OR 
        EXISTS (
            SELECT 1 FROM public.costar_users 
            WHERE id::text = auth.uid()::text AND role = 'admin'
        ) OR
        auth.uid() IS NULL
    );

-- Política para inserção (registro)
DROP POLICY IF EXISTS "Anyone can register" ON public.costar_users;
CREATE POLICY "Anyone can register" ON public.costar_users
    FOR INSERT WITH CHECK (true);

-- Política para atualização
DROP POLICY IF EXISTS "Users can update own data" ON public.costar_users;
CREATE POLICY "Users can update own data" ON public.costar_users
    FOR UPDATE USING (
        auth.uid()::text = id::text OR 
        EXISTS (
            SELECT 1 FROM public.costar_users 
            WHERE id::text = auth.uid()::text AND role = 'admin'
        )
    );

-- Índices
CREATE INDEX IF NOT EXISTS idx_costar_users_email ON public.costar_users(email);
CREATE INDEX IF NOT EXISTS idx_costar_users_username ON public.costar_users(username);
CREATE INDEX IF NOT EXISTS idx_costar_users_role ON public.costar_users(role);

-- Inserir configuração inicial na tabela system_settings se ela existir
INSERT INTO public.system_settings (key, value, description, is_public) VALUES
('costar_users_table_created', 'true', 'Tabela costar_users foi criada', false)
ON CONFLICT (key) DO UPDATE SET value = 'true', updated_at = NOW();