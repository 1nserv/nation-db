. .\.venv\Scripts\Activate.ps1

if (-not (Test-Path ".local" -PathType Container)) {
    Write-Host "Création du dossier .local ..."
    New-Item -ItemType Directory -Path ".local" | Out-Null
}

if (-not (Test-Path ".env" -PathType Leaf)) {
    Write-Host "Création du .env ..."
    New-Item -ItemType File -Path ".env" | Out-Null
}

Clear-Host

py -m scripts.reset

py -m scripts.reset.init_admins
py -m scripts.reset.init_bots
py -m scripts.reset.init_departments
py -m scripts.reset.init_institutions
py -m scripts.reset.init_positions

py -m scripts.reset.economy.init_accounts
py -m scripts.reset.economy.init_inventories
py -m scripts.reset.economy.init_items

Clear-Host