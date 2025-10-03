#!/usr/bin/env python3
"""
Script de teste e configuração do Supabase
"""
import asyncio
import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.supabase_config import check_configuration, get_config
from app.services.supabase_base_service import SupabaseService

class SupabaseSetupTester:
    """Classe para testar e configurar Supabase"""
    
    def __init__(self):
        self.config = get_config()
        self.service = None
        
    def print_header(self, title: str):
        """Imprime cabeçalho formatado"""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)
    
    def print_status(self, status: str, message: str, success: bool = True):
        """Imprime status com cores"""
        icon = "✅" if success else "❌"
        print(f"{icon} {status}: {message}")
    
    def check_environment_variables(self) -> bool:
        """Verifica variáveis de ambiente"""
        self.print_header("VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE")
        
        config_check = check_configuration()
        status = config_check['status']
        validation = config_check['validation']
        
        # Status geral
        print(f"📊 URL configurada: {'✅' if status['url_set'] else '❌'}")
        print(f"🔑 Chave anônima: {'✅' if status['anon_key_set'] else '❌'}")
        print(f"🔐 Chave de serviço: {'✅' if status['service_key_set'] else '❌'}")
        print(f"⚙️  Debug: {'✅' if status['debug'] else '❌'}")
        print(f"⏱️  Timeout: {status['timeout']}s")
        
        # Validações
        if validation['errors']:
            print("\n🚨 ERROS ENCONTRADOS:")
            for error in validation['errors']:
                print(f"   ❌ {error}")
        
        if validation['warnings']:
            print("\n⚠️  AVISOS:")
            for warning in validation['warnings']:
                print(f"   ⚠️  {warning}")
        
        ready = config_check['ready_for_public']
        self.print_status(
            "Configuração",
            "Pronta para uso público" if ready else "Incompleta - configure as variáveis",
            ready
        )
        
        return ready
    
    def test_connection(self) -> bool:
        """Testa conexão com Supabase"""
        self.print_header("TESTE DE CONEXÃO")
        
        try:
            # Inicializa serviço
            self.service = SupabaseService()
            
            # Testa conexão pública
            print("🔍 Testando conexão pública (com RLS)...")
            public_result = self.service.test_connection(use_admin=False)
            public_ok = public_result.get('status') == 'connected'
            self.print_status("Conexão Pública", "Sucesso" if public_ok else f"Falhou: {public_result.get('message', 'erro desconhecido')}", public_ok)
            
            # Testa conexão admin se disponível
            if self.config.has_admin_access():
                print("\n🔍 Testando conexão administrativa (sem RLS)...")
                admin_result = self.service.test_connection(use_admin=True)
                admin_ok = admin_result.get('status') == 'connected'
                self.print_status("Conexão Admin", "Sucesso" if admin_ok else f"Falhou: {admin_result.get('message', 'erro desconhecido')}", admin_ok)
            else:
                print("\n⚠️  Conexão admin não testada (SERVICE_ROLE_KEY não configurada)")
                admin_ok = False
            
            return public_ok
            
        except Exception as e:
            self.print_status("Erro de Conexão", f"Exceção: {e}", False)
            return False
    
    def check_database_schema(self) -> bool:
        """Verifica se o schema do banco existe"""
        self.print_header("VERIFICAÇÃO DO SCHEMA DO BANCO")
        
        if not self.service:
            print("❌ Serviço não inicializado - execute teste de conexão primeiro")
            return False
        
        try:
            # Lista tabelas existentes
            print("🔍 Verificando tabelas existentes...")
            
            # Query para listar tabelas
            query = """
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
            """
            
            result = self.service.execute_query(query, use_admin=True)
            
            if result['success']:
                tables = result['data']
                expected_tables = {
                    'user_profiles', 'prompts', 'prompt_templates', 
                    'template_ratings', 'ai_usage_logs', 'system_settings'
                }
                
                existing_tables = {table['table_name'] for table in tables}
                missing_tables = expected_tables - existing_tables
                
                print(f"📊 Tabelas encontradas: {len(existing_tables)}")
                for table in sorted(existing_tables):
                    print(f"   ✅ {table}")
                
                if missing_tables:
                    print(f"\n❌ Tabelas em falta: {len(missing_tables)}")
                    for table in sorted(missing_tables):
                        print(f"   ❌ {table}")
                    
                    print("\n💡 Para criar as tabelas, execute:")
                    print("   python tests/test_supabase_schema.py")
                    return False
                else:
                    self.print_status("Schema", "Todas as tabelas estão presentes", True)
                    return True
            else:
                self.print_status("Erro", f"Falha ao verificar tabelas: {result.get('error')}", False)
                return False
                
        except Exception as e:
            self.print_status("Erro", f"Exceção ao verificar schema: {e}", False)
            return False
    
    def run_full_test(self) -> Dict[str, bool]:
        """Executa todos os testes"""
        print("🚀 INICIANDO TESTES COMPLETOS DO SUPABASE")
        
        results = {}
        
        # 1. Verifica variáveis de ambiente
        results['environment'] = self.check_environment_variables()
        
        if not results['environment']:
            print("\n🛑 Teste interrompido - configure as variáveis de ambiente primeiro")
            return results
        
        # 2. Testa conexão
        results['connection'] = self.test_connection()
        
        if not results['connection']:
            print("\n🛑 Teste interrompido - problemas de conexão")
            return results
        
        # 3. Verifica schema
        results['schema'] = self.check_database_schema()
        
        # Resultado final
        self.print_header("RESULTADO FINAL")
        
        all_ok = all(results.values())
        
        if all_ok:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Supabase está configurado e pronto para uso")
        else:
            print("⚠️  ALGUNS TESTES FALHARAM:")
            for test, success in results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {test.title()}")
        
        return results

def main():
    """Função principal"""
    tester = SupabaseSetupTester()
    results = tester.run_full_test()
    
    # Código de saída
    exit_code = 0 if all(results.values()) else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    # Executa testes
    main()