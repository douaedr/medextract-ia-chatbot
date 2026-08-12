# ==========================================================================
#  MedExtract AI - Build pour connexion LENTE
#  Construit un service a la fois (toute la bande passante pour chacun)
#  et reessaie automatiquement en cas de coupure reseau.
#  Lancer depuis le dossier dev1 :   .\build_lent.ps1
# ==========================================================================

$ErrorActionPreference = "Continue"

function Invoke-WithRetry {
    param(
        [string]$Titre,
        [scriptblock]$Action,
        [int]$MaxEssais = 6
    )
    for ($i = 1; $i -le $MaxEssais; $i++) {
        Write-Host ""
        Write-Host ">>> $Titre  (essai $i/$MaxEssais)" -ForegroundColor Cyan
        & $Action
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    OK : $Titre" -ForegroundColor Green
            return $true
        }
        Write-Host "    Echec (reseau ?). Nouvelle tentative dans 5 s..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
    Write-Host "    ABANDON apres $MaxEssais essais : $Titre" -ForegroundColor Red
    return $false
}

Write-Host "=== 1/3  Telechargement des images de base (une par une) ===" -ForegroundColor Magenta
$bases = @("postgres:16", "python:3.11-slim", "node:20-alpine", "nginx:1.27-alpine")
foreach ($img in $bases) {
    Invoke-WithRetry "docker pull $img" { docker pull $img } | Out-Null
}

Write-Host ""
Write-Host "=== 2/3  Construction des services (du plus leger au plus lourd) ===" -ForegroundColor Magenta
# Ordre : les legers d'abord (victoires rapides), l'OCR (paddle) en dernier.
$services = @(
    "auth-service",
    "reporting-service",
    "chatbot-service",
    "document-service",
    "ai-service",
    "frontend",
    "ocr-service"     # le plus lourd (PaddleOCR)
)
foreach ($svc in $services) {
    $ok = Invoke-WithRetry "build $svc" { docker compose build $svc }
    if (-not $ok) {
        Write-Host ""
        Write-Host "!!! $svc n'a pas pu etre construit (connexion trop instable)." -ForegroundColor Red
        Write-Host "    Tu peux relancer ce script : il reprendra sans refaire ce qui est deja fait." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== 3/3  Demarrage de tous les services ===" -ForegroundColor Magenta
docker compose up -d

Write-Host ""
Write-Host "Etat des conteneurs :" -ForegroundColor Cyan
docker compose ps
Write-Host ""
Write-Host "Termine. Interface : http://localhost:3000   |   API : http://localhost:8080" -ForegroundColor Green
