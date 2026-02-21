# run.ps1 — run the full pipeline from repo root
# Usage: .\run.ps1

$ScriptRoot = "modules\banks\nedbank_namibia\projects\account_fit_intelligence_engine\code\src"

Write-Output "=== [1/2] Generating synthetic data ==="
python "$ScriptRoot\ingest\generate_synthetic.py"
if ($LASTEXITCODE -ne 0) { Write-Error "generate_synthetic.py failed"; exit 1 }

Write-Output ""
Write-Output "=== [2/2] Running account fit engine ==="
python "$ScriptRoot\engine\account_fit.py"
if ($LASTEXITCODE -ne 0) { Write-Error "account_fit.py failed"; exit 1 }

Write-Output ""
Write-Output "=== Pipeline complete ==="
