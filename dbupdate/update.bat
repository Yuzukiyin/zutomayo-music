@echo off
REM 快速更新脚本：批量更新 tracks 元数据
REM 使用方法：双击运行，或在 CMD 中执行 update.bat

echo ============================================
echo   曲目元数据批量更新工具
echo ============================================
echo.

REM 检查 updates.json 是否为空
findstr /C:"[" updates.json >nul 2>&1
if errorlevel 1 (
    echo [错误] updates.json 为空或格式错误！
    echo 请先编辑 updates.json，参考 updates_template.json 的格式。
    echo.
    pause
    exit /b 1
)

echo [步骤 1/3] 备份数据库...
if exist music.db (
    copy /Y music.db music.db.bak >nul
    echo ✓ 已备份到 music.db.bak
) else (
    echo [警告] music.db 不存在，请先运行 init_db.py 初始化数据库！
    pause
    exit /b 1
)
echo.

echo [步骤 2/3] 预览变更（dry-run）...
echo ----------------------------------------
python update_track_meta.py --json updates.json
echo ----------------------------------------
echo.

echo [步骤 3/3] 确认执行？
echo 按任意键执行真正的更新（写入数据库），或关闭窗口取消。
pause >nul

echo.
echo 正在更新数据库...
python update_track_meta.py --json updates.json --apply

echo.
echo ============================================
echo 完成！请检查上方输出确认更新结果。
echo ============================================
echo.
pause
