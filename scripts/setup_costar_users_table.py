"""
Script para configurar tabela de usuários no Supabase
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.supabase_base_service import SupabaseService

def setup_user_table():
    """Configurar tabela de usuários personalizada"""
    print("🔧 CONFIGURANDO TABELA DE USUÁRIOS")
    print("="*40)
    
    service = SupabaseService()
    
    if not service.enabled:
        print("❌ Supabase não configurado!")
        return False
    
    print("✅ Supabase conectado")
    
    # SQL para criar tabela personalizada de usuários
    create_table_sql = """
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
    """
    
    try:
        # Executar SQL
        result = service.admin_client.rpc('exec_sql', {'sql': create_table_sql}).execute()
        print("✅ Tabela costar_users configurada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar tabela: {str(e)}")
        print("\n💡 Execute manualmente no SQL Editor do Supabase:")
        print(create_table_sql)
        return False

def test_table():
    """Testar tabela criada"""
    print("\n🧪 TESTANDO TABELA")
    print("="*20)
    
    service = SupabaseService()
    
    try:
        # Testar select na tabela
        result = service.admin_client.table("costar_users").select("count").execute()
        print("✅ Tabela acessível")
        
        # Contar usuários
        count_result = service.admin_client.table("costar_users").select("*", count="exact").execute()
        user_count = count_result.count if count_result.count is not None else 0
        print(f"📊 Total de usuários: {user_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar tabela: {str(e)}")
        return False

def main():
    """Função principal"""
    success = setup_user_table()
    
    if success:
        test_table()
        print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
        print("📋 Próximos passos:")
        print("   1. Execute test_supabase_integration.py")
        print("   2. Execute create_admin_user_supabase.py")
    else:
        print("\n❌ CONFIGURAÇÃO FALHOU")
        print("   Execute o SQL manualmente no Supabase")

if __name__ == "__main__":
    main()