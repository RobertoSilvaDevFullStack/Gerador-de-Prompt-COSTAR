import os
import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="COSTAR Generator", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class COSTARRequest(BaseModel):
    context: str
    objective: str
    style: str
    tone: str
    audience: str
    response: str

# Sistema de usuários simples
users_db = {
    "admin@costar.com": {
        "id": 1,
        "name": "Admin",
        "email": "admin@costar.com",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin"
    }
}

active_tokens = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_urlsafe(32)

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    if request.email not in users_db:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    
    user = users_db[request.email]
    password_hash = hash_password(request.password)
    
    if user["password"] != password_hash:
        raise HTTPException(status_code=401, detail="Senha incorreta")
    
    token = generate_token()
    active_tokens[token] = {
        "user_id": user["id"],
        "email": user["email"],
        "expires": datetime.now() + timedelta(hours=24)
    }
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    if request.email in users_db:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    new_id = max([u["id"] for u in users_db.values()]) + 1
    
    users_db[request.email] = {
        "id": new_id,
        "name": request.name,
        "email": request.email,
        "password": hash_password(request.password),
        "role": "user"
    }
    
    return {"message": "Usuário criado com sucesso"}

@app.post("/api/generate")
async def generate_prompt(request: COSTARRequest):
    try:
        # Template básico COSTAR
        prompt = f"""
**CONTEXTO:** {request.context}

**OBJETIVO:** {request.objective}

**ESTILO:** {request.style}

**TOM:** {request.tone}

**AUDIÊNCIA:** {request.audience}

**RESPOSTA:** {request.response}

---

**PROMPT ESTRUTURADO:**
Considerando o contexto de {request.context}, preciso que você {request.objective}. 
O estilo deve ser {request.style} com tom {request.tone}, direcionado para {request.audience}.
A resposta deve ser no formato: {request.response}.
"""
        
        # Tentar usar Gemini AI se disponível
        try:
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-pro')
                
                ai_prompt = f"""Crie um prompt profissional e otimizado usando a metodologia COSTAR:
                
Context: {request.context}
Objective: {request.objective}
Style: {request.style}
Tone: {request.tone}
Audience: {request.audience}
Response: {request.response}
                
Retorne um prompt claro, estruturado e eficaz."""
                
                response = model.generate_content(ai_prompt)
                prompt = response.text
                
        except Exception as e:
            print(f"IA não disponível: {e}")
        
        return {"prompt": prompt}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar prompt: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "costar-generator",
        "platform": "vercel",
        "version": "3.0.0",
        "auth": "enabled",
        "ai": "gemini" if os.getenv('GEMINI_API_KEY') else "template"
    }

@app.get("/", response_class=HTMLResponse)
async def home():
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COSTAR Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .min-vh-100 { min-height: 100vh; }
    </style>
