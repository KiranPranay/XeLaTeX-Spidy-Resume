python render.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$opts = @("-silent","-f","-bibtex-","-interaction=nonstopmode","-halt-on-error")

latexmk @opts -xelatex Pranay_Kiran_Resume.tex
if ($LASTEXITCODE -ne 0) {
  Write-Host "latexmk (xelatex) failed, trying lualatex..." -ForegroundColor Yellow
  latexmk @opts -lualatex Pranay_Kiran_Resume.tex
}

if ($LASTEXITCODE -ne 0) {
  if (Test-Path .\Pranay_Kiran_Resume.log) {
    Write-Host "`n--- Last 60 lines of Pranay_Kiran_Resume.log ---`n" -ForegroundColor Cyan
    Get-Content .\Pranay_Kiran_Resume.log -Tail 60
  }
  exit $LASTEXITCODE
}
