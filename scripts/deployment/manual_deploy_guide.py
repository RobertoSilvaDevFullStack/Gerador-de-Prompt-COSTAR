#!/usr/bin/env python3
"""
Script para gerar instruções de deployment manual do schema Supabase
O cliente Python do Supabase tem limitações para SQL bruto, então este script
gera instruções para aplicar o schema manualmente no painel do Supabase.
"""
import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.supabase_config import get_config, check_configuration

class SupabaseManualDeployGuide:
    """Gerador de guia para deployment manual"""
    
    def __init__(self):
        self.config = get_config()
        self.schema_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'database', 
            'schema.sql'
        )
    
    def print_header(self, title: str):
        """Imprime cabeçalho formatado"""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)
    
    def check_config(self) -> bool:
        """Verifica configuração"""
        self.print_header("VERIFICAÇÃO DA CONFIGURAÇÃO")
        
        config_check = check_configuration()
        
        if config_check['ready_for_public']:
            print("✅ Configuração Supabase: OK")
            print(f"   📍 URL: {self.config.url}")
            print(f"   🔑 Chaves: Configuradas")
            return True
        else:
            print("❌ Configuração Supabase: Incompleta")
            for error in config_check['validation']['errors']:
                print(f"   ❌ {error}")
            return False
    
    def load_schema(self) -> str:
        """Carrega o arquivo de schema"""
        try:
            if not os.path.exists(self.schema_file):
                print(f"❌ Arquivo de schema não encontrado: {self.schema_file}")
                return None
                
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            lines = len(schema_sql.split('\n'))
            print(f"✅ Schema carregado: {lines} linhas")
            return schema_sql
            
        except Exception as e:
            print(f"❌ Erro ao carregar schema: {e}")
            return None
    
    def generate_deployment_guide(self):
        """Gera guia completo de deployment"""
        print("🚀 GUIA DE DEPLOYMENT MANUAL DO SCHEMA SUPABASE")
        print("Como o cliente Python tem limitações, use o editor SQL do Supabase")
        
        # 1. Verifica configuração
        if not self.check_config():
            print("\n🛑 Configure o Supabase primeiro!")
            return False
        
        # 2. Carrega schema
        self.print_header("CARREGAMENTO DO SCHEMA")
        schema_sql = self.load_schema()
        if not schema_sql:
            return False
        
        # 3. Gera instruções
        self.print_header("INSTRUÇÕES DE DEPLOYMENT")
        
        print("📋 PASSO A PASSO:")
        print()
        print("1️⃣  ACESSE O PAINEL SUPABASE:")
        print(f"   👆 Vá para: {self.config.url}")
        print("   👆 Faça login no seu projeto")
        print()
        print("2️⃣  ABRA O EDITOR SQL:")
        print("   👆 Na barra lateral esquerda, clique em 'SQL Editor'")
        print("   👆 Clique em 'New query' ou '+ New Query'")
        print()
        print("3️⃣  COPIE E EXECUTE O SCHEMA:")
        print("   👆 Copie todo o conteúdo abaixo")
        print("   👆 Cole no editor SQL do Supabase")
        print("   👆 Clique em 'Run' para executar")
        print()
        
        self.print_header("SCHEMA SQL PARA COPIAR")
        print("👇 COPIE TUDO ABAIXO 👇")
        print()
        print(schema_sql)
        print()
        print("👆 COPIE TUDO ACIMA 👆")
        
        self.print_header("APÓS EXECUTAR O SCHEMA")
        print("4️⃣  VERIFICAR SE DEU CERTO:")
        print("   👆 No painel Supabase, vá para 'Table Editor'")
        print("   👆 Você deve ver estas 6 tabelas:")
        print("      ✅ user_profiles")
        print("      ✅ prompts") 
        print("      ✅ prompt_templates")
        print("      ✅ template_ratings")
        print("      ✅ ai_usage_logs")
        print("      ✅ system_settings")
        print()
        print("5️⃣  ATIVAR O MODO SUPABASE NO CÓDIGO:")
        print("   👆 Edite: services/integrated_data_service.py")
        print("   👆 Na linha ~40, REMOVA estas 2 linhas:")
        print('   👆 # print("ℹ️  Usando modo demo (Supabase será habilitado posteriormente)")')
        print('   👆 # return')
        print()
        print("6️⃣  TESTAR O SISTEMA:")
        print("   👆 Reinicie o servidor: python main_demo.py")
        print("   👆 Execute: python scripts/test_supabase_setup.py")
        print("   👆 Deve mostrar: ✅ Todos os testes passaram!")
        
        print()
        print("🎉 PRONTO! Seu sistema estará rodando com Supabase!")
        
        return True

def main():
    """Função principal"""
    guide = SupabaseManualDeployGuide()
    success = guide.generate_deployment_guide()
    
    if success:
        print("\n✅ Guia gerado com sucesso!")
        print("📋 Siga as instruções acima para aplicar o schema")
    else:
        print("\n❌ Não foi possível gerar o guia")
        sys.exit(1)

if __name__ == "__main__":
    main()