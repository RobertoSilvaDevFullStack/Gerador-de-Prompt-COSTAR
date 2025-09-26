#!/usr/bin/env python3
"""
Debug do JWT Token
"""
import jwt
import requests
import json
import base64

def decode_jwt_manually(token):
    """Decodificar JWT manualmente para debug"""
    try:
        # Separar partes do JWT
        parts = token.split('.')
        
        # Decodificar header
        header = json.loads(base64.urlsafe_b64decode(parts[0] + '==='))
        
        # Decodificar payload
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '==='))
        
        print('🔍 JWT HEADER:')
        print(json.dumps(header, indent=2))
        
        print('\n🔍 JWT PAYLOAD:')
        print(json.dumps(payload, indent=2))
        
        return payload
        
    except Exception as e:
        print(f'❌ Erro ao decodificar JWT: {e}')
        return None

def debug_jwt():
    """Debug do JWT após login"""
    print('🔍 DEBUG DO JWT TOKEN')
    print('='*40)

    # Login
    data = {
        'email': 'admin@costar.com',
        'password': 'admin123'
    }

    try:
        response = requests.post('http://localhost:8000/api/members/auth/login', 
                               json=data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        if response.ok:
            result = response.json()
            token = result.get('access_token', '')
            
            print(f'🎫 Token recebido: {token[:50]}...')
            
            # Decodificar JWT
            payload = decode_jwt_manually(token)
            
            if payload:
                print(f'\n📊 ROLE NO JWT: "{payload.get("role")}" (tipo: {type(payload.get("role"))})')
        
        else:
            print(f'❌ Erro no login: {response.text}')
        
    except Exception as e:
        print(f'❌ Erro: {e}')

if __name__ == "__main__":
    debug_jwt()