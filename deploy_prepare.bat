@echo off
echo ========================================
echo   ZUTOMAYO Music Site - 快速部署
echo ========================================
echo.

echo [1/3] 检查 Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未安装 Git，请先安装: https://git-scm.com/
    pause
    exit /b 1
)
echo ✅ Git 已安装

echo.
echo [2/3] 初始化 Git 仓库...
if not exist .git (
    git init
    echo ✅ Git 仓库已初始化
) else (
    echo ℹ️  Git 仓库已存在
)

echo.
echo [3/3] 添加文件到 Git...
git add .
git status

echo.
echo ========================================
echo   准备完成！
echo ========================================
echo.
echo 下一步选择部署方式：
echo.
echo 方式 1 - Vercel（推荐，最简单）
echo   1. 访问 https://vercel.com
echo   2. 用 GitHub 登录
echo   3. Import Project
echo   4. 选择这个仓库
echo   5. 一键部署完成
echo.
echo 方式 2 - Railway
echo   1. 访问 https://railway.app  
echo   2. 用 GitHub 登录
echo   3. New Project - Deploy from GitHub
echo   4. 选择这个仓库
echo.
echo 方式 3 - 先推送到 GitHub
echo   运行: deploy_to_github.bat
echo.
pause
