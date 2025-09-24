import os
import json
import zipfile
from datetime import datetime
import asyncio
from typing import Dict, Any

class BackupService:
    def __init__(self, supabase_service):
        self.supabase_service = supabase_service
        self.backup_dir = os.getenv("BACKUP_DIR", "./backups")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    async def create_user_backup(self, user_id: str) -> str:
        """Criar backup completo dos dados do usuário"""
        try:
            # Buscar todos os dados do usuário
            prompts = await self.supabase_service.get_all_user_prompts(user_id)
            
            # Criar estrutura de backup
            backup_data = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "data": {
                    "prompts": prompts,
                    "metadata": {
                        "total_prompts": len(prompts),
                        "categories": list(set(p.get("categoria", "geral") for p in prompts))
                    }
                }
            }
            
            # Criar arquivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{user_id}_{timestamp}.json"
            filepath = os.path.join(self.backup_dir, filename)
            
            # Salvar dados em arquivo JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
            
            # Criar arquivo ZIP
            zip_filename = f"backup_{user_id}_{timestamp}.zip"
            zip_filepath = os.path.join(self.backup_dir, zip_filename)
            
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(filepath, filename)
            
            # Remover arquivo JSON temporário
            os.remove(filepath)
            
            return zip_filepath
            
        except Exception as e:
            raise Exception(f"Erro ao criar backup: {str(e)}")
    
    async def restore_user_backup(self, user_id: str, backup_file: str):
        """Restaurar backup do usuário"""
        try:
            # Extrair e ler arquivo de backup
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # Assumir que há apenas um arquivo JSON no ZIP
                json_filename = zipf.namelist()[0]
                with zipf.open(json_filename) as f:
                    backup_data = json.load(f)
            
            # Validar dados do backup
            if backup_data.get("user_id") != user_id:
                raise Exception("Backup não pertence ao usuário atual")
            
            # Restaurar prompts
            prompts = backup_data.get("data", {}).get("prompts", [])
            restored_count = 0
            
            for prompt_data in prompts:
                try:
                    # Remover campos que serão recriados
                    prompt_data.pop("id", None)
                    prompt_data.pop("criado_em", None)
                    prompt_data.pop("atualizado_em", None)
                    
                    # Criar prompt
                    await self.supabase_service.create_prompt(
                        user_id=user_id,
                        titulo=prompt_data.get("titulo", "Prompt Restaurado"),
                        prompt_data={
                            "contexto": prompt_data.get("contexto", ""),
                            "objetivo": prompt_data.get("objetivo", ""),
                            "estilo": prompt_data.get("estilo", ""),
                            "tom": prompt_data.get("tom", ""),
                            "audiencia": prompt_data.get("audiencia", ""),
                            "resposta": prompt_data.get("resposta", "")
                        },
                        prompt_completo=prompt_data.get("prompt_completo", ""),
                        categoria=prompt_data.get("categoria", "geral"),
                        tags=prompt_data.get("tags", []),
                        favorito=prompt_data.get("favorito", False),
                        compartilhado=prompt_data.get("compartilhado", False)
                    )
                    restored_count += 1
                    
                except Exception as e:
                    print(f"Erro ao restaurar prompt: {e}")
                    continue
            
            return {
                "message": "Backup restaurado com sucesso",
                "prompts_restored": restored_count,
                "total_prompts": len(prompts)
            }
            
        except Exception as e:
            raise Exception(f"Erro ao restaurar backup: {str(e)}")