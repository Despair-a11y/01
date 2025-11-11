@echo off
chcp 65001 >nul
echo ========================================
echo   MovieLens 电影评分数据分析系统
echo ========================================
echo.
echo 正在启动应用...
echo.

streamlit run app.py

pause

