@echo off
chcp 65001 >nul
echo ========================================================
echo  Запуск дашборда: Датасет Нарушение конфиденциальности
echo ========================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ОШИБКА] Python не найден в системе или не добавлен в PATH!
    echo Установите Python 3.10+ с официального сайта https://python.org
    echo Обязательно отметьте галочку: 'Add Python to PATH'
    pause
    exit /b 1
)

echo Проверка и установка зависимостей...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Ошибка при установке библиотек. Пробуем запустить напрямую...
)

echo.
echo Запуск Streamlit...
echo Открываю браузер на http://localhost:8501
streamlit run app.py

pause
