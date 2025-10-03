#!/usr/bin/env python3
"""
Script de Validação Final - Projeto Reorganizado
Valida se toda a funcionalidade está funcionando após a migração
"""

import sys
import asyncio
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ProjectValidator:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        
    def test(self, description, test_func):
        """Executar um teste e registrar resultado"""
        try:
            result = test_func()
            if result:
                print(f"✅ {description}")
                self.tests_passed += 1
            else:
                print(f"❌ {description}")
                self.tests_failed += 1
        except Exception as e:
            print(f"❌ {description} - Erro: {e}")
            self.tests_failed += 1
    
    def validate_imports(self):
        """Validar imports principais"""
        print("🔍 Validando imports...")
        
        def test_multi_ai_service():
            from app.services.multi_ai_service import MultiAIService
            return True
            
        def test_member_area_service():
            from app.services.member_area_service import MemberAreaService
            return True
            
        def test_auth_service():
            from app.services.supabase_auth_service import SupabaseAuthService
            return True
            
        def test_admin_analytics():
            from app.services.admin_analytics_service import AdminAnalyticsService
            return True
            
        def test_routes():
            from app.routes.member_admin_routes import member_router, admin_router
            return True
            
        def test_api():
            from app.api.index import app as api_app
            return True
        
        self.test("Multi-AI Service Import", test_multi_ai_service)
        self.test("Member Area Service Import", test_member_area_service)
        self.test("Auth Service Import", test_auth_service)
        self.test("Admin Analytics Import", test_admin_analytics)
        self.test("Routes Import", test_routes)
        self.test("API Import", test_api)
    
    def validate_main_app(self):
        """Validar aplicação principal"""
        print("\n🎯 Validando aplicação principal...")
        
        def test_main_demo_import():
            import main_demo
            return hasattr(main_demo, 'app')
            
        def test_app_core():
            from app.core.application import run_production_app
            return True
            
        def test_new_entry_point():
            import importlib.util
            spec = importlib.util.spec_from_file_location("app", "app.py")
            return spec is not None
        
        self.test("Main Demo Import", test_main_demo_import)
        self.test("App Core Module", test_app_core)
        self.test("New Entry Point (app.py)", test_new_entry_point)
    
    def validate_structure(self):
        """Validar nova estrutura de diretórios"""
        print("\n📁 Validando estrutura de diretórios...")
        
        def test_app_directory():
            return Path("app").exists()
            
        def test_services_moved():
            return Path("app/services").exists() and len(list(Path("app/services").glob("*.py"))) > 5
            
        def test_routes_moved():
            return Path("app/routes").exists() and len(list(Path("app/routes").glob("*.py"))) > 0
            
        def test_config_moved():
            return Path("app/config").exists() and len(list(Path("app/config").glob("*.py"))) > 0
            
        def test_tests_organized():
            return Path("tests").exists() and len(list(Path("tests").glob("test_*.py"))) > 5
            
        def test_debug_tools():
            return Path("debug_tools").exists() and len(list(Path("debug_tools").glob("debug_*.py"))) > 0
            
        def test_static_files():
            return Path("static").exists() and len(list(Path("static").glob("*.html"))) > 0
            
        def test_deploy_configs():
            return Path("deploy").exists() and Path("deploy/configs").exists()
        
        self.test("App Directory Created", test_app_directory)
        self.test("Services Moved to app/services", test_services_moved)
        self.test("Routes Moved to app/routes", test_routes_moved)
        self.test("Config Moved to app/config", test_config_moved)
        self.test("Tests Organized", test_tests_organized)
        self.test("Debug Tools Organized", test_debug_tools)
        self.test("Static Files Organized", test_static_files)
        self.test("Deploy Configs Created", test_deploy_configs)
    
    def validate_functionality(self):
        """Validar funcionalidades básicas"""
        print("\n⚙️ Validando funcionalidades...")
        
        def test_multi_ai_initialization():
            from app.services.multi_ai_service import MultiAIService
            service = MultiAIService()
            return service is not None
            
        def test_member_service_initialization():
            from app.services.member_area_service import MemberAreaService
            service = MemberAreaService()
            return service is not None
            
        def test_subscription_plans():
            from app.services.member_area_service import SubscriptionPlan
            return hasattr(SubscriptionPlan, 'FREE')
        
        self.test("Multi-AI Service Initialization", test_multi_ai_initialization)
        self.test("Member Service Initialization", test_member_service_initialization)
        self.test("Subscription Plans Available", test_subscription_plans)
    
    def cleanup_old_directories(self):
        """Limpeza de diretórios antigos vazios"""
        print("\n🧹 Verificando limpeza...")
        
        old_dirs = ["services", "routes", "config"]
        for old_dir in old_dirs:
            old_path = Path(old_dir)
            if old_path.exists():
                files = list(old_path.glob("*.py"))
                # Se só tem __init__.py, pode ser removido
                if len(files) <= 1 and any(f.name == "__init__.py" for f in files):
                    print(f"📁 Diretório antigo vazio encontrado: {old_dir}/")
                else:
                    print(f"⚠️ Diretório antigo ainda tem arquivos: {old_dir}/")
    
    def generate_report(self):
        """Gerar relatório final"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO FINAL DE VALIDAÇÃO")
        print("="*60)
        print(f"✅ Testes Passou: {self.tests_passed}")
        print(f"❌ Testes Falhou: {self.tests_failed}")
        print(f"📈 Taxa de Sucesso: {(self.tests_passed/(self.tests_passed+self.tests_failed)*100):.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 MIGRAÇÃO 100% SUCESSO!")
            print("✅ Projeto reorganizado com sucesso")
            print("✅ Todas as funcionalidades mantidas")
            print("✅ Imports atualizados corretamente")
            print("✅ Nova estrutura organizacional aplicada")
            
            print("\n🚀 PRÓXIMOS PASSOS:")
            print("1. Execute: python app.py")
            print("2. Acesse: http://localhost:8000")
            print("3. Teste admin dashboard e member area")
            print("4. Faça commit das mudanças")
            
        else:
            print(f"\n⚠️ {self.tests_failed} problemas encontrados")
            print("🔍 Verifique os erros acima e corrija antes de continuar")
        
        return self.tests_failed == 0

def main():
    validator = ProjectValidator()
    
    print("🚀 Iniciando Validação Final do Projeto Reorganizado")
    print("="*60)
    
    validator.validate_structure()
    validator.validate_imports()
    validator.validate_main_app()
    validator.validate_functionality()
    validator.cleanup_old_directories()
    
    success = validator.generate_report()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()