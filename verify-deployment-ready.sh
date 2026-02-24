#!/bin/bash
# Finance Tracker - Deployment Readiness Check
# Run this script before deploying to verify everything is configured

echo "================================"
echo "DEPLOYMENT READINESS CHECK"
echo "================================"
echo ""

all_good=true

# Check 1: Git repository
echo "Checking Git repository..."
if [ -d ".git" ]; then
    echo "✓ Git repository initialized"
else
    echo "✗ Git repository not found. Run: git init"
    all_good=false
fi

# Check 2: Required files
echo ""
echo "Checking required files..."
required_files=(
    "frontend/package.json"
    "backend/package.json"
    "ml-service/requirements.txt"
    "ml-service/main.py"
    "backend/server.js"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        all_good=false
    fi
done

# Check 3: ML Model files
echo ""
echo "Checking ML model files..."
model_files=(
    "app/models/svm_model.pkl"
    "app/models/vectorizer.pkl"
)

for file in "${model_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing - Model needs training"
        all_good=false
    fi
done

# Check 4: Environment example files
echo ""
echo "Checking environment example files..."
env_files=(
    "backend/.env.example"
    "ml-service/.env.example"
    "frontend/.env.example"
)

for file in "${env_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "⚠ $file missing (optional)"
    fi
done

# Check 5: .gitignore
echo ""
echo "Checking .gitignore..."
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore && grep -q "node_modules" .gitignore; then
        echo "✓ .gitignore properly configured"
    else
        echo "⚠ .gitignore may need updating"
    fi
else
    echo "✗ .gitignore missing"
    all_good=false
fi

# Check 6: No .env files committed
echo ""
echo "Checking for committed .env files..."
if git ls-files | grep -q "\.env$"; then
    echo "✗ .env files are committed! Remove them before deploying"
    all_good=false
else
    echo "✓ No .env files committed"
fi

# Check 7: Deployment config files
echo ""
echo "Checking deployment configuration..."
deploy_files=(
    "backend/render.yaml"
    "ml-service/render.yaml"
    "vercel.json"
)

for file in "${deploy_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "⚠ $file missing (optional)"
    fi
done

# Check 8: Node modules not committed
echo ""
echo "Checking for node_modules..."
if git ls-files | grep -q "node_modules"; then
    echo "✗ node_modules are committed! Add to .gitignore"
    all_good=false
else
    echo "✓ node_modules not committed"
fi

# Summary
echo ""
echo "================================"
if [ "$all_good" = true ]; then
    echo "✓ ALL CHECKS PASSED!"
    echo ""
    echo "You're ready to deploy! Follow these steps:"
    echo "1. Push to GitHub: git push origin main"
    echo "2. Follow QUICK_DEPLOY.md for deployment"
else
    echo "✗ SOME CHECKS FAILED"
    echo ""
    echo "Fix the issues above before deploying."
fi
echo "================================"
echo ""