</head>
<body>
    <!-- Login Modal -->
    <div class="modal fade" id="loginModal" tabindex="-1" aria-hidden="true" data-bs-backdrop="static">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title"><i class="bi bi-shield-check"></i> Entrar</h5>
                </div>
                <div class="modal-body">
                    <form id="loginForm">
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" id="loginEmail" value="admin@costar.com" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Senha</label>
                            <input type="password" class="form-control" id="loginPassword" value="admin123" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="bi bi-box-arrow-in-right"></i> Entrar
                        </button>
                    </form>
                    <div class="text-center mt-3">
                        <small class="text-muted">
                            <strong>Demo:</strong> admin@costar.com / admin123<br>
                            Ou <a href="#" onclick="showRegister()">Registre-se</a>
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Register Modal -->
    <div class="modal fade" id="registerModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-success text-white">
                    <h5 class="modal-title"><i class="bi bi-person-plus"></i> Registrar</h5>
                    <button type="button" class="btn-close btn-close-white" onclick="showLogin()"></button>
                </div>
                <div class="modal-body">
                    <form id="registerForm">
                        <div class="mb-3">
                            <label class="form-label">Nome</label>
                            <input type="text" class="form-control" id="registerName" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" id="registerEmail" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Senha</label>
                            <input type="password" class="form-control" id="registerPassword" required>
                        </div>
                        <button type="submit" class="btn btn-success w-100">
                            <i class="bi bi-person-check"></i> Registrar
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Header -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#"><i class="bi bi-magic"></i> COSTAR AI</a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3" id="userInfo" style="display: none;">
                    Bem-vindo, <span id="userName"></span>!
                </span>
                <button class="btn btn-outline-light btn-sm" id="logoutBtn" style="display: none;" onclick="logout()">
                    <i class="bi bi-box-arrow-right"></i> Sair
                </button>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div id="mainContent" style="display: none;">
        <div class="container-fluid">
            <div class="row min-vh-100">
                <div class="col-12">
                    <div class="row justify-content-center align-items-center min-vh-100">
                        <div class="col-lg-8 col-xl-6">
                            <div class="card shadow-lg border-0">
                                <div class="card-header bg-primary text-white text-center py-4">
                                    <h1 class="mb-0"><i class="bi bi-magic"></i> COSTAR Generator</h1>
                                    <p class="mb-0">Gerador de Prompts Profissionais com IA</p>
                                </div>
                                <div class="card-body p-5">
                                    <form id="costarForm">
                                        <div class="row g-3">
                                            <div class="col-md-6">
                                                <label class="form-label"><strong>C</strong>ontext</label>
                                                <textarea class="form-control" id="context" rows="3" placeholder="Descreva o contexto..."></textarea>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label"><strong>O</strong>bjective</label>
                                                <textarea class="form-control" id="objective" rows="3" placeholder="Qual o objetivo?"></textarea>
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label"><strong>S</strong>tyle</label>
                                                <input type="text" class="form-control" id="style" placeholder="Ex: formal, casual...">
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label"><strong>T</strong>one</label>
                                                <input type="text" class="form-control" id="tone" placeholder="Ex: profissional, amigável...">
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label"><strong>A</strong>udience</label>
                                                <input type="text" class="form-control" id="audience" placeholder="Para quem é?">
                                            </div>
                                            <div class="col-md-6">
                                                <label class="form-label"><strong>R</strong>esponse</label>
                                                <input type="text" class="form-control" id="response" placeholder="Formato da resposta">
                                            </div>
                                        </div>
                                        <div class="mt-4">
                                            <button type="submit" class="btn btn-primary btn-lg">
                                                <i class="bi bi-magic"></i> Gerar Prompt com IA
                                            </button>
                                        </div>
                                    </form>
                                    
                                    <div id="result" class="mt-4" style="display: none;">
                                        <h5>Prompt Gerado:</h5>
                                        <div class="card bg-light">
                                            <div class="card-body">
                                                <pre id="generatedPrompt" style="white-space: pre-wrap;"></pre>
                                                <button class="btn btn-outline-primary" onclick="copyToClipboard()">
                                                    <i class="bi bi-clipboard"></i> Copiar
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentUser = null;
        
        document.addEventListener('DOMContentLoaded', function() {
            checkAuthStatus();
        });
        
        function checkAuthStatus() {
            const token = localStorage.getItem('costar_token');
            const userData = localStorage.getItem('costar_user');
            
            if (token && userData) {
                currentUser = JSON.parse(userData);
                showMainContent();
            } else {
                showLoginModal();
            }
        }
        
        function showLoginModal() {
            const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
            loginModal.show();
        }
        
        function showRegister() {
            const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
            
            if (loginModal) loginModal.hide();
            registerModal.show();
        }
        
        function showLogin() {
            const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
            
            if (registerModal) registerModal.hide();
            loginModal.show();
        }
        
        function showMainContent() {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) modalInstance.hide();
            });
            
            document.getElementById('mainContent').style.display = 'block';
            document.getElementById('userInfo').style.display = 'inline';
            document.getElementById('logoutBtn').style.display = 'inline-block';
            document.getElementById('userName').textContent = currentUser.name;
        }
        
        function logout() {
            localStorage.removeItem('costar_token');
            localStorage.removeItem('costar_user');
            currentUser = null;
            
            document.getElementById('mainContent').style.display = 'none';
            document.getElementById('userInfo').style.display = 'none';
            document.getElementById('logoutBtn').style.display = 'none';
            
            showLoginModal();
        }
        
        // Login Form
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email, password})
                });
                
                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('costar_token', data.token);
                    localStorage.setItem('costar_user', JSON.stringify(data.user));
                    currentUser = data.user;
                    showMainContent();
                } else {
                    const error = await response.json();
                    alert('Erro: ' + error.detail);
                }
            } catch (error) {
                alert('Erro ao fazer login: ' + error.message);
            }
        });
        
        // Register Form
        document.getElementById('registerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const name = document.getElementById('registerName').value;
            const email = document.getElementById('registerEmail').value;
            const password = document.getElementById('registerPassword').value;
            
            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, email, password})
                });
                
                if (response.ok) {
                    alert('Usuário registrado com sucesso!');
                    showLogin();
                } else {
                    const error = await response.json();
                    alert('Erro: ' + error.detail);
                }
            } catch (error) {
                alert('Erro ao registrar: ' + error.message);
            }
        });
        
        // COSTAR Form
        document.getElementById('costarForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = e.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Gerando...';
            submitBtn.disabled = true;
            
            const formData = {
                context: document.getElementById('context').value,
                objective: document.getElementById('objective').value,
                style: document.getElementById('style').value,
                tone: document.getElementById('tone').value,
                audience: document.getElementById('audience').value,
                response: document.getElementById('response').value
            };
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('costar_token')
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('generatedPrompt').textContent = data.prompt;
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
                } else {
                    alert('Erro ao gerar prompt: ' + data.detail);
                }
            } catch (error) {
                alert('Erro ao gerar prompt: ' + error.message);
            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
        
        function copyToClipboard() {
            const text = document.getElementById('generatedPrompt').textContent;
            navigator.clipboard.writeText(text).then(() => {
                const btn = event.target;
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="bi bi-check"></i> Copiado!';
                btn.classList.remove('btn-outline-primary');
                btn.classList.add('btn-success');
                
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-outline-primary');
                }, 2000);
            });
        }
    </script>
</body>
</html>"""

# Handler para Vercel
handler = app