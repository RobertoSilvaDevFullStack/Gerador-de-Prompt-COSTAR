#!/usr/bin/env python3
"""
Script para corrigir todas as referências de 'frontend' para 'static'
"""

import re
from pathlib import Path

def fix_frontend_references(file_path):
    """Corrigir referências de frontend para static"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir referências de frontend/ para static/
        patterns = [
            (r'"frontend/', r'"static/'),
            (r"'frontend/", r"'static/"),
            (r'frontend/', 'static/'),
        ]
        
        changes_made = 0
        for old_pattern, new_pattern in patterns:
            if isinstance(old_pattern, str):
                old_content = content
                content = content.replace(old_pattern, new_pattern)
                if content != old_content:
                    changes_made += len(re.findall(re.escape(old_pattern), old_content))
            else:
                old_content = content
                content = re.sub(old_pattern, new_pattern, content)
                if content != old_content:
                    changes_made += len(re.findall(old_pattern, old_content))
        
        if changes_made > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {file_path}: {changes_made} referência(s) corrigida(s)")
        else:
            print(f"ℹ️ {file_path}: Nenhuma referência frontend encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")

def main():
    print("🔧 Corrigindo referências de 'frontend' para 'static'...")
    
    files_to_fix = [
        "tools/main_demo.py",
        "static/index.html",
        "static/member-area.html", 
        "static/admin-dashboard.html",
        "static/debug-login-main.html",
        "static/debug-member-area.html",
    ]
    
    for file_path in files_to_fix:
        if Path(file_path).exists():
            fix_frontend_references(file_path)
        else:
            print(f"⚠️ Arquivo não encontrado: {file_path}")
    
    print("✅ Correção de referências concluída!")

if __name__ == "__main__":
    main()