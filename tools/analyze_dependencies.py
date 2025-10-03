#!/usr/bin/env python3
"""
Script para mapear dependências e imports antes da refatoração
Garante que nenhuma dependência será quebrada durante a reorganização
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set

class DependencyMapper:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.imports_map = {}
        self.file_dependencies = {}
        self.python_files = []
        
    def scan_project(self):
        """Escanear todos os arquivos Python do projeto"""
        print("🔍 Escaneando projeto...")
        
        # Encontrar todos os arquivos Python
        for root, dirs, files in os.walk(self.project_root):
            # Ignorar __pycache__ e .git
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.project_root)
                    self.python_files.append(str(relative_path))
        
        print(f"📁 Encontrados {len(self.python_files)} arquivos Python")
        
    def analyze_imports(self):
        """Analisar imports em todos os arquivos Python"""
        print("📋 Analisando imports...")
        
        import_patterns = [
            r'^from\s+(\S+)\s+import\s+(.+)$',  # from module import something
            r'^import\s+(\S+)$',                 # import module
            r'^from\s+\.\s+import\s+(.+)$',     # from . import something
            r'^from\s+\.(\S+)\s+import\s+(.+)$' # from .module import something
        ]
        
        for file_path in self.python_files:
            full_path = self.project_root / file_path
            self.file_dependencies[file_path] = {
                'imports': [],
                'local_imports': [],
                'relative_imports': [],
                'size': full_path.stat().st_size if full_path.exists() else 0
            }
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for line_num, line in enumerate(content.split('\n'), 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    for pattern in import_patterns:
                        match = re.match(pattern, line)
                        if match:
                            if 'from .' in line:
                                self.file_dependencies[file_path]['relative_imports'].append({
                                    'line': line_num,
                                    'import': line,
                                    'module': match.group(1) if len(match.groups()) > 1 else match.group(1)
                                })
                            elif any(local_mod in line for local_mod in ['services', 'routes', 'config', 'debug']):
                                self.file_dependencies[file_path]['local_imports'].append({
                                    'line': line_num,
                                    'import': line,
                                    'module': match.group(1)
                                })
                            else:
                                self.file_dependencies[file_path]['imports'].append({
                                    'line': line_num,
                                    'import': line,
                                    'module': match.group(1)
                                })
                            break
                            
            except Exception as e:
                print(f"⚠️ Erro ao analisar {file_path}: {e}")
    
    def find_cross_references(self):
        """Encontrar referências cruzadas entre arquivos"""
        print("🔗 Mapeando referências cruzadas...")
        
        cross_refs = {}
        
        for file_path, deps in self.file_dependencies.items():
            cross_refs[file_path] = []
            
            # Verificar se outros arquivos importam este
            file_name = Path(file_path).stem
            module_name = str(Path(file_path).with_suffix('')).replace('/', '.').replace('\\', '.')
            
            for other_file, other_deps in self.file_dependencies.items():
                if other_file == file_path:
                    continue
                    
                # Verificar imports locais
                for imp in other_deps['local_imports']:
                    if file_name in imp['import'] or module_name in imp['import']:
                        cross_refs[file_path].append({
                            'referenced_by': other_file,
                            'line': imp['line'],
                            'import_statement': imp['import']
                        })
        
        return cross_refs
    
    def analyze_main_files(self):
        """Analisar arquivos principais de entrada"""
        main_files = [f for f in self.python_files if 'main' in f.lower()]
        
        analysis = {}
        for main_file in main_files:
            full_path = self.project_root / main_file
            analysis[main_file] = {
                'size': full_path.stat().st_size if full_path.exists() else 0,
                'dependencies': len(self.file_dependencies.get(main_file, {}).get('local_imports', [])),
                'is_entry_point': False
            }
            
            # Verificar se tem if __name__ == "__main__"
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '__name__' in content and '__main__' in content:
                        analysis[main_file]['is_entry_point'] = True
            except:
                pass
                
        return analysis
    
    def generate_report(self):
        """Gerar relatório completo"""
        print("📊 Gerando relatório...")
        
        cross_refs = self.find_cross_references()
        main_analysis = self.analyze_main_files()
        
        report = {
            'summary': {
                'total_python_files': len(self.python_files),
                'files_with_local_imports': len([f for f in self.file_dependencies if self.file_dependencies[f]['local_imports']]),
                'files_with_relative_imports': len([f for f in self.file_dependencies if self.file_dependencies[f]['relative_imports']]),
                'main_files_found': len(main_analysis)
            },
            'main_files': main_analysis,
            'files_by_directory': self._group_by_directory(),
            'high_risk_files': self._identify_high_risk_files(cross_refs),
            'move_plan': self._generate_move_plan(),
            'dependencies': self.file_dependencies,
            'cross_references': cross_refs
        }
        
        return report
    
    def _group_by_directory(self):
        """Agrupar arquivos por diretório"""
        by_dir = {}
        for file_path in self.python_files:
            directory = str(Path(file_path).parent)
            if directory not in by_dir:
                by_dir[directory] = []
            by_dir[directory].append(file_path)
        return by_dir
    
    def _identify_high_risk_files(self, cross_refs):
        """Identificar arquivos de alto risco para mover"""
        high_risk = []
        
        for file_path, refs in cross_refs.items():
            risk_score = len(refs)
            deps = self.file_dependencies.get(file_path, {})
            risk_score += len(deps.get('local_imports', []))
            risk_score += len(deps.get('relative_imports', [])) * 2  # Relative imports são mais arriscados
            
            if risk_score > 3:
                high_risk.append({
                    'file': file_path,
                    'risk_score': risk_score,
                    'references': len(refs),
                    'local_imports': len(deps.get('local_imports', [])),
                    'relative_imports': len(deps.get('relative_imports', []))
                })
        
        return sorted(high_risk, key=lambda x: x['risk_score'], reverse=True)
    
    def _generate_move_plan(self):
        """Gerar plano de movimentação segura"""
        return {
            'phase_1_safe_moves': [
                'test_*.py -> tests/',
                'debug_*.py -> debug/',
                '*.md -> docs/ (exceto README.md)'
            ],
            'phase_2_medium_risk': [
                'services/ -> app/services/',
                'routes/ -> app/routes/',
                'config/ -> app/config/'
            ],
            'phase_3_high_risk': [
                'main_*.py -> reorganizar',
                'api/ -> app/api/',
                'frontend/ -> static/'
            ]
        }

def main():
    project_root = os.getcwd()
    mapper = DependencyMapper(project_root)
    
    print("🚀 Iniciando análise de dependências...")
    mapper.scan_project()
    mapper.analyze_imports()
    
    report = mapper.generate_report()
    
    # Salvar relatório
    with open('dependency_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("📄 Relatório salvo em: dependency_analysis.json")
    
    # Exibir resumo
    print("\n" + "="*50)
    print("📋 RESUMO DA ANÁLISE")
    print("="*50)
    print(f"📁 Total de arquivos Python: {report['summary']['total_python_files']}")
    print(f"🔗 Arquivos com imports locais: {report['summary']['files_with_local_imports']}")
    print(f"📍 Arquivos com imports relativos: {report['summary']['files_with_relative_imports']}")
    print(f"🎯 Arquivos main encontrados: {report['summary']['main_files_found']}")
    
    print("\n🚨 ARQUIVOS DE ALTO RISCO:")
    for risk_file in report['high_risk_files'][:5]:
        print(f"   - {risk_file['file']} (risco: {risk_file['risk_score']})")
    
    print("\n✅ Análise completa! Verifique dependency_analysis.json para detalhes.")

if __name__ == "__main__":
    main()