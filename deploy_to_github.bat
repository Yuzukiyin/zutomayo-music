@echo off
echo ========================================
echo   推送到 GitHub
echo ========================================
echo.

set /p REPO_URL="请输入 GitHub 仓库地址 (如: https://github.com/用户名/仓库名.git): "

if "%REPO_URL%"=="" (
    echo ❌ 未输入仓库地址
    pause
    exit /b 1
)

echo.
echo [1/4] 添加所有文件...
git add .

echo.
echo [2/4] 提交更改...
git commit -m "Deploy ZUTOMAYO music site"

echo.
echo [3/4] 添加远程仓库...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo [4/4] 推送到 GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ⚠️  推送失败，可能需要先创建 main 分支
    echo 尝试推送到 master 分支...
    git push -u origin master
)

echo.
echo ========================================
echo   ✅ 推送完成！
echo ========================================
echo.
echo 现在可以去部署平台导入仓库：
echo - Vercel: https://vercel.com
echo - Railway: https://railway.app
echo.
pause
