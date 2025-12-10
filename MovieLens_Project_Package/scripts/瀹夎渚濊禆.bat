@echo off
chcp 65001 >nul
echo ========================================
echo   MovieLens 数据分析系统 - 依赖安装
echo ========================================
echo.
echo 正在安装Python依赖包...
echo.

pip install -r requirements.txt

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 请运行"启动应用.bat"来启动系统
echo.

pause

