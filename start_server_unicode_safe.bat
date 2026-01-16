@echo off
echo ===================================================
echo  UNICODE-SAFE DJANGO SERVER STARTUP
echo ===================================================

REM Set console to UTF-8
chcp 65001 >nul 2>&1

REM Set environment variables for Unicode handling
set PYTHONIOENCODING=utf-8
set LANG=en_US.UTF-8
set LC_ALL=en_US.UTF-8

echo ✅ Console encoding set to UTF-8
echo ✅ Environment variables configured
echo.

echo Starting Django development server...
python manage.py runserver

pause