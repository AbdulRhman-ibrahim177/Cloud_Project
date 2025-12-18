# start-stt.ps1
# PowerShell script to start STT service

# Get script directory
$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
Write-Host "📁 Script directory: $ScriptDir" -ForegroundColor Green

# Change to script directory
Set-Location $ScriptDir
Write-Host "📍 Changed to: $(Get-Location)" -ForegroundColor Green

# Start the service
Write-Host "`n🚀 Starting STT Service..." -ForegroundColor Cyan
Write-Host "📍 Listening on: http://127.0.0.1:8003" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://127.0.0.1:8003/docs" -ForegroundColor Cyan
Write-Host "⏹️  Press CTRL+C to stop`n" -ForegroundColor Yellow

python run.py
