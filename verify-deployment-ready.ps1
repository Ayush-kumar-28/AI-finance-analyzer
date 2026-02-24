# Finance Tracker - Deployment Readiness Check
# Run this script before deploying to verify everything is configured

Write-Host "================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT READINESS CHECK" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check 1: Git repository
Write-Host "Checking Git repository..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✗ Git repository not found. Run: git init" -ForegroundColor Red
    $allGood = $false
}

# Check 2: Required files
Write-Host "`nChecking required files..." -ForegroundColor Yellow
$requiredFiles = @(
    "frontend/package.json",
    "backend/package.json",
    "ml-service/requirements.txt",
    "ml-service/main.py",
    "backend/server.js"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $file missing" -ForegroundColor Red
        $allGood = $false
    }
}

# Check 3: ML Model files
Write-Host "`nChecking ML model files..." -ForegroundColor Yellow
$modelFiles = @(
    "app/models/svm_model.pkl",
    "app/models/vectorizer.pkl"
)

foreach ($file in $modelFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "✗ $file missing - Model needs training" -ForegroundColor Red
        $allGood = $false
    }
}

# Check 4: Environment example files
Write-Host "`nChecking environment example files..." -ForegroundColor Yellow
$envFiles = @(
    "backend/.env.example",
    "ml-service/.env.example",
    "frontend/.env.example"
)

foreach ($file in $envFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "⚠ $file missing (optional)" -ForegroundColor Yellow
    }
}

# Check 5: .gitignore
Write-Host "`nChecking .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    if ($gitignoreContent -match "\.env" -and $gitignoreContent -match "node_modules") {
        Write-Host "✓ .gitignore properly configured" -ForegroundColor Green
    } else {
        Write-Host "⚠ .gitignore may need updating" -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ .gitignore missing" -ForegroundColor Red
    $allGood = $false
}

# Check 6: No .env files committed
Write-Host "`nChecking for committed .env files..." -ForegroundColor Yellow
$envCommitted = git ls-files | Select-String "\.env$"
if ($envCommitted) {
    Write-Host "✗ .env files are committed! Remove them before deploying" -ForegroundColor Red
    $allGood = $false
} else {
    Write-Host "✓ No .env files committed" -ForegroundColor Green
}

# Check 7: Deployment config files
Write-Host "`nChecking deployment configuration..." -ForegroundColor Yellow
$deployFiles = @(
    "backend/render.yaml",
    "ml-service/render.yaml",
    "vercel.json"
)

foreach ($file in $deployFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "⚠ $file missing (optional)" -ForegroundColor Yellow
    }
}

# Check 8: Node modules not committed
Write-Host "`nChecking for node_modules..." -ForegroundColor Yellow
$nodeModulesCommitted = git ls-files | Select-String "node_modules"
if ($nodeModulesCommitted) {
    Write-Host "✗ node_modules are committed! Add to .gitignore" -ForegroundColor Red
    $allGood = $false
} else {
    Write-Host "✓ node_modules not committed" -ForegroundColor Green
}

# Summary
Write-Host "`n================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "✓ ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "`nYou're ready to deploy! Follow these steps:" -ForegroundColor Cyan
    Write-Host "1. Push to GitHub: git push origin main" -ForegroundColor White
    Write-Host "2. Follow QUICK_DEPLOY.md for deployment" -ForegroundColor White
} else {
    Write-Host "✗ SOME CHECKS FAILED" -ForegroundColor Red
    Write-Host "`nFix the issues above before deploying." -ForegroundColor Yellow
}
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
