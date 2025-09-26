#!/usr/bin/env python3
"""
Script simples para exibir SQL limpo do schema Supabase
"""
import os

def main():
    # Caminho para o arquivo SQL limpo
    sql_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'deploy_clean.sql')
    
    print("🚀 SCHEMA SUPABASE - COPIE E COLE NO SQL EDITOR")
    print("="*60)
    print()
    print("📋 INSTRUÇÕES:")
    print("1. Acesse: https://supabase.com/dashboard")
    print("2. Vá no seu projeto")
    print("3. Clique em 'SQL Editor' na barra lateral")
    print("4. Clique em 'New Query'")
    print("5. COPIE TODO O CÓDIGO ABAIXO")
    print("6. COLE no editor e clique 'Run'")
    print()
    print("="*60)
    print("👇 COPIE DAQUI PARA BAIXO 👇")
    print("="*60)
    print()
    
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print(sql_content)
        
        print()
        print("="*60)
        print("👆 COPIE ATÉ AQUI 👆")
        print("="*60)
        print()
        print("✅ Após executar no Supabase, todas as tabelas serão criadas!")
        print("🎉 Depois execute: python scripts/test_supabase_setup.py")
        
    except Exception as e:
        print(f"❌ Erro ao carregar SQL: {e}")

if __name__ == "__main__":
    main()