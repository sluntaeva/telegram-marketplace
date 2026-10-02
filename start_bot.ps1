$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pgRoot = Join-Path $env:USERPROFILE "Downloads\postgresql-18.6-5-windows-x64-binaries"
$dataDir = Join-Path $env:USERPROFILE "Documents\PostgreSQL\data"
$logFile = Join-Path $env:USERPROFILE "Documents\PostgreSQL\start.log"

$pgCtl = Get-ChildItem -LiteralPath $pgRoot -Recurse -Filter "pg_ctl.exe" |
    Select-Object -First 1 -ExpandProperty FullName

if (-not $pgCtl) {
    throw "Не найден pg_ctl.exe в $pgRoot"
}

& $pgCtl -D $dataDir status *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Запускаю PostgreSQL..."
    & $pgCtl -D $dataDir -l $logFile start
    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL не запустился. Проверьте журнал: $logFile"
    }
}

Write-Host "PostgreSQL работает. Запускаю Telegram-бота..."
Set-Location -LiteralPath $projectDir
python app.py
