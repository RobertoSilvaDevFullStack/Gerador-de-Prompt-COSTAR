#!/usr/bin/env python3
"""
Script para aplicar o schema do banco de dados Supabase
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

from app.services.supabase_base_service import SupabaseService
from app.config.supabase_config import get_config, check_configuration

class SupabaseSchemaManager:
    """Gerenciador do schema do Supabase"""
    
    def __init__(self):
        self.service = None
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
    
    def print_status(self, status: str, message: str, success: bool = True):
        """Imprime status com cores"""
        icon = "✅" if success else "❌"
        print(f"{icon} {status}: {message}")    
    
    def initialize_service(self) -> bool:
        """Inicializa o serviço Supabase"""
        self.print_header("INICIALIZAÇÃO DO SERVIÇO")
        
        # Verifica configuração
        config_check = check_configuration()
        if not config_check['ready_for_admin']:
            print("❌ Configuração incompleta para operações administrativas")
            print("💡 Certifique-se de ter SUPABASE_SERVICE_ROLE_KEY configurada")
            return False
        
        try:
            self.service = SupabaseService()
            connection_result = self.service.test_connection(use_admin=True)
            connection_ok = connection_result.get('status') == 'connected'
            
            if connection_ok:
                self.print_status("Serviço", "Inicializado com sucesso", True)
                return True
            else:
                self.print_status("Serviço", "Falha na conexão administrativa", False)
                return False
                
        except Exception as e:
            self.print_status("Erro", f"Falha na inicialização: {e}", False)
            return False
    
    def load_schema_file(self) -> str:
        """Carrega o arquivo de schema SQL"""
        self.print_header("CARREGAMENTO DO SCHEMA")
        
        try:
            if not os.path.exists(self.schema_file):
                self.print_status("Arquivo", f"Schema não encontrado: {self.schema_file}", False)
                return None
                
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            lines = len(schema_sql.split('\n'))
            self.print_status("Schema", f"Carregado com {lines} linhas", True)
            return schema_sql
            
        except Exception as e:
            self.print_status("Erro", f"Falha ao carregar schema: {e}", False)
            return None
    
    def apply_schema(self, schema_sql: str) -> bool:
        """Aplica o schema no banco de dados"""
        self.print_header("APLICAÇÃO DO SCHEMA")
        
        try:
            # Separa comandos SQL (split por ponto e vírgula seguido de quebra de linha)
            commands = [cmd.strip() for cmd in schema_sql.split(';\n') if cmd.strip()]
            
            print(f"🔍 Encontrados {len(commands)} comandos SQL para executar")
            
            success_count = 0
            error_count = 0
            
            for i, command in enumerate(commands, 1):
                if not command or command.startswith('--'):
                    continue
                    
                print(f"\n📝 Executando comando {i}/{len(commands)}...")
                
                # Mostra parte do comando para debug
                preview = command[:100] + "..." if len(command) > 100 else command
                print(f"   SQL: {preview}")
                
                try:
                    result = self.service.execute_query(command, use_admin=True)
                    
                    if result['success']:
                        print(f"   ✅ Sucesso")
                        success_count += 1
                    else:
                        print(f"   ❌ Erro: {result.get('error', 'Erro desconhecido')}")
                        error_count += 1
                        
                        # Para em erros críticos
                        if 'permission denied' in str(result.get('error', '')).lower():
                            print("🛑 Erro de permissão - verificar SERVICE_ROLE_KEY")
                            return False
                        
                except Exception as e:
                    print(f"   ❌ Exceção: {e}")
                    error_count += 1
            
            # Resultado final
            print(f"\n📊 RESULTADO DA APLICAÇÃO:")
            print(f"   ✅ Sucessos: {success_count}")
            print(f"   ❌ Erros: {error_count}")
            
            if error_count == 0:
                self.print_status("Schema", "Aplicado com sucesso completo", True)
                return True
            elif success_count > error_count:
                self.print_status("Schema", "Aplicado com alguns erros (maioria ok)", True)
                return True
            else:
                self.print_status("Schema", "Falha na aplicação (muitos erros)", False)
                return False
                
        except Exception as e:
            self.print_status("Erro", f"Falha na aplicação do schema: {e}", False)
            return False
    
    def verify_schema(self) -> bool:
        """Verifica se todas as tabelas foram criadas"""
        self.print_header("VERIFICAÇÃO DO SCHEMA")
        
        try:
            # Lista tabelas criadas
            query = """
            SELECT 
                table_name, 
                table_type,
                (SELECT count(*) FROM information_schema.columns 
                 WHERE table_name=t.table_name AND table_schema='public') as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
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
                extra_tables = existing_tables - expected_tables
                
                print(f"📊 TABELAS ENCONTRADAS: {len(existing_tables)}")
                for table in tables:
                    status = "✅" if table['table_name'] in expected_tables else "ℹ️"
                    print(f"   {status} {table['table_name']} ({table['column_count']} colunas)")
                
                if missing_tables:
                    print(f"\n❌ TABELAS EM FALTA: {len(missing_tables)}")
                    for table in sorted(missing_tables):
                        print(f"   ❌ {table}")
                
                if extra_tables:
                    print(f"\nℹ️  TABELAS EXTRAS: {len(extra_tables)}")
                    for table in sorted(extra_tables):
                        print(f"   ℹ️  {table}")
                
                # Verifica índices
                index_query = """
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND indexname NOT LIKE '%_pkey'
                ORDER BY tablename, indexname;
                """
                
                index_result = self.service.execute_query(index_query, use_admin=True)
                if index_result['success']:
                    indexes = index_result['data']
                    print(f"\n📇 ÍNDICES CRIADOS: {len(indexes)}")
                    for idx in indexes:
                        print(f"   📇 {idx['tablename']}.{idx['indexname']}")
                
                schema_complete = len(missing_tables) == 0
                self.print_status(
                    "Schema", 
                    "Completo e verificado" if schema_complete else "Incompleto - tabelas em falta",
                    schema_complete
                )
                
                return schema_complete
            else:
                self.print_status("Erro", f"Falha na verificação: {result.get('error')}", False)
                return False
                
        except Exception as e:
            self.print_status("Erro", f"Exceção na verificação: {e}", False)
            return False
    
    def run_full_deployment(self) -> Dict[str, bool]:
        """Executa o deployment completo do schema"""
        print("🚀 INICIANDO DEPLOYMENT DO SCHEMA SUPABASE")
        
        results = {}
        
        # 1. Inicializa serviço
        results['initialization'] = self.initialize_service()
        if not results['initialization']:
            return results
        
        # 2. Carrega schema
        schema_sql = self.load_schema_file()
        results['schema_load'] = bool(schema_sql)
        if not results['schema_load']:
            return results
        
        # 3. Aplica schema
        results['schema_apply'] = self.apply_schema(schema_sql)
        
        # 4. Verifica resultado
        results['verification'] = self.verify_schema()
        
        # Resultado final
        self.print_header("RESULTADO FINAL DO DEPLOYMENT")
        
        all_ok = all(results.values())
        
        if all_ok:
            print("🎉 DEPLOYMENT CONCLUÍDO COM SUCESSO!")
            print("✅ Todas as tabelas e estruturas foram criadas")
            print("🔄 Execute 'python scripts/test_supabase_setup.py' para validar")
        else:
            print("⚠️  DEPLOYMENT COM PROBLEMAS:")
            for step, success in results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {step.replace('_', ' ').title()}")
        
        return results

def main():
    """Função principal"""
    manager = SupabaseSchemaManager()
    results = manager.run_full_deployment()
    
    # Código de saída
    exit_code = 0 if all(results.values()) else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    # Executa deployment
    main()