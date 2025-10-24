# Run coverage analysis for MRTD tests
Write-Host "Running tests with coverage..." -ForegroundColor Cyan
python -m coverage run -m unittest MRTDtest

Write-Host "`nGenerating coverage report..." -ForegroundColor Cyan
python -m coverage report

Write-Host "`nGenerating detailed coverage report..." -ForegroundColor Cyan
python -m coverage report -m

Write-Host "`nGenerating HTML coverage report..." -ForegroundColor Cyan
python -m coverage html

Write-Host "`nCoverage analysis complete!" -ForegroundColor Green
Write-Host "HTML report generated at htmlcov\index.html" -ForegroundColor Yellow
Write-Host "`nTo view the HTML report, run: start htmlcov\index.html" -ForegroundColor Yellow
