import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import os
import asyncio
import aiohttp

class NotificationService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: str = None
    ):
        """Enviar email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Adicionar versão texto
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Adicionar versão HTML
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Enviar email em thread separada
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_smtp, msg)
            
        except Exception as e:
            raise Exception(f"Erro ao enviar email: {str(e)}")
    
    def _send_smtp(self, msg):
        """Enviar email via SMTP (método síncrono)"""
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
    
    async def send_welcome_email(self, user_email: str, user_name: str):
        """Enviar email de boas-vindas"""
        subject = "Bem-vindo ao COSTAR Prompt Generator!"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #667eea;">Olá {user_name}! 👋</h2>
                
                <p>Seja muito bem-vindo ao <strong>COSTAR Prompt Generator</strong>!</p>
                
                <p>Agora você tem acesso a uma ferramenta poderosa para criar prompts estruturados e profissionais seguindo a metodologia COSTAR:</p>
                
                <ul style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <li><strong>Context</strong> - Defina o contexto</li>
                    <li><strong>Objective</strong> - Estabeleça objetivos claros</li>
                    <li><strong>Style</strong> - Especifique o estilo</li>
                    <li><strong>Tone</strong> - Determine o tom</li>
                    <li><strong>Audience</strong> - Identifique a audiência</li>
                    <li><strong>Response</strong> - Configure a resposta</li>
                </ul>
                
                <h3 style="color: #667eea;">Recursos Disponíveis:</h3>
                <ul>
                    <li>✨ Gerador de prompts COSTAR</li>
                    <li>📚 Templates prontos</li>
                    <li>💾 Sistema de salvamento</li>
                    <li>🤖 Integração com Gemini AI</li>
                    <li>📊 Analytics e estatísticas</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://seu-dominio.com" 
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 12px 25px; text-decoration: none; 
                              border-radius: 8px; font-weight: bold;">
                        Começar Agora
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    Se tiver dúvidas, entre em contato conosco. Estamos aqui para ajudar!
                </p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="color: #999; font-size: 12px; text-align: center;">
                    COSTAR Prompt Generator - Criando prompts profissionais
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Olá {user_name}!
        
        Seja muito bem-vindo ao COSTAR Prompt Generator!
        
        Agora você tem acesso a uma ferramenta poderosa para criar prompts estruturados seguindo a metodologia COSTAR.
        
        Acesse: https://seu-dominio.com
        
        Se tiver dúvidas, entre em contato conosco.
        
        COSTAR Prompt Generator
        """
        
        await self.send_email(user_email, subject, html_content, text_content)
    
    async def send_export_ready_email(self, user_email: str, download_link: str):
        """Notificar que export está pronto"""
        subject = "Seu export de prompts está pronto!"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #667eea;">Export Concluído ✅</h2>
                
                <p>Seu export de prompts foi processado com sucesso!</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{download_link}" 
                       style="background: #28a745; color: white; padding: 12px 25px; 
                              text-decoration: none; border-radius: 8px;">
                        Baixar Arquivo
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    <strong>Nota:</strong> O link expira em 24 horas por motivos de segurança.
                </p>
            </div>
        </body>
        </html>
        """
        
        await self.send_email(user_email, subject, html_content)