#!/usr/bin/env python3
"""
Script para validar integridade dos caminhos após reorganização
"""

import os
import sys
from pathlib import Path

def check_file_structure():
    """Verificar se a estrutura de arquivos está correta"""
    
    print("🔍 VERIFICANDO ESTRUTURA DE ARQUIVOS")
    print("=" * 40)
    
    # Arquivos que devem existir na raiz
    root_files = [
        "main.py",
        "main_demo.py", 
        "requirements.txt",
        "README.md",
        "vercel.json",
        ".env.example"
    ]
    
    # Arquivos que devem estar em pastas específicas
    organized_files = {
        "data/ai_usage_stats.json": "Estatísticas das IAs",
        "scripts/create_admin_user.py": "Script de criação de admin", 
        ".vscode/pyrightconfig.json": "Configuração Python LSP"
    }
    
    # Verificar arquivos da raiz
    print("\n📁 ARQUIVOS DA RAIZ:")
    project_root = Path("..").resolve()
    
    for file_name in root_files:
        file_path = project_root / file_name
        status = "✅" if file_path.exists() else "❌"
        print(f"   {status} {file_name}")
    
    # Verificar arquivos organizados
    print("\n📂 ARQUIVOS ORGANIZADOS:")
    all_good = True
    
    for file_path, description in organized_files.items():
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path} - {description}")
        else:
            print(f"   ❌ {file_path} - {description} (FALTANDO)")
            all_good = False
    
    # Verificar estrutura de pastas
    print("\n📁 ESTRUTURA DE PASTAS:")
    expected_folders = [
        "frontend", "services", "routes", "scripts", 
        "data", "docs", "docker", ".vscode"
    ]
    
    for folder in expected_folders:
        folder_path = project_root / folder
        status = "✅" if folder_path.exists() and folder_path.is_dir() else "❌"
        print(f"   {status} {folder}/")
    
    # Resumo
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 ESTRUTURA ORGANIZADA COM SUCESSO!")
        print("✅ Todos os arquivos estão nos locais corretos")
        print("✅ Caminhos limpos e organizados")
    else:
        print("⚠️  Alguns arquivos podem estar em locais incorretos")
    
    return all_good

def check_imports():
    """Verificar se os imports dos serviços estão funcionando"""
    
    print("\n🔍 TESTANDO IMPORTS DOS SERVIÇOS")
    print("=" * 40)
    
    # Adicionar o diretório pai ao path para imports
    parent_dir = Path("..").resolve()
    sys.path.insert(0, str(parent_dir))
    
    services_to_test = [
        ("services.auth_service", "AuthService"),
        ("services.member_area_service", "MemberAreaService"), 
        ("services.admin_analytics_service", "AdminAnalyticsService"),
        ("services.gemini_service", "GeminiService"),
        ("services.analytics_service", "AnalyticsService")
    ]
    
    success_count = 0
    
    for module_name, class_name in services_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            service_class = getattr(module, class_name)
            print(f"   ✅ {module_name} -> {class_name}")
            success_count += 1
        except Exception as e:
            print(f"   ❌ {module_name} -> {class_name} (ERRO: {e})")
    
    print(f"\n📊 RESULTADO: {success_count}/{len(services_to_test)} serviços importados com sucesso")
    
    return success_count == len(services_to_test)

if __name__ == "__main__":
    print("🔧 VALIDADOR DE INTEGRIDADE PÓS-REORGANIZAÇÃO")
    print("=" * 50)
    
    # Verificar estrutura
    structure_ok = check_file_structure()
    
    # Verificar imports
    imports_ok = check_imports()
    
    # Resultado final
    print("\n" + "=" * 50)
    if structure_ok and imports_ok:
        print("🎉 REORGANIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ Estrutura: Organizada")
        print("✅ Imports: Funcionando")
        print("✅ Projeto: Pronto para uso")
    else:
        print("⚠️  REORGANIZAÇÃO COM PROBLEMAS:")
        if not structure_ok:
            print("❌ Estrutura: Com problemas")
        if not imports_ok:
            print("❌ Imports: Com problemas")
        print("🔧 Verifique os erros acima")
    
    print("\n💡 Para testar o sistema completo:")
    print("   cd .. && python main.py")