# Activation script for PowerShell (run with: . .\activate.ps1)
Write-Host "Activating virtual environment..." -ForegroundColor Green
Set-Location backend
& .\venv\Scripts\Activate.ps1
Write-Host ""
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  flask run              - Run development server"
Write-Host "  flask db upgrade       - Apply database migrations"
Write-Host "  pytest                 - Run tests"
Write-Host "  python app.py          - Run app directly"
Write-Host ""
