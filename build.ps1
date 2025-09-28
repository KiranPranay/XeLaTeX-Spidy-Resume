param(
  [string]$Config = "config\pranay.json"
)

# 1) Render TEX and get build meta as JSON
$render = python .\render.py --config "$Config"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

try {
  $meta = $render | ConvertFrom-Json
} catch {
  Write-Host "Failed to parse render.py output:" -ForegroundColor Red
  Write-Host $render
  exit 1
}

$texPath   = $meta.tex_path
$outDir    = $meta.outdir
$engine    = $meta.engine
$outBase   = $meta.output_basename

# 2) Compile with latexmk; keep all files in outputs/
$opts = @("-silent","-f","-bibtex-","-interaction=nonstopmode","-halt-on-error","-outdir=$outDir","-auxdir=$outDir")

if ($engine -ieq "lualatex") {
  latexmk @opts -lualatex "$texPath"
} else {
  latexmk @opts -xelatex "$texPath"
}

if ($LASTEXITCODE -ne 0) {
  $log = Join-Path $outDir ([System.IO.Path]::GetFileNameWithoutExtension($texPath) + ".log")
  if (Test-Path $log) {
    Write-Host "`n--- Last 80 lines of build log ---`n" -ForegroundColor Cyan
    Get-Content $log -Tail 80
  }
  exit $LASTEXITCODE
}

Write-Host "`nBuild succeeded." -ForegroundColor Green
Write-Host ("PDF: " + (Join-Path $outDir ($outBase + ".pdf")))
