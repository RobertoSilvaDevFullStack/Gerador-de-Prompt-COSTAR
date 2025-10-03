"""
Configuração centralizada de caminhos do projeto
"""
import os
from pathlib import Path

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Diretórios principais
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TOOLS_DIR = PROJECT_ROOT / "tools"
DOCS_DIR = PROJECT_ROOT / "docs"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
SERVICES_DIR = PROJECT_ROOT / "services"
ROUTES_DIR = PROJECT_ROOT / "routes"
CONFIG_DIR = PROJECT_ROOT / "config"
TESTS_DIR = PROJECT_ROOT / "tests"

# Arquivos específicos
MAIN_SERVER = PROJECT_ROOT / "main.py"
DEMO_SERVER = PROJECT_ROOT / "main_demo.py"
README_FILE = PROJECT_ROOT / "README.md"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

# Logs
SERVER_LOG = LOGS_DIR / "server.log"
SERVER_OUTPUT_LOG = LOGS_DIR / "server_output.log"

# Data files
AI_USAGE_STATS = DATA_DIR / "ai_usage_stats.json"
USER_ACTIVITIES = DATA_DIR / "user_activities.json"
SAVED_PROMPTS = DATA_DIR / "saved_prompts.json"
SAVED_TEMPLATES = DATA_DIR / "saved_templates.json"
MEMBER_PROFILES = DATA_DIR / "member_profiles.json"
SYSTEM_METRICS = DATA_DIR / "system_metrics.json"

def ensure_directories_exist():
    """Garantir que todos os diretórios necessários existam"""
    directories = [
        DATA_DIR, LOGS_DIR, SCRIPTS_DIR, TOOLS_DIR, 
        DOCS_DIR, FRONTEND_DIR, SERVICES_DIR, ROUTES_DIR,
        CONFIG_DIR, TESTS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_relative_path(file_path: Path, base_path: Path = PROJECT_ROOT) -> str:
    """Obter caminho relativo a partir de um base path"""
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        return str(file_path)

if __name__ == "__main__":
    # Teste dos caminhos
    ensure_directories_exist()
    print("✅ Estrutura de diretórios verificada")
    print(f"📁 Projeto: {PROJECT_ROOT}")
    print(f"📊 Data: {DATA_DIR}")
    print(f"📝 Logs: {LOGS_DIR}")
    print(f"🔧 Scripts: {SCRIPTS_DIR}")
    print(f"🛠️ Tools: {TOOLS_DIR}")