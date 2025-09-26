#!/usr/bin/env python3
"""
Script para exibir SQL de RESET COMPLETO + DEPLOY
"""
import os

def main():
    # Caminho para o arquivo SQL de reset
    sql_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'reset_and_deploy.sql')
    
    print("🔄 RESET COMPLETO + DEPLOY SUPABASE")
    print("="*60)
    print()
    print("⚠️  ATENÇÃO: Este SQL vai DELETAR tudo e recriar!")
    print("📋 Use isso para corrigir o erro de 'tabela já existe'")
    print()
    print("📋 INSTRUÇÕES:")
    print("1. Vá para o Supabase SQL Editor")
    print("2. Crie uma nova query")
    print("3. COPIE TODO O SQL ABAIXO")
    print("4. Execute no Supabase")
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
        print("✅ Este SQL vai limpar tudo e recriar corretamente!")
        print("🎉 Depois execute: python scripts/test_supabase_setup.py")
        
    except Exception as e:
        print(f"❌ Erro ao carregar SQL: {e}")

if __name__ == "__main__":
    main()