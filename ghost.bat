@echo off
:: === Таймер 60 секунд для теста ===
timeout /t 60 /nobreak >nul
:: ===================================

title !!! CTOVCKP !!!
color 0a
mode con cols=80 lines=25
echo.
echo       .-"-.
echo      /|6 6|\
echo     {/(_0_)\}
echo      _/ ^ \_
echo     (/ /^\ \)-'
echo      ""' '""
echo.
echo ============================================
echo   Внимание! Запущен протокол взлома CtOS!
echo ============================================
echo.
echo   Загрузка базы данных уязвимостей... 100%
echo   Обход межсетевого огня... 100%
echo   Сканирование открытых портов... 100%
echo   Доступ получен!
echo.
echo   Для остановки введите пароль.
echo.
:check
set /p pass="Пароль: "
if "%pass%"=="1601" goto unlock
echo Неверный пароль!
goto check
:unlock
cls
echo Отключение... До свидания.
timeout /t 2 >nul
exit
