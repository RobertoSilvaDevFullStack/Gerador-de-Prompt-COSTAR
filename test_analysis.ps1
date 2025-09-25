# Teste do endpoint de análise usando PowerShell
$uri = "http://localhost:8001/api/prompts/analyze"
$body = @{
    contexto = "Análise de dados empresariais"
    objetivo = "Criar relatório com insights e recomendações"
    estilo = "Formal e técnico"
    tom = "Profissional"
    audiencia = "Executivos"
    resposta = "Relatório estruturado com gráficos"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "🔍 Testando endpoint de análise..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -Headers $headers -TimeoutSec 30
    
    Write-Host "✅ Sucesso!" -ForegroundColor Green
    Write-Host "📝 Modo: $($response.modo)" -ForegroundColor Cyan
    Write-Host "📄 Mensagem: $($response.message)" -ForegroundColor Cyan
    
    if ($response.analise) {
        if ($response.analise.pontuacao) {
            Write-Host "🎯 Pontuação: $($response.analise.pontuacao)" -ForegroundColor Green
        }
        if ($response.analise.qualidade) {
            Write-Host "🏆 Qualidade: $($response.analise.qualidade)" -ForegroundColor Green
        }
        if ($response.analise.resumo) {
            Write-Host "📋 Resumo: $($response.analise.resumo.Substring(0, [Math]::Min(100, $response.analise.resumo.Length)))..." -ForegroundColor White
        }
    }
    
    Write-Host "`n📊 Response completa:" -ForegroundColor Magenta
    $response | ConvertTo-Json -Depth 5
    
} catch {
    Write-Host "❌ Erro: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}